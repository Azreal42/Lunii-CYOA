from __future__ import annotations

from typing import Dict, List, Literal, Union, Annotated
from pydantic import BaseModel, Field, model_validator


class StoryMetadata(BaseModel):
    id: str
    start_node: str
    title: Dict[str, str] = Field(default_factory=dict)
    version: str | None = None
    thumbnail: str | None = None
    output_uuid: str | None = None


class AssetsConfig(BaseModel):
    base_dir: str
    audio_ext: str
    image_ext: str
    audio_target: str | None = None
    image_target: str | None = None
    ffmpeg: str | None = None
    imagemagick: str | None = None
    auto_generate_menu_audio: bool | None = None
    auto_generate_menu_image: bool | None = None


class Effect(BaseModel):
    var: str
    op: Literal["=", "+=", "-="]
    value: Union[int, bool, str]


class Choice(BaseModel):
    id: str
    label_audio: str | None = None
    label_text: str | None = None
    target: str
    effects: List[Effect] = Field(default_factory=list)
    guard: str | None = None


class RandomOption(BaseModel):
    target: str


class StoryNode(BaseModel):
    id: str
    kind: Literal["story", "menu", "branch", "random"]
    bg: str
    audio: str
    target: str | None = None
    choices: List[Choice] = Field(default_factory=list)
    random: Dict[str, List[RandomOption]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_kind_payload(self) -> "StoryNode":
        if self.kind == "random":
            options = self.random.get("options", [])
            if not options:
                raise ValueError(f"Random node '{self.id}' must define at least one option")
        else:
            if self.random:
                raise ValueError(f"Node '{self.id}' of kind '{self.kind}' must not include random options")
        if self.kind in ("menu", "branch") and not self.choices:
            raise ValueError(f"Node '{self.id}' of kind '{self.kind}' must define choices")
        if self.kind in ("story", "menu", "branch") and self.random:
            raise ValueError(f"Node '{self.id}' of kind '{self.kind}' cannot have random section")
        return self


class StateInt(BaseModel):
    type: Literal["int"]
    min: int
    max: int
    default: int | None = None

    @model_validator(mode="after")
    def validate_range(self) -> "StateInt":
        if self.min > self.max:
            raise ValueError("min cannot be greater than max")
        if self.default is not None and not (self.min <= self.default <= self.max):
            raise ValueError("default must be within [min, max]")
        return self


class StateBool(BaseModel):
    type: Literal["bool"]


class StateEnum(BaseModel):
    type: Literal["enum"]
    values: List[str]
    default: str | None = None

    @model_validator(mode="after")
    def validate_values(self) -> "StateEnum":
        if not self.values:
            raise ValueError("enum state must list values")
        if self.default is not None and self.default not in self.values:
            raise ValueError("default must be one of enum values")
        return self


StateDeclaration = Annotated[Union[StateInt, StateBool, StateEnum], Field(discriminator="type")]


class StoryDocument(BaseModel):
    story: StoryMetadata
    assets: AssetsConfig
    state: Dict[str, StateDeclaration] = Field(default_factory=dict)
    nodes: List[StoryNode]

    @model_validator(mode="after")
    def check_uniqueness_and_references(self) -> "StoryDocument":
        node_ids = [n.id for n in self.nodes]
        if len(set(node_ids)) != len(node_ids):
            raise ValueError("Duplicate node ids found")
        for node in self.nodes:
            if node.kind == "random":
                targets = [opt.target for opt in node.random.get("options", [])]
            elif node.kind in ("menu", "branch"):
                targets = [choice.target for choice in node.choices]
            else:
                targets = [node.target] if node.target else []
            for target in targets:
                if target and target not in node_ids:
                    raise ValueError(f"Node '{node.id}' references unknown target '{target}'")
            if node.kind in ("menu", "branch"):
                choice_ids = [c.id for c in node.choices]
                if len(set(choice_ids)) != len(choice_ids):
                    raise ValueError(f"Node '{node.id}' has duplicate choice ids")
        if self.story.start_node not in node_ids:
            raise ValueError("start_node must reference an existing node")
        return self
