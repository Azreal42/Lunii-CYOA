from __future__ import annotations

import ast
import re
from typing import Any, Dict, List, Tuple

from .models import Effect, StateBool, StateDeclaration, StateEnum, StateInt, StoryDocument, StoryNode
from .structures import Edge, ExpansionResult, PhysicalNode, StateSnapshot


class GuardEvaluationError(Exception):
    """Raised when a guard expression is invalid or cannot be evaluated."""


class EffectApplicationError(Exception):
    """Raised when effects cannot be applied (unknown var, type mismatch, out of bounds)."""


class ExpansionError(Exception):
    """Raised when expansion fails (invalid references, caps exceeded, etc.)."""


class InitialStateBuilder:
    def __init__(self, doc: StoryDocument):
        self.doc = doc

    def build(self) -> StateSnapshot:
        state: StateSnapshot = {}
        for name, decl in self.doc.state.items():
            if isinstance(decl, StateInt):
                if decl.default is not None:
                    state[name] = decl.default
                else:
                    story_default = self.doc.story.get_default_value(name)
                    state[name] = story_default if story_default is not None else decl.min
            elif isinstance(decl, StateBool):
                state[name] = False
            elif isinstance(decl, StateEnum):
                state[name] = decl.default if decl.default is not None else decl.values[0]
        return state


class GuardEvaluator:
    def __init__(self, state_decl: Dict[str, StateDeclaration]):
        self.state_decl = state_decl

    def evaluate(self, expr: str, current_state: StateSnapshot) -> bool:
        normalized = expr.replace("&&", " and ").replace("||", " or ")
        normalized = re.sub(r"!(?!=)", " not ", normalized)
        normalized = re.sub(r"\btrue\b", "True", normalized, flags=re.IGNORECASE)
        normalized = re.sub(r"\bfalse\b", "False", normalized, flags=re.IGNORECASE)

        try:
            tree = ast.parse(normalized, mode="eval")
        except SyntaxError as exc:
            raise GuardEvaluationError(f"Invalid guard syntax: {expr}") from exc

        allowed_nodes = (
            ast.Expression,
            ast.BoolOp,
            ast.BinOp,
            ast.UnaryOp,
            ast.Compare,
            ast.Name,
            ast.Constant,
            ast.Load,
            ast.And,
            ast.Or,
            ast.Not,
            ast.Eq,
            ast.NotEq,
            ast.Lt,
            ast.LtE,
            ast.Gt,
            ast.GtE,
        )

        for node in ast.walk(tree):
            if not isinstance(node, allowed_nodes):
                raise GuardEvaluationError(f"Unsupported syntax in guard: {expr}")
            if isinstance(node, ast.Call):
                raise GuardEvaluationError("Function calls not allowed in guards")
            if isinstance(node, ast.Attribute):
                raise GuardEvaluationError("Attributes not allowed in guards")

        def _eval(node: ast.AST) -> Any:
            if isinstance(node, ast.Expression):
                return _eval(node.body)
            if isinstance(node, ast.BoolOp):
                values = [_eval(v) for v in node.values]
                if isinstance(node.op, ast.And):
                    return all(values)
                if isinstance(node.op, ast.Or):
                    return any(values)
            if isinstance(node, ast.UnaryOp):
                operand = _eval(node.operand)
                if isinstance(node.op, ast.Not):
                    return not operand
                raise GuardEvaluationError("Unsupported unary operator")
            if isinstance(node, ast.Compare):
                left = _eval(node.left)
                for op, comparator in zip(node.ops, node.comparators):
                    right = _eval(comparator)
                    if isinstance(op, ast.Eq):
                        ok = left == right
                    elif isinstance(op, ast.NotEq):
                        ok = left != right
                    elif isinstance(op, ast.Lt):
                        ok = left < right
                    elif isinstance(op, ast.LtE):
                        ok = left <= right
                    elif isinstance(op, ast.Gt):
                        ok = left > right
                    elif isinstance(op, ast.GtE):
                        ok = left >= right
                    else:
                        raise GuardEvaluationError("Unsupported comparison")
                    if not ok:
                        return False
                    left = right
                return True
            if isinstance(node, ast.Name):
                if node.id not in current_state:
                    raise GuardEvaluationError(f"Unknown variable in guard: {node.id}")
                return current_state[node.id]
            if isinstance(node, ast.Constant):
                return node.value
            raise GuardEvaluationError(f"Unsupported syntax in guard: {expr}")

        result = _eval(tree)
        if not isinstance(result, bool):
            raise GuardEvaluationError("Guard did not evaluate to a boolean")
        return result


class EffectApplier:
    def __init__(self, state_decl: Dict[str, StateDeclaration]):
        self.state_decl = state_decl

    def apply(self, effects: List[Effect], state: StateSnapshot) -> StateSnapshot:
        new_state = dict(state)
        for eff in effects:
            if eff.var not in self.state_decl:
                raise EffectApplicationError(f"Effect references unknown var '{eff.var}'")
            decl = self.state_decl[eff.var]
            current = new_state[eff.var]
            if isinstance(decl, StateInt):
                updated = self._apply_int_effect(eff, current)
                if not (decl.min <= updated <= decl.max):
                    raise EffectApplicationError(f"Value {updated} out of bounds for '{eff.var}'")
                new_state[eff.var] = updated
            elif isinstance(decl, StateBool):
                if eff.op != "=":
                    raise EffectApplicationError(f"Bool var '{eff.var}' only supports '='")
                if not isinstance(eff.value, bool):
                    raise EffectApplicationError(f"Bool var '{eff.var}' requires boolean value")
                new_state[eff.var] = eff.value
            elif isinstance(decl, StateEnum):
                if eff.op != "=":
                    raise EffectApplicationError(f"Enum var '{eff.var}' only supports '='")
                if eff.value not in decl.values:
                    raise EffectApplicationError(f"Enum var '{eff.var}' value '{eff.value}' not in {decl.values}")
                new_state[eff.var] = eff.value
        return new_state

    def _apply_int_effect(self, eff: Effect, current: int) -> int:
        if not isinstance(eff.value, int):
            raise EffectApplicationError(f"Int var '{eff.var}' requires integer value")
        value = eff.value
        if eff.op == "=":
            return value
        if eff.op == "+=":
            return current + value
        if eff.op == "-=":
            return current - value
        raise EffectApplicationError(f"Unsupported op '{eff.op}' for int var '{eff.var}'")


class StoryExpander:
    def __init__(self, doc: StoryDocument, max_states: int = 5000):
        self.doc = doc
        self.max_states = max_states
        self.logical_map = {n.id: n for n in doc.nodes}
        self.guard = GuardEvaluator(doc.state)
        self.effects = EffectApplier(doc.state)
        self.initial_state_builder = InitialStateBuilder(doc)

    def expand(self) -> ExpansionResult:
        if self.doc.story.start_node not in self.logical_map:
            raise ExpansionError("start_node does not exist in nodes")

        initial_state = self.initial_state_builder.build()
        start_key = self._state_key(self.doc.story.start_node, initial_state)
        queue: List[Tuple[str, StateSnapshot, int]] = [(self.doc.story.start_node, initial_state, 0)]
        assigned_ids: Dict[Tuple[str, Tuple[Tuple[str, Any], ...]], int] = {start_key: 0}
        nodes_by_id: Dict[int, PhysicalNode] = {}
        edges: List[Edge] = []
        next_id = 1

        while queue:
            node_id, state, pid = queue.pop(0)
            if pid in nodes_by_id:
                continue
            if len(nodes_by_id) >= self.max_states:
                raise ExpansionError(f"Reached max_states ({self.max_states}) during expansion")

            logical_node: StoryNode = self.logical_map[node_id]
            nodes_by_id[pid] = PhysicalNode(physical_id=pid, logical_id=node_id, kind=logical_node.kind, state=state)

            outgoing = self._collect_outgoing(logical_node, state)
            for target_id, label, next_state in outgoing:
                if target_id not in self.logical_map:
                    raise ExpansionError(f"Node '{node_id}' references unknown target '{target_id}'")
                next_key = self._state_key(target_id, next_state)
                if next_key in assigned_ids:
                    target_pid = assigned_ids[next_key]
                else:
                    target_pid = next_id
                    assigned_ids[next_key] = target_pid
                    queue.append((target_id, next_state, target_pid))
                    next_id += 1
                edges.append(Edge(source=pid, target=target_pid, label=label))
                nodes_by_id[pid].outgoing.append(target_pid)

        physical_nodes = [nodes_by_id[i] for i in sorted(nodes_by_id)]
        reachable_logical = {node.logical_id for node in physical_nodes}
        unreachable = [nid for nid in self.logical_map if nid not in reachable_logical]
        dead_ends = [node.physical_id for node in physical_nodes if not node.outgoing]

        return ExpansionResult(
            physical_nodes=physical_nodes,
            edges=edges,
            unreachable_logical=unreachable,
            dead_ends=dead_ends,
        )

    def _collect_outgoing(self, node: StoryNode, state: StateSnapshot) -> List[Tuple[str, str | None, StateSnapshot]]:
        outgoing_targets: List[Tuple[str, str | None, StateSnapshot]] = []
        if node.kind == "story":
            if node.target:
                outgoing_targets.append((node.target, None, state))
        elif node.kind in ("menu", "branch"):
            for choice in node.choices:
                try:
                    guard_ok = True if not choice.guard else self.guard.evaluate(choice.guard, state)
                except GuardEvaluationError as exc:
                    raise ExpansionError(f"Guard error in node '{node.id}', choice '{choice.id}': {exc}") from exc
                if not guard_ok:
                    continue
                try:
                    next_state = self.effects.apply(choice.effects, state)
                except EffectApplicationError as exc:
                    raise ExpansionError(f"Effect error in node '{node.id}', choice '{choice.id}': {exc}") from exc
                outgoing_targets.append((choice.target, choice.id, next_state))
        elif node.kind == "random":
            options = node.random.get("options", [])
            if not options:
                raise ExpansionError(f"Random node '{node.id}' has no options")
            for opt in options:
                outgoing_targets.append((opt.target, "random", state))
        return outgoing_targets

    def _state_key(self, node_id: str, state: StateSnapshot) -> Tuple[str, Tuple[Tuple[str, Any], ...]]:
        return node_id, tuple(sorted(state.items()))


def expand_story(doc: StoryDocument, max_states: int = 5000) -> ExpansionResult:
    expander = StoryExpander(doc, max_states=max_states)
    return expander.expand()
