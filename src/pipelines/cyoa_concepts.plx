domain = "cyoa"

# -------------------------
# Concepts
# -------------------------

[concept.Settings]
description = "Global knobs and IO."
[concept.Settings.structure]
target_runtime_min = { type = "integer", description = "Target total runtime in minutes (advisory only)", required = true }
advisory_max_states = { type = "integer", description = "Soft cap for expanded state combinations", required = true }
debug = { type = "boolean", description = "If false, skip debug dumps", required = false, default_value = true }
out_dir = { type = "text", description = "Base output directory for artifacts", required = false, default_value = "out" }
text_dir = { type = "text", description = "Directory for generated longform .txt files", required = false, default_value = "out/texts" }
assets_dir = { type = "text", description = "Directory for assets (audio/images)", required = false, default_value = "assets" }
image_width = { type = "integer", description = "Image generation width in pixels", required = false, default_value = 768 }
image_height = { type = "integer", description = "Image generation height in pixels", required = false, default_value = 576 }
img_guidance = { type = "number", description = "Guidance scale for image generation", required = false, default_value = 4.5 }
img_steps = { type = "integer", description = "Number of diffusion steps for images", required = false, default_value = 30 }

[concept.StoryBrief]
description = "Author brief (native language)."
[concept.StoryBrief.structure]
native_prompt = { type = "text", description = "Author prompt in the source language", required = true }
language = { type = "text", description = "Language code (e.g., en, fr)", required = true }
audience = { type = "text", description = "Intended audience", required = false }
genre = { type = "text", description = "Genre or tone", required = false }
working_title = { type = "text", description = "Working title", required = false }

[concept.Blueprint]
description = "Design doctrine and constraints."
[concept.Blueprint.structure]
patterns = { type = "dict", key_type = "text", value_type = "text", description = "Structural patterns (foldback, hubs, bottlenecks)", required = true }
pillars = { type = "dict", key_type = "text", value_type = "text", description = "Tone, POV, themes, stakes", required = true }
mechanics = { type = "dict", key_type = "text", value_type = "text", description = "HP, per-chapter items, randomness", required = true }
continuity_rules = { type = "dict", key_type = "text", value_type = "text", description = "Rules for cross-chapter continuity", required = true }

[concept.CharacterBible]
description = "Cast and voice notes (for later TTS guidance only)."
[concept.CharacterBible.structure]
protagonist = { type = "list", item_type = "dict", description = "Main character notes", required = true }
allies = { type = "list", item_type = "dict", description = "Supporting characters", required = true }
foes = { type = "list", item_type = "dict", description = "Antagonists", required = true }
neutrals = { type = "list", item_type = "dict", description = "Neutral characters", required = true }
voices = { type = "text", description = "Voice guidance", required = false }

[concept.ChaptersPlan]
description = "Chapterization and time budgets (advisory)."
[concept.ChaptersPlan.structure]
chapter_count = { type = "integer", description = "Number of chapters (5-8)", required = true }
chapter_titles = { type = "list", item_type = "text", description = "Titles per chapter", required = true }
minutes_per_chapter = { type = "list", item_type = "integer", description = "Time budget per chapter", required = true }
chapter_blurbs = { type = "list", item_type = "text", description = "Short blurbs per chapter", required = true }

[concept.ChapterOutlineItem]
description = "Per-chapter outline entry for batching."
[concept.ChapterOutlineItem.structure]
index = { type = "integer", description = "1-based chapter index", required = true }
title = { type = "text", description = "Chapter title", required = true }
minutes = { type = "integer", description = "Time budget for the chapter", required = true }
blurb = { type = "text", description = "Short blurb/synopsis", required = true }

[concept.ChapterDetail]
description = "Detailed per-chapter plan."
[concept.ChapterDetail.structure]
index = { type = "integer", description = "1-based chapter index", required = true }
title = { type = "text", description = "Chapter title", required = true }
minutes = { type = "integer", description = "Time budget", required = true }
detailed_summary = { type = "text", description = "3-5 sentence expanded summary", required = true }
beats = { type = "list", item_type = "text", description = "Key beats/scenes in order", required = true }
obstacles = { type = "text", description = "Main conflicts/obstacles", required = true }
mood = { type = "text", description = "Tone/mood for this chapter", required = false }

[concept.ChapterDetailsPath]
description = "Filesystem path for stored chapter details."
[concept.ChapterDetailsPath.structure]
path = { type = "text", description = "Path to chapter_details.json", required = true }

[concept.StatePlan]
description = "Global state with per-chapter item reuse."
[concept.StatePlan.structure]
hp_min = { type = "integer", description = "Minimum HP", required = true }
hp_max = { type = "integer", description = "Maximum HP", required = true }
item_slots = { type = "list", item_type = "text", description = "Per-chapter item slots", required = true }
reset_policy = { type = "text", description = "How items reset at chapter exit", required = true }
state_cardinality = { type = "integer", description = "Computed state space size", required = true }

[concept.ChapterContext]
description = "Inputs for one chapter."
[concept.ChapterContext.structure]
index = { type = "integer", description = "1-based chapter index", required = true }
title = { type = "text", description = "Chapter title", required = true }
minutes_target = { type = "integer", description = "Advisory minutes for the chapter", required = true }
prev_chapters_summary = { type = "text", description = "Neutral recap of previous chapters", required = true }
item_slot_mapping = { type = "dict", key_type = "text", value_type = "text", description = "Slot-to-item mapping for this chapter", required = true }

[concept.StageSpec]
description = "One stage inside a chapter."
[concept.StageSpec.structure]
kind = { type = "text", description = "entry|hub|stage|combat|bottleneck|exit", required = true }
goal = { type = "text", description = "Stage goal", required = true }
obstacles = { type = "text", description = "Obstacles or complications", required = true }
mandatory = { type = "boolean", description = "Whether the stage is mandatory", required = true }
suggested_random = { type = "boolean", description = "Whether to insert randomness", required = true }

[concept.StageOutline]
description = "Stages list for a chapter."
[concept.StageOutline.structure]
stages = { type = "list", item_type = "dict", description = "Ordered stages for the chapter", required = true }

[concept.ChoicePlan]
description = "One menu/branch choice."
[concept.ChoicePlan.structure]
id = { type = "text", description = "Choice identifier", required = true }
label_text = { type = "text", description = "Choice label for UI/debug", required = true }
target = { type = "text", description = "Target node id", required = true }
guard = { type = "text", description = "Guard expression (TOML guard)", required = false }
effects = { type = "list", item_type = "dict", description = "State effects applied on selection", required = false }

[concept.NodePlan]
description = "One logical node."
[concept.NodePlan.structure]
id = { type = "text", description = "Lower_snake_case node id", required = true }
kind = { type = "text", description = "story|menu|random", required = true }
chapter_id = { type = "text", description = "Owning chapter id", required = true }
stage_id = { type = "text", description = "Owning stage id", required = true }
bg = { type = "text", description = "Background image path", required = true }
audio = { type = "text", description = "Narration audio path", required = true }
summary = { type = "text", description = "Short guidance for longform generation", required = true }
target = { type = "text", description = "Target for auto-advance story node", required = false }
choices = { type = "list", item_type = "dict", description = "Menu/branch choices", required = false }
random_options = { type = "list", item_type = "text", description = "Random target ids", required = false }
libkey = { type = "text", description = "Reuse key for shared snippets", required = false }

[concept.StageNodes]
description = "All nodes for a stage."
[concept.StageNodes.structure]
stage_kind = { type = "text", description = "Stage kind", required = true }
nodes = { type = "list", item_type = "dict", description = "Nodes belonging to the stage", required = true }

[concept.GraphSketch]
description = "Graph prior to TOML emission (structured)."
[concept.GraphSketch.structure]
start_node = { type = "text", description = "Start node id", required = true }
nodes = { type = "list", item_type = "dict", description = "All logical nodes", required = true }
node_count = { type = "integer", description = "Total node count", required = true }
choice_count = { type = "integer", description = "Total choice count", required = true }

[concept.NodeBullets]
description = "Guidance bullets per node for longform."
[concept.NodeBullets.structure]
bullets = { type = "dict", key_type = "text", value_type = "list", description = "Map node_id -> list of bullets", required = true }
count = { type = "integer", description = "Total bullet count", required = true }

[concept.NodeWorkItem]
description = "Unit of work for longform expansion."
[concept.NodeWorkItem.structure]
node_id = { type = "text", description = "Node id", required = true }
kind = { type = "text", description = "Node kind", required = true }
bullets = { type = "list", item_type = "text", description = "Bullets to expand", required = true }
voice_hints = { type = "text", description = "Optional voice hints", required = false }

[concept.NodeLongText]
description = "One node's long narration (.txt later)."
[concept.NodeLongText.structure]
node_id = { type = "text", description = "Node id", required = true }
long_text = { type = "text", description = "Full narration text", required = true }

[concept.NodeLongformScripts]
description = "All long narrations."
[concept.NodeLongformScripts.structure]
by_id = { type = "dict", key_type = "text", value_type = "text", description = "Map node_id -> long_text", required = true }

[concept.ImagePrompt]
description = "Prompt for one menu-node image."
[concept.ImagePrompt.structure]
node_id = { type = "text", description = "Node id", required = true }
prompt = { type = "text", description = "Positive prompt", required = true }
negative_prompt = { type = "text", description = "Negative prompt", required = false }
seed = { type = "integer", description = "Optional seed", required = false }

[concept.ImagePrompts]
description = "All image prompts."
[concept.ImagePrompts.structure]
items = { type = "list", item_type = "dict", description = "List of image prompts", required = true }

[concept.ImageGenItem]
description = "Inputs to generate one image."
[concept.ImageGenItem.structure]
node_id = { type = "text", description = "Node id", required = true }
prompt = { type = "text", description = "Positive prompt", required = true }
negative_prompt = { type = "text", description = "Negative prompt", required = false }
width = { type = "integer", description = "Width in pixels", required = true }
height = { type = "integer", description = "Height in pixels", required = true }
out_path = { type = "text", description = "Output path for the image", required = true }
seed = { type = "integer", description = "Optional seed", required = false }
guidance = { type = "number", description = "Guidance scale override", required = false }
steps = { type = "integer", description = "Diffusion steps override", required = false }

[concept.ImageOutputs]
description = "Generated images manifest."
[concept.ImageOutputs.structure]
items = { type = "list", item_type = "dict", description = "List of {node_id, image_path}", required = true }

[concept.ImageOutputsManifest]
description = "Images written to disk."
[concept.ImageOutputsManifest.structure]
items = { type = "list", item_type = "dict", description = "List of {node_id, image_path}", required = true }

[concept.StoryToml]
description = "Final TOML (graph only; no text)."
refines = "Text"

[concept.TTSScriptsCSV]
description = "node_id,script (for later TTS)."
refines = "Text"

[concept.ValidationReport]
description = "Advisory checks."
[concept.ValidationReport.structure]
logical_nodes = { type = "integer", description = "Count of logical nodes", required = true }
choices = { type = "integer", description = "Count of choices", required = true }
advisory_state_cardinality = { type = "integer", description = "State space size", required = true }
advisory_expanded_upper = { type = "integer", description = "Upper bound on expanded graph size", required = true }
notes = { type = "text", description = "Notes and warnings", required = true }

[concept.DebugManifest]
description = "Saved intermediates for debugging."
[concept.DebugManifest.structure]
paths = { type = "list", item_type = "dict", description = "List of {artifact, path}", required = true }

[concept.StoryBundle]
description = "Bundle returned by the main pipe."
[concept.StoryBundle.structure]
story_toml = { type = "text", description = "Serialized story TOML", required = true }
tts_scripts_csv = { type = "text", description = "CSV of node_id,script", required = true }
image_prompts = { type = "text", description = "YAML dump of image prompts", required = true }
image_outputs = { type = "text", description = "YAML dump of image outputs", required = true }
validation = { type = "text", description = "Validation summary string", required = true }
outline = { type = "text", description = "Story outline recap", required = true }
characters = { type = "text", description = "Key character summaries", required = true }
chapters = { type = "text", description = "Chapter list summary", required = true }
debug = { type = "text", description = "Debug notes", required = true }
