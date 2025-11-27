domain = "cyoa"
description = "Small helper pipeline to generate chapter_details and persist planning artefacts using the main cyoa domain."
main_pipe = "test_chapter_details"

[pipe.test_chapter_details]
type = "PipeSequence"
inputs = { brief = "StoryBrief", settings = "Settings" }
output = "PlanningArtifacts"
steps = [
  { pipe = "create_chapter_details", result = "bundle" },
  { pipe = "bundle_to_chapter_details", result = "chapter_details" },
  { pipe = "bundle_to_blueprint", result = "blueprint" },
  { pipe = "bundle_to_characters", result = "characters" },
  { pipe = "bundle_to_chapters_plan", result = "chapters" },
  { pipe = "persist_chapter_details", result = "chapter_details_path" },
  { pipe = "persist_planning_artifacts_test", result = "artifacts" }
]

[pipe.persist_planning_artifacts_test]
type = "PipeFunc"
inputs = { blueprint = "Blueprint", characters = "CharacterBible", chapters = "ChaptersPlan", settings = "Settings" }
output = "PlanningArtifacts"
function_name = "cyoa_persist_planning_artifacts"

[pipe.persist_chapter_details]
type = "PipeFunc"
inputs = { chapter_details = "ChapterDetail[]", settings = "Settings" }
output = "ChapterDetailsPath"
function_name = "cyoa_persist_chapter_details"

[pipe.debug_dump]
type = "PipeLLM"
inputs = { any = "Text" }
output = "DebugManifest"
model = { model = "gpt-4o", temperature = 0.0 }
prompt = "Return a DebugManifest with one dummy path entry. Input: @any"
