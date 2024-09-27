from dataclasses import dataclass
from typing import Union


@dataclass
class Ok[T]:
    value: T


@dataclass
class Err[E]:
    err: E


type Result[T, E] = Union[Ok[T], Err[E]]
