domain = "cyoa"
description = "Hour-long CYOA generator: chapters > stages > nodes; graph-only TOML; per-node .txt; menu image prompts via PipeImgGen; debug checkpoints. No TTS."
main_pipe = "build_cyoa_story"


# -------------------------
# Pipes — design & planning
# -------------------------

[pipe.design_blueprint]
type = "PipeLLM"
inputs = { brief = "StoryBrief", settings = "Settings" }
output = "Blueprint"
model = { model = "gpt-4o", temperature = 0.25 }
system_prompt = """
Lead interactive fiction designer. Use foldback + hubs/bottlenecks; converge every 2-3 choices; fail-forward pacing. Minimal state: hp in [1..3] plus two boolean item slots per chapter; reset items at chapter exit; small bounded randomness.
"""
prompt = """
Story capsule (must remain consistent across planning steps):
- Title: @brief.working_title
- Author prompt/logline: @brief.native_prompt
- Audience: @brief.audience
- Language: @brief.language
- Genre/Tone: @brief.genre
- Target runtime (minutes): @settings.target_runtime_min

Return JSON with keys:
- patterns: structure/pacing for THIS logline (foldback, hubs, bottlenecks)
- pillars: tone, themes, stakes, POV grounded in the author prompt
- mechanics: hp=1..3, two per-chapter boolean item slots, small randomness, fail-forward; give 1-2 item examples that fit the prompt
- continuity_rules: what persists across chapters (hp), how to recap, how to keep characters/setting consistent with the author prompt
"""

[pipe.character_bible]
type = "PipeLLM"
inputs = { brief = "StoryBrief" }
output = "CharacterBible"
model = { model = "gpt-4o", temperature = 0.6 }
prompt = """
Use the story capsule to build a coherent cast.
Return JSON: protagonist, allies, foes, neutrals, voices (each a short paragraph).
Rules:
- Keep every role aligned with the author prompt setting/goal/genre.
- Mention the main goal/setting when describing relationships.
- Voices: give tempo/diction/emotional color matching the tone implied by @brief.genre/@brief.audience.
LANG=@brief.language
"""

[pipe.chapterize]
type = "PipeLLM"
inputs = { brief = "StoryBrief", settings = "Settings" }
output = "ChaptersPlan"
model = { model = "gpt-4o", temperature = 0.3 }
prompt = """
Create 6-8 chapters for THIS story (use the author prompt). Minutes_per_chapter must sum to ~ @settings.target_runtime_min.
Return JSON with keys:
- chapter_count (int)
- chapter_titles (list; each title should reflect the setting/goal/characters from the prompt)
- minutes_per_chapter (list[int] summing to target_runtime_min)
- chapter_blurbs (list[str]; 2-3 sentences each, describing progress toward the goal in the same world/characters as the prompt)
LANG=@brief.language
"""

[pipe.chapters_to_outline_items]
type = "PipeFunc"
inputs = { chapters = "ChaptersPlan" }
output = "ChapterOutlineItem[]"
function_name = "cyoa_make_chapter_outline_items"

[pipe.chapters_outline_to_text]
type = "PipeFunc"
inputs = { chapter_outline_items = "ChapterOutlineItem[]" }
output = "Text"
function_name = "cyoa_outline_to_text"

[pipe.expand_one_chapter]
type = "PipeLLM"
inputs = { chapter = "ChapterOutlineItem", brief = "StoryBrief" }
output = "ChapterDetail"
model = { model = "gpt-4o", temperature = 0.35 }
prompt = """
You are outlining a single chapter for a CYOA.
Inputs:
- Title: @chapter.title
- Minutes: @chapter.minutes
- Blurb: @chapter.blurb
- Story brief: @brief.native_prompt (audience=@brief.audience, genre=@brief.genre, lang=@brief.language)

Return JSON:
{
  "index": @chapter.index,
  "title": @chapter.title,
  "minutes": @chapter.minutes,
  "detailed_summary": "3-5 sentences expanding the blurb with clear start/middle/end for this chapter",
  "beats": ["ordered key beats (short, imperative)", "..."],
  "obstacles": "main conflicts or decisions in this chapter",
  "mood": "tone for narration and SFX (optional)"
}
Ensure content stays in the same world/goal as the brief; no off-genre drift.
LANG=@brief.language
"""

[pipe.expand_chapters_sequential]
type = "PipeLLM"
inputs = { chapters_text = "Text", brief = "StoryBrief", characters = "CharacterBible" }
output = "ChapterDetail[]"
model = { model = "gpt-4o", temperature = 0.35 }
prompt = """
You are expanding chapter blurbs into detailed chapter plans, in ORDER, keeping continuity.
Inputs:
- chapters_text: JSON array of {index, title, minutes, blurb}
- brief: author prompt (@brief.native_prompt), language (@brief.language), audience (@brief.audience), genre (@brief.genre)
- characters: character bible summary (use to keep cast consistent)

Chapters JSON:
@chapters_text
Characters:
@characters

Return JSON exactly:
{ "items": [
  { "index": 1, "title": "...", "minutes": int,
    "detailed_summary": "3-5 sentences, beginning/middle/end, reference prior chapters when index>1",
    "beats": ["ordered short beats (imperative)"],
    "obstacles": "main conflicts/decisions",
    "mood": "tone for narration/SFX"
  },
  ...
] }
Rules:
- Process chapters sequentially; chapter n must mention continuity from chapter n-1 when relevant.
- You MUST output exactly one item per element of chapters_text; items.length == len(chapters_text array). Do not stop early.
- Keep setting/goal/characters from brief and character bible; no new off-theme casts.
- Minutes must match the provided per-chapter minutes.
LANG=@brief.language
"""

[pipe.require_complete_chapter_details]
type = "PipeFunc"
inputs = { chapter_details = "ChapterDetail[]", chapter_outline_items = "ChapterOutlineItem[]" }
output = "ChapterDetail[]"
function_name = "cyoa_require_complete_chapter_details"

[pipe.persist_chapter_details]
type = "PipeFunc"
inputs = { chapter_details = "ChapterDetail[]", settings = "Settings" }
output = "ChapterDetailsPath"
function_name = "cyoa_persist_chapter_details"

[pipe.plan_state_vars]
type = "PipeLLM"
inputs = { }
output = "StatePlan"
model = { model = "gpt-4o", temperature = 0.1 }
prompt = """
Return StatePlan:
hp_min=1, hp_max=3; item_slots=["slot1","slot2"]; reset_policy="set both false at chapter exit";
state_cardinality=(hp_max - hp_min + 1) * 2^(len(item_slots)).
"""

# -------------------------
# Chapters -> Stages (sequential)
# -------------------------

[pipe.init_prev_chapters_summary]
type = "PipeLLM"
inputs = { brief = "StoryBrief" }
output = "Text"
model = { model = "gpt-4o", temperature = 0.2 }
prompt = "Return an empty but well-formed recap header in @brief.language (no plot facts yet)."

[pipe.process_all_chapters_sequential]
type = "PipeSequence"
inputs = { blueprint = "Blueprint", characters = "CharacterBible", brief = "StoryBrief", prev_sum = "Text" }
output = "GraphSketch"
steps = [
  { pipe = "build_chapter_context", result = "ctx" },
  { pipe = "stage_outline_for_chapter", result = "stages" },
  { pipe = "process_stages_sequential", result = "nodes" },
  { pipe = "append_resets_at_exit", result = "nodes" },
  { pipe = "chapter_graph_from_nodes", result = "graph" },
  { pipe = "rollup_chapter_summary", result = "chapter_summary" },
  { pipe = "accumulate_graphs", result = "graph_accum" }
]

[pipe.build_chapter_context]
type = "PipeLLM"
inputs = { brief = "StoryBrief", prev_sum = "Text" }
output = "ChapterContext"
model = { model = "gpt-4o", temperature = 0.2 }
prompt = """
Create ChapterContext:
- index (from batch), title, minutes_target (advisory)
- prev_chapters_summary: compress @prev_sum to 5-8 lines
- item_slot_mapping: map slot1/slot2 to 0-2 concrete items for THIS chapter (e.g., {"slot1":"rope","slot2":"lantern"})
LANG=@brief.language
"""

[pipe.stage_outline_for_chapter]
type = "PipeLLM"
inputs = { ctx = "ChapterContext", blueprint = "Blueprint", brief = "StoryBrief" }
output = "StageOutline"
model = { model = "gpt-4o", temperature = 0.2 }
system_prompt = """
Chapter topology: entry -> hub -> 2-4 optional stages -> bottleneck -> exit. No cross-chapter item deps; only HP persists.
Combat stages follow the rubric below.
"""
prompt = """
Return StageOutline.stages (array of StageSpec):
- kind: entry|hub|stage|combat|bottleneck|exit
- goal, obstacles, mandatory, suggested_random
You MUST return JSON with a 'stages' array. Example:
{ "stages": [
  {"kind":"entry","goal":"meet the robot","obstacles":["crowded fair"],"mandatory":true,"suggested_random":false},
  {"kind":"hub","goal":"gather tools","obstacles":["lost parts"],"mandatory":false,"suggested_random":true}
]}
Context:
title=@ctx.title
minutes_target=@ctx.minutes_target
prev_summary=@ctx.prev_chapters_summary
blueprint=@blueprint.patterns / @blueprint.pillars / @blueprint.mechanics

Combat rubric:
- up to 2 rounds micro-loop: setup -> approach menu (attack/defend/use_item/retreat) -> random check(s) -> bounded hp/item effects -> outcome -> route to bottleneck/hub.
- Fail-forward: losing costs hp or time; never stalls; hp in [1..3]; on 0 -> shared death snippet later.
LANG=@brief.language
"""

[pipe.process_stages_sequential]
type = "PipeSequence"
inputs = { ctx = "ChapterContext", brief = "StoryBrief", characters = "CharacterBible" }
output = "StageNodes"
steps = [
  { pipe = "rollup_prev_stages_summary", result = "prev_stage_sum" },
  { pipe = "node_summaries_for_stage", result = "stage_nodes" },
  { pipe = "stage_nodes_to_structured", result = "stage_nodes_structured" },
  { pipe = "accumulate_stage_nodes", result = "nodes_accum" }
]

[pipe.rollup_prev_stages_summary]
type = "PipeLLM"
output = "Text"
model = { model = "gpt-4o", temperature = 0.2 }
prompt = "Summarize visited stages so far in 3-5 lines to inform the next stage. No new facts."

[pipe.node_summaries_for_stage]
type = "PipeLLM"
inputs = { ctx = "ChapterContext", brief = "StoryBrief", characters = "CharacterBible" }
output = "StageNodes"
model = { model = "gpt-4o", temperature = 0.45 }
system_prompt = """
Design nodes for one stage. Rules:
- 2-3 choices for menus; 'random' nodes for checks (potion/door/hit-miss).
- Guards/effects must follow the TOML spec; vars: hp, slot1, slot2 only; hp stays within [1..3].
- script text is NOT generated here; provide 'summary' only (1-3 sentences).
- Menu nodes will later get long image prompts; do NOT include prompts here.
- Use @ctx.item_slot_mapping semantics; reset at chapter exit.
- For combat: setup story node -> approach menu -> random outcomes -> outcome story node; max 2 loops.
"""
prompt = """
Return StageNodes with:
- stage_kind
- nodes: List<NodePlan> fields {id,kind,chapter_id,stage_id,bg,audio,summary,target?,choices?,random_options?,libkey?}
LANG=@brief.language
Context recap:
@ctx.prev_chapters_summary
Items mapping:
@ctx.item_slot_mapping
Cast (abridged):
@characters
"""

[pipe.stage_nodes_to_structured]
type = "PipeLLM"
output = "StageNodes"
model = { model = "gpt-4o", temperature = 0.2 }
prompt = "Normalize node ids, deduplicate choices, ensure intra-stage targets exist, and return StageNodes unchanged in structure."

[pipe.append_resets_at_exit]
type = "PipeLLM"
inputs = { ctx = "ChapterContext" }
output = "StageNodes"
model = { model = "gpt-4o", temperature = 0.1 }
prompt = """
Return a StageNodes payload containing a 'story' node (id 'chapter_{{ctx.index}}_exit') that auto-advances and applies:
[{ var='slot1', op='=', value=false }, { var='slot2', op='=', value=false }]
"""

[pipe.accumulate_stage_nodes]
type = "PipeLLM"
output = "StageNodes"
model = { model = "gpt-4o", temperature = 0.0 }
prompt = "Pass through StageNodes unchanged (identity)."

[pipe.chapter_graph_from_nodes]
type = "PipeLLM"
inputs = { nodes = "StageNodes" }
output = "GraphSketch"
model = { model = "gpt-4o", temperature = 0.0 }
prompt = """
Convert StageNodes into GraphSketch with start_node, nodes list, node_count, and choice_count.
Source:
@nodes
"""

[pipe.rollup_chapter_summary]
type = "PipeLLM"
inputs = { ctx = "ChapterContext", prev_sum = "Text" }
output = "Text"
model = { model = "gpt-4o", temperature = 0.0 }
prompt = """
Merge previous chapters summary with current chapter title/minutes to produce updated recap.
Previous:
@prev_sum
Current:
@ctx
"""

[pipe.accumulate_graphs]
type = "PipeLLM"
inputs = { graph = "GraphSketch" }
output = "GraphSketch"
model = { model = "gpt-4o", temperature = 0.0 }
prompt = "Return GraphSketch unchanged (placeholder accumulator). Input: @graph"

# -------------------------
# TOML (graph only)
# -------------------------

[pipe.emit_story_toml]
type = "PipeLLM"
inputs = { brief = "StoryBrief", graph = "GraphSketch", state = "StatePlan" }
output = "StoryToml"
model = { model = "gpt-4o", temperature = 0.2 }
system_prompt = """
Emit valid TOML 1.0 per the project spec. Include only graph + assets + state. No narrative text.
Sections: [story], [assets], [state.*], [[nodes]], [[nodes.choices]], [[nodes.random.options]].
Ids: lower snake_case; no dangling targets; unique ids. Paths are relative to assets.base_dir.
"""
prompt = """
Render story.toml (graph only):

[story]
id = stable snake_case from @brief.working_title or derived
start_node = @graph.start_node
title.@brief.language = derived title aligned with @brief.genre
version = "0.5"

[assets]
base_dir = "assets"
audio_ext = "mp3"
image_ext = "png"
audio_target = "mp3_44k1_mono_64kbps"
image_target = "bmp_320x240_4bpp"
auto_generate_menu_audio = true
auto_generate_menu_image = true

[state.hp]
type = "int"
min = @state.hp_min
max = @state.hp_max
default = @state.hp_max

{% for slot in state.item_slots %}
[state.{{slot}}]
type = "bool"
{% endfor %}

# Serialize [[nodes]] from GraphSketch.nodes; for random nodes emit [[nodes.random.options]]
"""

# -------------------------
# Image prompts -> PipeImgGen (flux)
# -------------------------

[pipe.derive_menu_image_prompts_long]
type = "PipeLLM"
inputs = { graph = "GraphSketch", brief = "StoryBrief", characters = "CharacterBible", blueprint = "Blueprint" }
output = "ImagePrompts"
model = { model = "gpt-4o", temperature = 0.2 }
system_prompt = """
Write rich prompts for menu-node images (long, multi-sentence). Include: subject, action, setting, era, mood, palette, lighting, composition (foreground/midground/background), key props (slot items), style guardrails (family-friendly; no gore; no text).
Provide optional negative_prompt to avoid: text overlays, watermarks, logos, gore, photorealistic skin pores, NSFW, extra limbs, weird hands.
"""
prompt = """
From GraphSketch.nodes filter kind=='menu' and return ImagePrompts.items as:
{ node_id, prompt, negative_prompt?, seed? }
You MUST return JSON with an 'items' array (3-6 objects). Example:
{ "items": [
  {"node_id":"menu_1","prompt":"Warm illustration of a kid and a tiny robot...", "negative_prompt":"text overlay, watermark"},
  {"node_id":"menu_2","prompt":"Evening scene at the science fair tent...", "negative_prompt":""}
]}
LANG=@brief.language
Use Character voices and Blueprint pillars to set mood.
Graph:
@graph
Characters:
@characters
Blueprint:
@blueprint
"""

[pipe.build_image_gen_items]
type = "PipeLLM"
inputs = { img_prompts = "ImagePrompts", settings = "Settings" }
output = "ImageGenItem[]"
model = { model = "gpt-4o", temperature = 0.0 }
prompt = "For each prompt in @img_prompts.items, emit ImageGenItem with node_id, prompt, negative_prompt, width=@settings.image_width, height=@settings.image_height, out_path='assets/img/' + node_id + '.png'."

[pipe.render_one_menu_image_flux]
type = "PipeLLM"
inputs = { item = "ImageGenItem" }
output = "Text"
model = { model = "gpt-4o", temperature = 0.0 }
prompt = "Return a text manifest for generated image: node_id=@item.node_id, prompt=@item.prompt"

[pipe.generate_menu_images_parallel]
type = "PipeBatch"
description = "Generate one image per menu node with flux."
inputs = { items = "ImageGenItem[]" }
output = "ImageOutputsManifest"
branch_pipe_code = "render_one_menu_image_flux"
input_list_name = "items"
input_item_name = "item"

# -------------------------
# Longform (parallel) — write .txt per node
# -------------------------

[pipe.derive_node_bullets]
type = "PipeLLM"
inputs = { graph = "GraphSketch" }
output = "NodeBullets"
model = { model = "gpt-4o", temperature = 0.25 }
prompt = """
Produce NodeBullets:
- bullets: map of node_id -> 3-5 bullets (purpose, conflict, imagery hooks, snippet cues like death/heal/unlock/rest)
- count
No prose; bullets only.
Graph:
@graph
"""

[pipe.build_node_work_items]
type = "PipeLLM"
inputs = { graph = "GraphSketch", bullets = "NodeBullets" }
output = "NodeWorkItem[]"
model = { model = "gpt-4o", temperature = 0.0 }
prompt = """
Combine GraphSketch.nodes ids/kinds with NodeBullets.bullets to produce NodeWorkItem list.
Graph:
@graph
Bullets:
@bullets
"""

[pipe.expand_single_node_longform]
type = "PipeLLM"
inputs = { item = "NodeWorkItem", characters = "CharacterBible", brief = "StoryBrief" }
output = "NodeLongText"
model = { model = "gpt-4o", temperature = 0.7 }
system_prompt = """
Write long-form narration in @brief.language for one node.
Length guidance (no budgets): story nodes = rich scene (several paragraphs, ~1-10 minutes aloud depending on chapter role); menu/random nodes = short transitional beats.
Keep POV/tone consistent with CharacterBible. Use concrete sensory detail, short paragraphs, and end on a forward-looking 'button'. Tags allowed sparingly: [pause 0.6s], <break time="400ms"/>.
"""
prompt = """
NODE {{item.node_id}} (kind={{item.kind}})
Bullets:
{{item.bullets}}

Cast notes:
@characters

Brief:
@brief

Return: { node_id, long_text }
"""

[pipe.expand_nodes_parallel]
type = "PipeBatch"
description = "One LLM call per node for longform."
inputs = { work_items = "NodeWorkItem[]", characters = "CharacterBible", brief = "StoryBrief" }
output = "NodeLongText[]"
branch_pipe_code = "expand_single_node_longform"
input_list_name = "work_items"
input_item_name = "item"

[pipe.collect_node_texts]
type = "PipeLLM"
inputs = { node_texts = "NodeLongText[]" }
output = "NodeLongformScripts"
model = { model = "gpt-4o", temperature = 0.0 }
prompt = "Aggregate NodeLongText items into NodeLongformScripts.by_id mapping. Input: @node_texts"

[pipe.write_node_txts]
type = "PipeLLM"
inputs = { scripts = "NodeLongformScripts", settings = "Settings" }
output = "Text"                                                    # manifest: [{node_id,text_path}...]
model = { model = "gpt-4o", temperature = 0.0 }
prompt = """
Summarize scripts into a manifest text placeholder for file writes.
Scripts:
@scripts
Settings:
@settings
"""

[pipe.emit_tts_scripts_csv]
type = "PipeLLM"
inputs = { scripts = "NodeLongformScripts" }
output = "TTSScriptsCSV"
model = { model = "gpt-4o", temperature = 0.1 }
system_prompt = "Return CSV 'node_id,script' preserving SSML/ElevenLabs tags (no synthesis)."
prompt = """
From NodeLongformScripts.by_id, emit node_id,script CSV.
Input:
@scripts
"""

# -------------------------
# Validation & checkpoints
# -------------------------

[pipe.validate_advisory]
type = "PipeLLM"
inputs = { graph = "GraphSketch", state = "StatePlan", settings = "Settings" }
output = "ValidationReport"
model = { model = "gpt-4o", temperature = 0.0 }
prompt = """
Compute logical_nodes=@graph.node_count; choices=@graph.choice_count;
advisory_state_cardinality=@state.state_cardinality;
advisory_expanded_upper=logical_nodes*advisory_state_cardinality.
Warn on undeclared vars in guards, out-of-range hp effects, or missing targets. Return ValidationReport.
Settings:
@settings
"""

[pipe.debug_dump]
type = "PipeLLM"
inputs = { any = "Text" }
output = "DebugManifest"
model = { model = "gpt-4o", temperature = 0.0 }
prompt = "Return a DebugManifest with one dummy path entry. Input: @any"

[pipe.package_bundle]
type = "PipeLLM"
inputs = { story_toml = "StoryToml", tts_csv = "TTSScriptsCSV", img_prompts = "ImagePrompts", img_outputs = "ImageOutputsManifest", validation = "ValidationReport", blueprint = "Blueprint", chapters = "ChaptersPlan", characters = "CharacterBible" }
output = "StoryBundle"
model = { model = "gpt-4o", temperature = 0.1 }
prompt = """
Return StoryBundle with:
- story_toml: @story_toml
- tts_scripts_csv: @tts_csv
- image_prompts: YAML dump of @img_prompts.items
- image_outputs: YAML dump of @img_outputs.items
- validation: "nodes=@validation.logical_nodes, choices=@validation.choices, state=@validation.advisory_state_cardinality, expanded<=@validation.advisory_expanded_upper"
- outline: 6-10 sentence recap combining @blueprint.patterns/@blueprint.pillars with chapter highlights
- characters: compact list of key cast
- chapters: chapter_titles and minutes_per_chapter
- debug: note that intermediates were saved per settings.debug
Inputs:
@story_toml
@tts_csv
@img_prompts
@img_outputs
@validation
@blueprint
@chapters
@characters
"""

# -------------------------
# Orchestration
# -------------------------

[pipe.build_cyoa_story]
type = "PipeSequence"
inputs = { brief = "StoryBrief", settings = "Settings" }
output = "StoryBundle"
steps = [
  { pipe = "design_blueprint", result = "blueprint" },
  { pipe = "character_bible", result = "characters" },
  { pipe = "chapterize", result = "chapters" },
  { pipe = "chapters_to_outline_items", result = "chapter_outline_items" },
  { pipe = "chapters_outline_to_text", result = "chapters_text" },
  { pipe = "expand_chapters_sequential", result = "chapter_details" },
  { pipe = "require_complete_chapter_details", result = "chapter_details" },
  { pipe = "persist_chapter_details", result = "chapter_details_path" },
  { pipe = "plan_state_vars", result = "state" },

  { pipe = "init_prev_chapters_summary", result = "prev_sum" },
  { pipe = "process_all_chapters_sequential", result = "graph" },

  { pipe = "emit_story_toml", result = "story_toml" },

  # Image prompts -> images with flux
  { pipe = "derive_menu_image_prompts_long", result = "img_prompts" },
  { pipe = "build_image_gen_items", result = "items" },
  { pipe = "generate_menu_images_parallel", result = "img_outputs" },

  # Longform: bullets -> per-node expansion -> write .txt -> CSV for later TTS
  { pipe = "derive_node_bullets", result = "bullets" },
  { pipe = "build_node_work_items", result = "work_items" },
  { pipe = "expand_nodes_parallel", result = "node_texts" },
  { pipe = "collect_node_texts", result = "scripts" },
  { pipe = "write_node_txts", result = "text_manifest" },
  { pipe = "emit_tts_scripts_csv", result = "tts_csv" },

  { pipe = "validate_advisory", result = "validation" },
  { pipe = "package_bundle", result = "bundle" }
]

[pipe.plan_chapter_details]
type = "PipeSequence"
inputs = { brief = "StoryBrief", settings = "Settings" }
output = "ChapterDetail[]"
steps = [
  { pipe = "design_blueprint", result = "blueprint" },
  { pipe = "character_bible", result = "characters" },
  { pipe = "chapterize", result = "chapters" },
  { pipe = "chapters_to_outline_items", result = "chapter_outline_items" },
  { pipe = "chapters_outline_to_text", result = "chapters_text" },
  { pipe = "expand_chapters_sequential", result = "chapter_details" }
]
