from dataclasses import dataclass
from typing import Optional, Self, Union


@dataclass
class Ok[T]:
    value: T


@dataclass
class Err[E]:
    err: E


type Result[T, E] = Union[Ok[T], Err[E]]


@dataclass
class IntrusiveListRef[L, T]:
    inner_ref: T

    _phantom_data: Optional[L] = None

    next: Optional[Self] = None
    prev: Optional[Self] = None


@dataclass
class IntrusiveList[L, T]:
    head: Optional[IntrusiveListRef[L, T]]
    tail: Optional[IntrusiveListRef[L, T]]
    size: int

    def push_front(self, ref: IntrusiveListRef[L, T]):
        ref.next = self.head

        if self.head is not None:
            self.head.prev = ref
        else:
            self.tail = ref

        self.head = ref
        self.size += 1

    def push_back(self, ref: IntrusiveListRef[L, T]):
        ref.prev = self.tail

        if self.tail is not None:
            self.tail.next = ref
        else:
            self.head = ref

        self.tail = ref
        self.size += 1

    def remove_head(self):
        match self.head:
            case None:
                self.tail = None
            case x:
                self.head = x.next

        match self.head:
            case None:
                self.tail = None
            case x:
                self.head.prev = None

        if self.size > 0:
            self.size -= 1

    def remove_tail(self):
        match self.tail:
            case None:
                self.head = None
            case x:
                self.tail = x.prev

        match self.tail:
            case None:
                self.head = None
            case x:
                self.tail.next = None

        if self.size > 0:
            self.size -= 1

    def remove(self, ref: IntrusiveListRef[L, T]):
        match ref:
            case self.head:
                self.remove_head()
            case self.tail:
                self.remove_tail()

            case _:
                if ref.prev is not None:
                    ref.prev.next = ref.next

                if ref.next is not None:
                    ref.next.prev = ref.prev

        if self.size > 0:
            self.size -= 1
