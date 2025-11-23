"""Minimal stub implementations for PipeFunc steps used in the CYOA pipeline.

These functions keep validation happy by existing in the func_registry. They
return lightweight TextContent placeholders instead of performing real work.
"""

from datetime import datetime, timezone
from pathlib import Path

from kajson.kajson_manager import KajsonManager
from pipelex.core.memory.working_memory import WorkingMemory
from pipelex.core.memory.working_memory_factory import WorkingMemoryFactory
from pipelex.core.pipes.input_requirements import TypedNamedInputRequirement
from pipelex.core.stuffs.structured_content import StructuredContent
from pipelex.core.stuffs.stuff_content import StuffContent
from pipelex.core.stuffs.stuff_content import StuffContentType
from pipelex.core.stuffs.list_content import ListContent
from pipelex.core.stuffs.text_content import TextContent
from pipelex.core.stuffs.stuff import Stuff
from pipelex.core.stuffs.stuff_factory import StuffFactory
from pipelex.hub import get_required_concept
from pipelex.system.registries.func_registry import func_registry


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


class ChapterOutlineItemContent(StructuredContent):
    index: int
    title: str
    minutes: int
    blurb: str


class ChapterDetailsPath(StructuredContent):
    path: str


async def cyoa_stub_blueprint(working_memory: WorkingMemory) -> StructuredContent:
    """Return a lightweight placeholder blueprint."""
    return StructuredContent.model_validate(
        {
            "patterns": "foldback with hubs/bottlenecks; short kid-friendly loops",
            "pillars": "adventure, friendship, courage; time-bound quest; consistent POV",
            "mechanics": "hp 1..3; two boolean item slots per chapter; small randomness; fail-forward",
            "continuity_rules": "hp persists; items reset per chapter; recap at chapter start",
        }
    )


async def cyoa_stub_character_bible(working_memory: WorkingMemory) -> StructuredContent:
    """Return a placeholder cast aligned with generic adventure."""
    return StructuredContent.model_validate(
        {
            "protagonist": "Curious kid on a quest with a helpful companion.",
            "allies": "A loyal guide and a handful of friendly locals met en route.",
            "foes": "Obstacles and a shadowy opposing force creating tension.",
            "neutrals": "Colorful bystanders who add texture but stay impartial.",
            "voices": "Warm, clear narration with playful tempo; gentle urgency.",
        }
    )


async def cyoa_stub_chapters_plan(working_memory: WorkingMemory) -> StructuredContent:
    """Return a short, generic chapters plan."""
    return StructuredContent.model_validate(
        {
            "chapter_count": 6,
            "chapter_titles": ["Arrival", "Meeting the Guide", "Forest Whispers", "Trials", "The Deadline", "Homecoming"],
            "minutes_per_chapter": [2, 2, 2, 2, 2, 2],
            "chapter_blurbs": [
                "Hero enters the strange world and sets the goal.",
                "A guide appears and offers help.",
                "Mysteries deepen; clues surface.",
                "Tests of courage and skill shape the journey.",
                "Clock is ticking; stakes rise.",
                "Goal reached; lesson learned; epilogue hint.",
            ],
        }
    )


async def cyoa_persist_planning_artifacts(working_memory: WorkingMemory) -> StructuredContent:
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


async def cyoa_seed_planning_inputs(working_memory: WorkingMemory) -> StructuredContent:
    """Ensure dry-run has StoryBrief and Settings stuffs populated."""

    def _seed_if_missing(name: str, concept_string: str) -> None:
        if working_memory.get_optional_stuff(name):
            return
        concept = get_required_concept(concept_string=concept_string)
        structure_class: type[StuffContent] = KajsonManager.get_class_registry().get_required_subclass(
            name=concept.structure_class_name,
            base_class=StuffContent,
        )
        if concept.code == "Settings":
            content = structure_class(  # type: ignore[call-arg]
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
            content = structure_class(  # type: ignore[call-arg]
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
        working_memory.add_new_stuff(name=name, stuff=stuff)

    # Try seeding for the current domain first, then fallback to main CYOA domain.
    for domain_code in ("cyoa_plan", "cyoa"):
        try:
            _seed_if_missing("brief", f"{domain_code}.StoryBrief")
            _seed_if_missing("settings", f"{domain_code}.Settings")
            break
        except Exception:
            continue

    return StructuredContent.model_validate({"status": "seeded"})


async def cyoa_make_chapter_outline_items(working_memory: WorkingMemory) -> ListContent[ChapterOutlineItemContent]:
    """Split ChaptersPlan into a list of per-chapter outline items for batching."""
    chapters_stuff = working_memory.get_optional_stuff("chapters")
    if not chapters_stuff:
        return ListContent(items=[])

    chapters = chapters_stuff.content
    titles = getattr(chapters, "chapter_titles", []) or []
    minutes = getattr(chapters, "minutes_per_chapter", []) or []
    blurbs = getattr(chapters, "chapter_blurbs", []) or []

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


async def cyoa_require_complete_chapter_details(working_memory: WorkingMemory) -> ListContent:
    """Fail fast if chapter_details count differs from outline count; pass-through otherwise."""
    details_stuff = working_memory.get_optional_stuff("chapter_details")
    outline_stuff = working_memory.get_optional_stuff("chapter_outline_items")
    if not details_stuff or not outline_stuff:
        raise ValueError("chapter_details or chapter_outline_items missing for count check")

    details_list = details_stuff.as_list_content()
    outline_list = outline_stuff.as_list_content()

    if len(details_list.items) != len(outline_list.items):
        msg = f"chapter_details count={len(details_list.items)} does not match outline count={len(outline_list.items)}"
        raise ValueError(msg)

    # return unchanged to keep pipeline dataflow simple
    return details_list


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
    }
)
