from typing import Coroutine

from core.infrastructure.base_queue import BaseQueue

from .config import Config
from .entities import Repository, Task, TaskStatus, User
from .interfaces import CodeHubStorage, CrawlerStorage, Repository

Repository.update_forward_refs()


class DoneTaskRepoCounter:
    def __init__(self, expected: int, done: int = 0) -> None:
        self.expected = expected
        self.done = done


class UserRepositoriesUseCase:
    def __init__(
        self, storage: CrawlerStorage, remote: CodeHubStorage, queue: BaseQueue, config: Config
    ):
        self.storage = storage
        self.queue = queue
        self.config = config
        self.done_repo_counters: dict[int, DoneTaskRepoCounter] = {}
        self.remote = remote

    async def create_task(self, user: User) -> int:
        task, created = await self.storage.get_or_create_task(user)
        if not created and task.status == TaskStatus.PENDING:
            return task.id

        await self.storage.set_task_status(task, TaskStatus.PENDING)
        task.status = TaskStatus.PENDING
        await self._add_to_queue(task, self._request_user_repositories(task))
        return task.id

    async def get_task_result(self, task_id: int) -> Task:
        task = await self.storage.get_task(task_id)
        return task

    async def restore_queue_tasks(self):
        tasks = await self.storage.get_pending_tasks()
        for task in tasks:
            await self._add_to_queue(task, self._request_user_repositories(task))

    async def _request_user_repositories(self, task: Task):
        try:
            repos = await self.remote.get_user_repos(task.user)
            self.done_repo_counters[task.id] = DoneTaskRepoCounter(expected=len(repos))

            for repo in repos:
                await self._add_to_queue(task, self._request_repo_details(task, repo.name))
        except Exception as e:
            await self.storage.set_task_status(task, TaskStatus.FAILED)

    async def _request_repo_details(self, task: Task, repo_name: str):
        try:
            repo = await self.remote.get_repo_data(task.user, Repository(name=repo_name))
            repo = await self.storage.update_or_create_repository(repo, owner=task.user)

            self.done_repo_counters[task.id].done += 1

            task_is_done = (
                self.done_repo_counters[task.id].expected <= self.done_repo_counters[task.id].done
                and (await self.storage.get_task(task.id)).status == TaskStatus.PENDING
            )
            if task_is_done:
                await self.storage.set_task_status(task, TaskStatus.DONE)

        except Exception as e:
            await self.storage.set_task_status(task, TaskStatus.FAILED)

    async def _add_to_queue(self, task: Task, coro: Coroutine):
        await self.queue.add_task(task.id, coro)
