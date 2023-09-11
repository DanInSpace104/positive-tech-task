import asyncio
from typing import Coroutine

from core.infrastructure.base_queue import BaseQueue, TaskStatus


class AsyncioQueue(BaseQueue):
    def __init__(self):
        self.tasks: dict[int, asyncio.Task] = {}

    async def add_task(self, task_id: int, coro: Coroutine):
        task = asyncio.create_task(coro, name=str(task_id))
        self.tasks[task_id] = task

    async def get_task_status(self, task_id: int) -> TaskStatus:
        task = self.tasks[task_id]
        if not task.done():
            return TaskStatus.PENDING
        if task.exception() is not None:
            return TaskStatus.FAILED
        return TaskStatus.DONE

    def remove_task(self, task_id: int):
        self.tasks.pop(task_id)
