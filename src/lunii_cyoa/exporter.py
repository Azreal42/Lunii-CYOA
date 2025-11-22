from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Dict, List
from uuid import uuid4

from .expansion import expand_story
from .loader import load_story
from .models import StoryDocument
from .structures import ExpansionResult, PhysicalNode


class ExportError(Exception):
    """Raised when export to Studio format fails."""


class StudioExporter:
    def __init__(self, story_path: Path, output_dir: Path, copy_assets: bool = True):
        self.story_path = story_path
        self.output_dir = output_dir
        self.copy_assets = copy_assets

    def export(self) -> Path:
        doc = load_story(self.story_path)
        expansion = expand_story(doc)
        stage_map = self._build_stage_map(expansion, doc)
        action_nodes = self._build_action_nodes(expansion, stage_map)
        stage_nodes = self._build_stage_nodes(expansion, doc, stage_map, action_nodes)
        story_json = {
            "format": 1,
            "version": 1,
            "title": self._primary_title(doc),
            "description": "",
            "stageNodes": stage_nodes,
            "actionNodes": action_nodes,
        }
        self._write_story(story_json)
        if self.copy_assets:
            self._copy_assets(doc, stage_nodes)
        return self.output_dir / "story.json"

    def _primary_title(self, doc: StoryDocument) -> str:
        if doc.story.title:
            return next(iter(doc.story.title.values()))
        return doc.story.id

    def _build_stage_map(self, expansion: ExpansionResult, doc: StoryDocument) -> Dict[int, str]:
        return {node.physical_id: str(uuid4()).upper() for node in expansion.physical_nodes}

    def _build_action_nodes(self, expansion: ExpansionResult, stage_map: Dict[int, str]) -> List[dict]:
        action_nodes: List[dict] = []
        for node in expansion.physical_nodes:
            if not node.outgoing:
                continue
            action_id = str(uuid4()).upper()
            options = [stage_map[target] for target in node.outgoing]
            action_nodes.append({"id": action_id, "options": options})
            node._action_id = action_id  # type: ignore[attr-defined]
        return action_nodes

    def _build_stage_nodes(self, expansion: ExpansionResult, doc: StoryDocument, stage_map: Dict[int, str], action_nodes: List[dict]) -> List[dict]:
        logical_lookup = {n.id: n for n in doc.nodes}
        stage_nodes: List[dict] = []
        for phys in expansion.physical_nodes:
            logical = logical_lookup[phys.logical_id]
            stage_uuid = stage_map[phys.physical_id]
            stage = {
                "uuid": stage_uuid,
                "image": logical.bg,
                "audio": logical.audio,
            }
            if phys.outgoing:
                action_id = getattr(phys, "_action_id")  # type: ignore[attr-defined]
                if logical.kind == "random":
                    option_index = -1
                elif logical.kind in ("menu", "branch"):
                    option_index = -1
                else:
                    option_index = 0
                stage["okTransition"] = {"actionNode": action_id, "optionIndex": option_index}
                stage["homeTransition"] = {"actionNode": action_id, "optionIndex": option_index}
            stage_nodes.append(stage)
        return stage_nodes

    def _write_story(self, story_json: dict) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        target = self.output_dir / "story.json"
        target.write_text(json.dumps(story_json, indent=2), encoding="utf-8")

    def _copy_assets(self, doc: StoryDocument, stage_nodes: List[dict]) -> None:
        base_dir = (self.story_path.parent / doc.assets.base_dir).resolve()
        assets_out = self.output_dir / "assets"
        for stage in stage_nodes:
            for key in ("image", "audio"):
                rel = stage.get(key)
                if not rel:
                    continue
                src = base_dir / rel
                dest = assets_out / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                if src.exists():
                    shutil.copy2(src, dest)
