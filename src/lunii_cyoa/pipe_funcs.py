"""Minimal stub implementations for PipeFunc steps used in the CYOA pipeline.

These functions keep validation happy by existing in the func_registry. They
return lightweight TextContent placeholders instead of performing real work.
"""

from datetime import datetime, timezone
from typing import Any
import json
from pathlib import Path

from kajson.kajson_manager import KajsonManager
from pipelex.core.memory.working_memory import WorkingMemory
from pipelex.core.memory.working_memory_factory import WorkingMemoryFactory
from pipelex.core.pipes.input_requirements import TypedNamedInputRequirement
from pipelex.core.stuffs.structured_content import StructuredContent
from pipelex.core.stuffs.stuff_content import StuffContent
from pipelex.core.stuffs.list_content import ListContent
from pipelex.core.stuffs.text_content import TextContent
from pipelex.core.stuffs.stuff_factory import StuffFactory
from pipelex.hub import get_required_concept
from pipelex.system.registries.func_registry import func_registry


class StoryBriefContent(StructuredContent):
    native_prompt: str
    language: str
    audience: str | None = None
    genre: str | None = None
    working_title: str | None = None


class SettingsContent(StructuredContent):
    target_runtime_min: int
    advisory_max_states: int
    debug: bool
    out_dir: str
    text_dir: str
    assets_dir: str
    image_width: int
    image_height: int
    img_guidance: float
    img_steps: int


class BlueprintContent(StructuredContent):
    patterns: dict[str, Any]
    pillars: dict[str, Any]
    mechanics: dict[str, Any]
    continuity_rules: dict[str, Any]


class CharacterBibleContent(StructuredContent):
    protagonist: list[dict]
    allies: list[dict]
    foes: list[dict]
    neutrals: list[dict]
    voices: str | None = None


class ChaptersPlanContent(StructuredContent):
    chapter_count: int
    chapter_titles: list[str]
    minutes_per_chapter: list[int]
    chapter_blurbs: list[str]


class ChapterDetailContent(StructuredContent):
    index: int
    title: str
    minutes: int
    detailed_summary: str
    beats: list[str]
    obstacles: str
    mood: str | None = None


async def _return_placeholder(working_memory: WorkingMemory, label: str) -> TextContent:
    """Generic helper returning a small placeholder string."""
    return TextContent(text=f"{label}-placeholder")


async def cyoa_accumulate_stage_nodes(working_memory: WorkingMemory) -> TextContent:
    return await _return_placeholder(working_memory, "stage-nodes")


async def cyoa_chapter_nodes_to_graph(working_memory: WorkingMemory) -> TextContent:
    return await _return_placeholder(working_memory, "graph-from-nodes")


async def cyoa_merge_graphs_across_chapters(working_memory: WorkingMemory) -> TextContent:
    return await _return_placeholder(working_memory, "graph-merged")


async def cyoa_build_image_gen_items(working_memory: WorkingMemory) -> TextContent:
    return await _return_placeholder(working_memory, "image-gen-items")


async def cyoa_build_node_work_items(working_memory: WorkingMemory) -> TextContent:
    return await _return_placeholder(working_memory, "node-work-items")


async def cyoa_collect_node_texts_to_yaml(working_memory: WorkingMemory) -> TextContent:
    return await _return_placeholder(working_memory, "node-texts")


async def cyoa_write_node_txts(working_memory: WorkingMemory) -> TextContent:
    return await _return_placeholder(working_memory, "write-node-txts")


async def cyoa_debug_dump_structured(working_memory: WorkingMemory) -> TextContent:
    return await _return_placeholder(working_memory, "debug-dump")


async def cyoa_stage_outline_stub(working_memory: WorkingMemory) -> StructuredContent:
    """Emit a minimal StageOutline with a deterministic five-step arc."""
    stages = [
        {"kind": "entry", "goal": "Meet the tiny robot and set the timer", "obstacles": ["crowded garden"], "mandatory": True, "suggested_random": False},
        {"kind": "hub", "goal": "Gather tools and clues", "obstacles": ["limited time"], "mandatory": False, "suggested_random": True},
        {"kind": "stage", "goal": "Fix the robot's voice chip", "obstacles": ["missing screw"], "mandatory": True, "suggested_random": True},
        {"kind": "bottleneck", "goal": "Test run before judges arrive", "obstacles": ["battery drain"], "mandatory": True, "suggested_random": False},
        {"kind": "exit", "goal": "Present at the science fair", "obstacles": ["nerves"], "mandatory": True, "suggested_random": False},
    ]
    # StructuredContent is the base class expected by Pipelex for structured outputs.
    return StructuredContent.model_validate({"stages": stages})


async def cyoa_image_prompts_stub(working_memory: WorkingMemory) -> StructuredContent:
    """Produce a handful of deterministic menu image prompts."""
    items = [
        {"node_id": "menu_1", "prompt": "Warm illustration of a kid and a tiny robot crouched in a sunlit school garden, tools scattered, hopeful mood.", "negative_prompt": "text overlay, watermark, gore"},
        {"node_id": "menu_2", "prompt": "Evening scene at the science fair tent, friends rushing to fix wires on the robot under string lights.", "negative_prompt": "extra limbs, blurry text"},
        {"node_id": "menu_3", "prompt": "Close-up of the robot holding a map, kid cheering nearby, colorful posters in background.", "negative_prompt": "watermark, violence"},
    ]
    return StructuredContent.model_validate({"items": items})


class PlanningArtifactsContent(StructuredContent):
    blueprint_path: str
    characters_path: str
    chapters_path: str
    run_dir: str


class PlanningBundleContent(StructuredContent):
    blueprint: BlueprintContent
    characters: CharacterBibleContent
    chapters: ChaptersPlanContent
    chapter_details: ListContent[ChapterDetailContent]


class ChapterOutlineItemContent(StructuredContent):
    index: int
    title: str
    minutes: int
    blurb: str


class ChapterDetailsPath(StructuredContent):
    path: str


async def cyoa_stub_blueprint(working_memory: WorkingMemory) -> BlueprintContent:
    """Return a lightweight placeholder blueprint."""
    return BlueprintContent(
        patterns={"structure": "foldback with hubs/bottlenecks", "pacing": "short kid-friendly loops"},
        pillars={"themes": "adventure, friendship, courage", "tone": "hopeful urgency", "POV": "kid"},
        mechanics={"hp": "1..3", "items": "two booleans per chapter", "randomness": "small fail-forward"},
        continuity_rules={"hp": "persists", "items": "reset per chapter", "recap": "start of chapter"},
    )


async def cyoa_stub_character_bible(working_memory: WorkingMemory) -> CharacterBibleContent:
    """Return a placeholder cast aligned with generic adventure."""
    return CharacterBibleContent(
        protagonist=[{"description": "Curious kid on a quest with a helpful companion."}],
        allies=[{"description": "A loyal guide and a handful of friendly locals met en route."}],
        foes=[{"description": "Obstacles and a shadowy opposing force creating tension."}],
        neutrals=[{"description": "Colorful bystanders who add texture but stay impartial."}],
        voices="Warm, clear narration with playful tempo; gentle urgency.",
    )


async def cyoa_stub_chapters_plan(working_memory: WorkingMemory) -> ChaptersPlanContent:
    """Return a short, generic chapters plan."""
    return ChaptersPlanContent(
        chapter_count=6,
        chapter_titles=["Arrival", "Meeting the Guide", "Forest Whispers", "Trials", "The Deadline", "Homecoming"],
        minutes_per_chapter=[2, 2, 2, 2, 2, 2],
        chapter_blurbs=[
            "Hero enters the strange world and sets the goal.",
            "A guide appears and offers help.",
            "Mysteries deepen; clues surface.",
            "Tests of courage and skill shape the journey.",
            "Clock is ticking; stakes rise.",
            "Goal reached; lesson learned; epilogue hint.",
        ],
    )


async def cyoa_persist_planning_artifacts(working_memory: WorkingMemory) -> PlanningArtifactsContent:
    """Write blueprint/characters/chapters JSON dumps to disk for quick inspection."""

    def _dump(content: StructuredContent, path: Path) -> str:
        path.write_text(content.model_dump_json(indent=2, ensure_ascii=False), encoding="utf-8")
        return str(path)

    out_dir: str = working_memory.get_typed_object_or_attribute("settings.out_dir", str)
    run_dir = Path(out_dir) / "planning" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir.mkdir(parents=True, exist_ok=True)

    blueprint = working_memory.get_stuff("blueprint").content
    characters = working_memory.get_stuff("characters").content
    chapters = working_memory.get_stuff("chapters").content

    blueprint_path = _dump(content=blueprint, path=run_dir / "blueprint.json")
    characters_path = _dump(content=characters, path=run_dir / "characters.json")
    chapters_path = _dump(content=chapters, path=run_dir / "chapters.json")

    return PlanningArtifactsContent(
        blueprint_path=blueprint_path,
        characters_path=characters_path,
        chapters_path=chapters_path,
        run_dir=str(run_dir),
    )


async def cyoa_seed_planning_inputs(working_memory: WorkingMemory) -> TextContent:
    """Ensure dry-run has StoryBrief and Settings stuffs populated."""

    def _needs_seed(name: str, required_attr: str) -> bool:
        stuff = working_memory.get_optional_stuff(name)
        if not stuff:
            return True
        return not hasattr(stuff.content, required_attr)

    def _seed_if_missing(name: str, concept_string: str, required_attr: str) -> None:
        if not _needs_seed(name, required_attr):
            return
        concept = get_required_concept(concept_string=concept_string)
        structure_class: type[StuffContent] | None = None
        try:
            structure_class = KajsonManager.get_class_registry().get_required_subclass(
                name=concept.structure_class_name,
                base_class=StuffContent,
            )
        except Exception:
            fallback_map: dict[str, type[StructuredContent]] = {
                "Settings": SettingsContent,
                "StoryBrief": StoryBriefContent,
            }
            structure_class = fallback_map.get(concept.code)
        if concept.code == "Settings":
            factory_class = structure_class or SettingsContent
            content = factory_class(  # type: ignore[call-arg]
                target_runtime_min=10,
                advisory_max_states=50,
                debug=True,
                out_dir="out/dry",
                text_dir="out/dry/texts",
                assets_dir="out/dry/assets",
                image_width=512,
                image_height=384,
                img_guidance=4.5,
                img_steps=20,
            )
        elif concept.code == "StoryBrief":
            factory_class = structure_class or StoryBriefContent
            content = factory_class(  # type: ignore[call-arg]
                native_prompt="Dry run prompt",
                language="en",
                audience="8-10",
                genre="adventure",
                working_title="Dry Run Story",
            )
        else:
            requirement = TypedNamedInputRequirement(
                variable_name=name,
                concept=concept,
                multiplicity=None,
                structure_class=structure_class,
            )
            content = WorkingMemoryFactory.create_mock_content(requirement)
        stuff = StuffFactory.make_stuff(concept=concept, content=content, name=name)
        existing = working_memory.get_optional_stuff(name)
        if existing:
            working_memory.replace_stuff(name=name, stuff=stuff)
        else:
            working_memory.add_new_stuff(name=name, stuff=stuff)

    errors: list[str] = []
    seeded = False
    for domain_code in ("cyoa_plan", "cyoa"):
        try:
            _seed_if_missing("brief", f"{domain_code}.StoryBrief", "native_prompt")
            _seed_if_missing("settings", f"{domain_code}.Settings", "target_runtime_min")
            seeded = True
            break
        except Exception as exc:
            errors.append(f"{domain_code}: {exc}")
            continue

    if not seeded and errors:
        raise ValueError(f"Failed to seed planning inputs: {'; '.join(errors)}")

    return TextContent(text="seeded")


async def cyoa_make_chapter_outline_items(working_memory: WorkingMemory) -> ListContent[ChapterOutlineItemContent]:
    """Split ChaptersPlan into a list of per-chapter outline items for batching."""
    chapters_stuff = working_memory.get_optional_stuff("chapters")
    if not chapters_stuff:
        return ListContent(items=[])

    chapters_content = chapters_stuff.content
    data = _to_dict(chapters_content)

    titles = data.get("chapter_titles") or getattr(chapters_content, "chapter_titles", []) or []
    minutes = data.get("minutes_per_chapter") or getattr(chapters_content, "minutes_per_chapter", []) or []
    blurbs = data.get("chapter_blurbs") or getattr(chapters_content, "chapter_blurbs", []) or []

    items: list[ChapterOutlineItemContent] = []
    for idx, title in enumerate(titles):
        minute = minutes[idx] if idx < len(minutes) else 0
        blurb = blurbs[idx] if idx < len(blurbs) else ""
        items.append(
            ChapterOutlineItemContent(
                index=idx + 1,
                title=title,
                minutes=minute,
                blurb=blurb,
            )
        )

    return ListContent(items=items)


async def cyoa_outline_to_text(working_memory: WorkingMemory) -> TextContent:
    """Serialize ChapterOutlineItem[] into JSON text for LLM consumption."""
    outline_list = working_memory.get_optional_stuff("chapter_outline_items")
    if not outline_list:
        return TextContent(text="[]")
    content = outline_list.as_list_of_fixed_content_type(item_type=ChapterOutlineItemContent)
    return TextContent(text=content.model_dump_json(indent=2, ensure_ascii=False))


async def cyoa_persist_chapter_details(working_memory: WorkingMemory) -> ChapterDetailsPath:
    """Persist ChapterDetail[] to disk under settings.out_dir/planning/{ts}/chapter_details.json."""
    chapter_details_stuff = working_memory.get_optional_stuff("chapter_details")
    if not chapter_details_stuff:
        raise ValueError("chapter_details not found in working memory")

    details_content = chapter_details_stuff.as_list_content()
    out_dir: str = working_memory.get_typed_object_or_attribute("settings.out_dir", str)
    run_dir = Path(out_dir) / "planning" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir.mkdir(parents=True, exist_ok=True)
    target = run_dir / "chapter_details.json"
    target.write_text(details_content.model_dump_json(indent=2, ensure_ascii=False), encoding="utf-8")
    return ChapterDetailsPath(path=str(target))


async def cyoa_require_complete_chapter_details(working_memory: WorkingMemory) -> ListContent[ChapterDetailContent]:
    """Fail fast if chapter_details count differs from outline count; pass-through otherwise."""
    details_stuff = working_memory.get_optional_stuff("chapter_details")
    outline_stuff = working_memory.get_optional_stuff("chapter_outline_items")
    if not details_stuff or not outline_stuff:
        raise ValueError("chapter_details or chapter_outline_items missing for count check")

    details_list = details_stuff.as_list_content()
    if len(details_list.items) == 1 and isinstance(details_list.items[0], TextContent):
        try:
            raw = details_list.items[0].text
            parsed = json.loads(raw)
            items = parsed.get("items") if isinstance(parsed, dict) else None
            if isinstance(items, list):
                details_list = ListContent(items=[ChapterDetailContent.model_validate(item) for item in items])
        except Exception:
            pass
    outline_list = outline_stuff.as_list_content()

    if len(details_list.items) != len(outline_list.items):
        msg = f"chapter_details count={len(details_list.items)} does not match outline count={len(outline_list.items)}"
        raise ValueError(msg)

    coerced_items: list[ChapterDetailContent] = []
    for item in details_list.items:
        if isinstance(item, ChapterDetailContent):
            coerced_items.append(item)
        else:
            coerced_items.append(ChapterDetailContent.model_validate(_to_dict(item)))

    return ListContent(items=coerced_items)


def _to_dict(content: StuffContent) -> dict:
    def _strip_code_fence(text: str) -> str:
        stripped = text.strip()
        if stripped.startswith("```"):
            parts = stripped.split("\n", 1)
            stripped = parts[1] if len(parts) > 1 else ""
            if stripped.endswith("```"):
                stripped = stripped.rsplit("```", 1)[0].rstrip()
        return stripped

    if isinstance(content, TextContent):
        text = getattr(content, "text")
        if isinstance(text, str):
            stripped = _strip_code_fence(text)
            try:
                return json.loads(stripped)
            except Exception:
                return {"text": text}
    if hasattr(content, "model_dump"):
        try:
            return content.model_dump()
        except Exception:
            pass
    return {"text": str(content)}


def _get_planning_bundle(working_memory: WorkingMemory) -> PlanningBundleContent:
    bundle_stuff = working_memory.get_optional_stuff("bundle") or working_memory.get_optional_stuff("planning_bundle")
    if not bundle_stuff:
        raise ValueError("PlanningBundle not found in working memory")
    content = bundle_stuff.content
    if not isinstance(content, PlanningBundleContent):
        # Defensive: allow plain dict payloads created by validators
        return PlanningBundleContent.model_validate(content)
    return content


async def cyoa_pack_planning_bundle(working_memory: WorkingMemory) -> PlanningBundleContent:
    """Pack blueprint, characters, chapters, and chapter_details into a single bundle."""
    blueprint = working_memory.get_optional_stuff("blueprint")
    characters = working_memory.get_optional_stuff("characters")
    chapters = working_memory.get_optional_stuff("chapters")
    chapter_details = working_memory.get_optional_stuff("chapter_details")
    missing = [
        name
        for name, stuff in (("blueprint", blueprint), ("characters", characters), ("chapters", chapters), ("chapter_details", chapter_details))
        if stuff is None
    ]
    if missing:
        raise ValueError(f"Cannot pack PlanningBundle; missing stuffs: {', '.join(missing)}")

    def _parse_json_if_text(content: StuffContent) -> dict | StuffContent:
        if not isinstance(content, TextContent):
            return content

        raw = content.text.strip()
        if raw.startswith("```"):
            raw = raw.lstrip("`")
            # Drop optional language tag like json or JSON after backticks
            raw = raw.split("\n", 1)[-1]
        if raw.endswith("```"):
            raw = raw[:-3].rstrip()

        try:
            return json.loads(raw)
        except Exception:
            return content

    def _to_plain_dict(content: StuffContent | dict) -> dict:
        if isinstance(content, dict):
            return content
        if isinstance(content, TextContent):
            parsed = _parse_json_if_text(content)
            if isinstance(parsed, dict):
                return parsed
        if hasattr(content, "model_dump"):
            try:
                return content.model_dump(serialize_as_any=True)  # type: ignore[call-arg]
            except Exception:
                pass
        parsed = _parse_json_if_text(content) if isinstance(content, StuffContent) else content
        return parsed if isinstance(parsed, dict) else {}

    def _coerce_char_entries(value: dict, key: str) -> None:
        entries = value.get(key, [])
        coerced: list[dict[str, Any]] = []
        for item in entries:
            if isinstance(item, dict):
                coerced.append(item)
            elif isinstance(item, str):
                coerced.append({"description": item})
        value[key] = coerced

    blueprint_payload = _to_plain_dict(blueprint.content)
    characters_payload = _to_plain_dict(characters.content)
    chapters_payload = _to_plain_dict(chapters.content)

    for character_key in ("protagonist", "allies", "foes", "neutrals"):
        _coerce_char_entries(characters_payload, character_key)

    return PlanningBundleContent(
        blueprint=BlueprintContent.model_validate(blueprint_payload),
        characters=CharacterBibleContent.model_validate(characters_payload),
        chapters=ChaptersPlanContent.model_validate(chapters_payload),
        chapter_details=chapter_details.as_list_content(),
    )


async def cyoa_bundle_to_blueprint(working_memory: WorkingMemory) -> BlueprintContent:
    bundle = _get_planning_bundle(working_memory)
    data = bundle.blueprint
    if isinstance(data, StructuredContent):
        return data
    return BlueprintContent.model_validate(data)


async def cyoa_bundle_to_characters(working_memory: WorkingMemory) -> CharacterBibleContent:
    bundle = _get_planning_bundle(working_memory)
    data = bundle.characters
    if isinstance(data, StructuredContent):
        return data
    return CharacterBibleContent.model_validate(data)


async def cyoa_bundle_to_chapters_plan(working_memory: WorkingMemory) -> ChaptersPlanContent:
    bundle = _get_planning_bundle(working_memory)
    data = bundle.chapters
    if isinstance(data, StructuredContent):
        return data
    return ChaptersPlanContent.model_validate(data)


async def cyoa_bundle_to_chapter_details(working_memory: WorkingMemory) -> ListContent[ChapterDetailContent]:
    bundle = _get_planning_bundle(working_memory)
    details = bundle.chapter_details
    if isinstance(details, ListContent):
        return details
    return ListContent[ChapterDetailContent].model_validate(details)

# Register all functions on import so the CLI `pipelex validate` sees them.
func_registry.register_functions_dict(
    {
        "cyoa_accumulate_stage_nodes": cyoa_accumulate_stage_nodes,
        "cyoa_chapter_nodes_to_graph": cyoa_chapter_nodes_to_graph,
        "cyoa_merge_graphs_across_chapters": cyoa_merge_graphs_across_chapters,
        "cyoa_build_image_gen_items": cyoa_build_image_gen_items,
        "cyoa_build_node_work_items": cyoa_build_node_work_items,
        "cyoa_collect_node_texts_to_yaml": cyoa_collect_node_texts_to_yaml,
        "cyoa_write_node_txts": cyoa_write_node_txts,
        "cyoa_debug_dump_structured": cyoa_debug_dump_structured,
        "cyoa_stage_outline_stub": cyoa_stage_outline_stub,
        "cyoa_image_prompts_stub": cyoa_image_prompts_stub,
        "cyoa_persist_planning_artifacts": cyoa_persist_planning_artifacts,
        "cyoa_seed_planning_inputs": cyoa_seed_planning_inputs,
        "cyoa_stub_blueprint": cyoa_stub_blueprint,
        "cyoa_stub_character_bible": cyoa_stub_character_bible,
        "cyoa_stub_chapters_plan": cyoa_stub_chapters_plan,
        "cyoa_make_chapter_outline_items": cyoa_make_chapter_outline_items,
        "cyoa_outline_to_text": cyoa_outline_to_text,
        "cyoa_persist_chapter_details": cyoa_persist_chapter_details,
        "cyoa_require_complete_chapter_details": cyoa_require_complete_chapter_details,
        "cyoa_pack_planning_bundle": cyoa_pack_planning_bundle,
        "cyoa_bundle_to_blueprint": cyoa_bundle_to_blueprint,
        "cyoa_bundle_to_characters": cyoa_bundle_to_characters,
        "cyoa_bundle_to_chapters_plan": cyoa_bundle_to_chapters_plan,
        "cyoa_bundle_to_chapter_details": cyoa_bundle_to_chapter_details,
    }
)
