from __future__ import annotations

import shutil
from pathlib import Path
from typing import Dict, List, Tuple
from uuid import uuid4

from .expansion import expand_story
from .loader import load_story
from .models import StoryDocument
from .structures import ExpansionResult
from pkg.api.studio_builder import ActionNodeSpec, StageNodeSpec, StudioStoryBuilder
from pkg.api.stories import StudioStory


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
        action_nodes, action_lookup = self._build_action_nodes(expansion, stage_map)
        stage_nodes = self._build_stage_nodes(expansion, doc, stage_map, action_lookup)
        builder = StudioStoryBuilder(
            title=self._primary_title(doc),
            description="",
            format_version=1,
            pack_version=1,
        )
        builder.stage_nodes = stage_nodes
        builder.action_nodes = action_nodes
        story = builder.to_studio_story()
        self._write_story(story)
        if self.copy_assets:
            self._copy_assets(doc, stage_nodes)
        return self.output_dir / "story.json"

    def _primary_title(self, doc: StoryDocument) -> str:
        if doc.story.title:
            return next(iter(doc.story.title.values()))
        return doc.story.id

    def _build_stage_map(self, expansion: ExpansionResult, doc: StoryDocument) -> Dict[int, str]:
        return {node.physical_id: str(uuid4()).upper() for node in expansion.physical_nodes}

    def _build_action_nodes(self, expansion: ExpansionResult, stage_map: Dict[int, str]) -> Tuple[List[ActionNodeSpec], Dict[int, str]]:
        action_nodes: List[ActionNodeSpec] = []
        action_lookup: Dict[int, str] = {}
        for node in expansion.physical_nodes:
            if not node.outgoing:
                continue
            action_id = str(uuid4()).upper()
            options = [stage_map[target] for target in node.outgoing]
            action_nodes.append({"id": action_id, "options": options})
            action_lookup[node.physical_id] = action_id
        return action_nodes, action_lookup

    def _build_stage_nodes(self, expansion: ExpansionResult, doc: StoryDocument, stage_map: Dict[int, str], action_lookup: Dict[int, str]) -> List[StageNodeSpec]:
        logical_lookup = {n.id: n for n in doc.nodes}
        stage_nodes: List[StageNodeSpec] = []
        for phys in expansion.physical_nodes:
            logical = logical_lookup[phys.logical_id]
            stage_uuid = stage_map[phys.physical_id]
            stage: StageNodeSpec = {
                "uuid": stage_uuid,
                "image": logical.bg,
                "audio": logical.audio,
            }
            if phys.outgoing:
                action_id = action_lookup[phys.physical_id]
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

    def _write_story(self, story: StudioStory) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        target = self.output_dir / "story.json"
        target.write_text(story.to_json(), encoding="utf-8")

    def _copy_assets(self, doc: StoryDocument, stage_nodes: List[StageNodeSpec]) -> None:
        base_dir = (self.story_path.parent / doc.assets.base_dir).resolve()
        assets_out = self.output_dir / "assets"
        for stage in stage_nodes:
            for key in ("image", "audio"):
                rel_obj = stage.get(key)
                if not isinstance(rel_obj, str) or not rel_obj:
                    continue
                rel_path = Path(rel_obj)
                src = base_dir / rel_path
                dest = assets_out / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                if src.exists():
                    shutil.copy2(src, dest)
