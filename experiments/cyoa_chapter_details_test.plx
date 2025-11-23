domain = "cyoa"
description = "Small helper pipeline to generate chapter_details and persist planning artefacts using the main cyoa domain."
main_pipe = "test_chapter_details"

[pipe.test_chapter_details]
type = "PipeSequence"
inputs = { brief = "StoryBrief", settings = "Settings" }
output = "PlanningArtifacts"
steps = [
  { pipe = "design_blueprint", result = "blueprint" },
  { pipe = "character_bible", result = "characters" },
  { pipe = "chapterize", result = "chapters" },
  { pipe = "chapters_to_outline_items", result = "chapter_outline_items" },
  { pipe = "chapters_outline_to_text", result = "chapters_text" },
  { pipe = "expand_chapters_sequential", result = "chapter_details" },
  { pipe = "require_complete_chapter_details", result = "chapter_details" },
  { pipe = "persist_chapter_details_test", result = "chapter_details_path" },
  { pipe = "persist_planning_artifacts_test", result = "artifacts" }
]

[pipe.persist_chapter_details_test]
type = "PipeFunc"
inputs = { chapter_details = "ChapterDetail[]", settings = "Settings" }
output = "ChapterDetailsPath"
function_name = "cyoa_persist_chapter_details"

[pipe.persist_planning_artifacts_test]
type = "PipeFunc"
inputs = { blueprint = "Blueprint", characters = "CharacterBible", chapters = "ChaptersPlan", settings = "Settings" }
output = "PlanningArtifacts"
function_name = "cyoa_persist_planning_artifacts"
