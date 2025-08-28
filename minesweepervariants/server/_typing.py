from typing import Literal, Never, NotRequired, TypedDict, Optional, List, Tuple, Dict, Union

from flask.config import T

__all__ = ["CellType", "CellState", "Board", "CountInfo", "ComponentTemplate", "ComponentConfig", "CellConfig",
           "BoardMetadata", "U_Hint", "ClickResponse"]


class CellType(TypedDict):
    boardname: str
    x: int
    y: int


class CellState(TypedDict):
    type: CellType
    isRevealed: bool
    isLoading: bool
    hint1: bool
    hint2: bool
    error: bool
    errormine: bool


class Board(TypedDict):
    name: Optional[str]
    position: Tuple[int, int]
    showLabel: Optional[bool]
    showName: Optional[bool]
    dye: Optional[List[List[bool]]]
    mask: Optional[List[List[bool]]]
    size: Tuple[int, int]


class CountInfo(TypedDict):
    total: int
    known: Optional[int]
    unknown: int
    remains: Optional[int]


class ComponentTemplate(TypedDict):
    name: str
    value: object


class ComponentConfig(TypedDict):
    type: Literal["container", "text", "assets", "template"]
    value: Union[List['ComponentConfig'], str, ComponentTemplate]
    style: Optional[str]
    class_: Optional[str]


class CellConfig(TypedDict):
    overlayText: str
    position: CellType
    component: ComponentConfig
    highlight: Optional[Dict[str, List[CellType]]]


class BoardMetadata(TypedDict):
    rules: List[str]
    boards: Dict[str, Board]
    cells: List[CellConfig]
    count: Optional[CountInfo]
    seed: Optional[str]
    noFail: Optional[bool]
    noHint: Optional[bool]
    mode: Literal["NORMAL", "EXPERT", "ULTIMATE", "PUZZLE", "UNKNOWN"]
    u_mode: NotRequired[List[str]]
    u_hint: NotRequired[Dict[str, int]]
    version: tuple[int, int, int]


class U_Hint(TypedDict):
    emptycount: int
    flagcount: int
    markcount: NotRequired[int]


class ClickResponse(TypedDict):
    success: bool
    gameover: bool
    reason: str
    cells: List[CellConfig]
    count: Optional[CountInfo]
    noFail: Optional[bool]
    noHint: Optional[bool]
    mines: NotRequired[List[CellType]]
    win: NotRequired[bool]
    u_hint: NotRequired[U_Hint]


class GenerateBoardResult(TypedDict):
    reason: str
    success: bool


class CreateGameParams(TypedDict):
    size: str
    rules: str
    mode: str
    total: str
    u_mode: NotRequired[str]
    dye: NotRequired[str]
    mask: NotRequired[str]
    seed: NotRequired[str]


class ClickData(TypedDict):
    x: int
    y: int
    boardName: str
    button: Literal["left", "right", "middle"]


type MetadataResult = BoardMetadata

type ResponseType[T] = T | tuple[T, int]
