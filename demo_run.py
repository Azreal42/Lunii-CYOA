import asyncio
import sitecustomize
from pathlib import Path
from pipelex import pretty_print
from pipelex.pipelex import Pipelex
from pipelex.pipeline.execute import execute_pipeline
from pipelex.pipe_run.pipe_run_mode import PipeRunMode
from pipelex.system.runtime import IntegrationMode
from pipelex.core.interpreter import PipelexInterpreter
from pipelex.hub import get_library_manager

Pipelex.make(integration_mode=IntegrationMode.PYTHON)
lm = get_library_manager()
bb = PipelexInterpreter.load_bundle_blueprint("src/pipelines/cyoa.plx")
lm.remove_from_blueprint(bb)
plx = Path("src/pipelines/cyoa.plx").read_text(encoding="utf-8")
inputs = {
    "brief": {
        "concept": "cyoa.StoryBrief",
        "content": {
            "native_prompt": "A curious kid finds a tiny robot in the school garden and they race to fix the robot before the science fair ends tonight.",
            "language": "en",
            "audience": "8-10",
            "genre": "adventure",
            "working_title": "Robot Rush"
        }
    },
    "settings": {
        "concept": "cyoa.Settings",
        "content": {
            "target_runtime_min": 10,
            "advisory_max_states": 50,
            "debug": False,
            "out_dir": "out/demo",
            "text_dir": "out/demo/texts",
            "assets_dir": "out/demo/assets",
            "image_width": 768,
            "image_height": 576,
            "img_guidance": 7.5,
            "audio_ext": "mp3",
            "image_ext": "png"
        }
    }
}

async def main():
    res = await execute_pipeline(plx_content=plx, inputs=inputs, pipe_run_mode=PipeRunMode.LIVE, search_domains=["cyoa"])
    pretty_print(res, title="CYOA demo output")

if __name__ == "__main__":
    asyncio.run(main())
