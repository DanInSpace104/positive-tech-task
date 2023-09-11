from abc import ABC, abstractmethod
from collections.abc import Coroutine
from enum import Enum


class TaskStatus(str, Enum):
    PENDING = 'pending'
    DONE = 'done'
    FAILED = 'failed'


class BaseQueue(ABC):
    @abstractmethod
    async def add_task(self, task_id: int, coro: Coroutine) -> None:
        ...

    @abstractmethod
    async def get_task_status(self, task_id: int) -> TaskStatus:
        ...

    @abstractmethod
    def remove_task(self, task_id: int):
        ...
