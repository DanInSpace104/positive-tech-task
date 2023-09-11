from abc import ABC, abstractmethod

from .entities import Repository, Task, TaskStatus, User


class CrawlerStorage(ABC):
    @abstractmethod
    async def get_or_create_task(self, user: User) -> tuple[Task, bool]:
        ...

    @abstractmethod
    async def get_task(self, task_id: int) -> Task:
        ...

    @abstractmethod
    async def set_task_status(self, task: Task, status: TaskStatus) -> Task:
        ...

    @abstractmethod
    async def get_pending_tasks(self) -> list[Task]:
        ...

    @abstractmethod
    async def update_or_create_repository(
        self, repo: Repository, owner: User
    ) -> tuple[Repository, bool]:
        ...


class CodeHubStorage(ABC):
    @abstractmethod
    async def get_user_repos(self, user: User) -> list[Repository]:
        ...

    @abstractmethod
    async def get_repo_data(self, owner: User, repo: Repository) -> Repository:
        ...
