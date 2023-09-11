from sqlalchemy.ext.asyncio import create_async_engine

from common.asyncio_queue import AsyncioQueue

from .config import settings
from .interfaces import CrawlerStorage
from .storages.codehub_storage import EmulatorCodeHubStorage, GithubStorage
from .storages.crawler_storage import CrawlerSQLiteStorage
from .use_cases import UserRepositoriesUseCase


class Context:
    def __init__(self) -> None:
        self.queue = AsyncioQueue()
        self.crawler_storage: CrawlerStorage = CrawlerSQLiteStorage(
            engine=create_async_engine(f'sqlite+aiosqlite:///{settings.SQLITE_DB_FILE}')
        )
        self.codehub_storage = GithubStorage(settings)
        # self.codehub_storage = EmulatorCodeHubStorage(settings)
        self.user_repositories_usecase = UserRepositoriesUseCase(
            self.crawler_storage, self.codehub_storage, self.queue, settings
        )

    def get_user_repositories_usecase(self) -> UserRepositoriesUseCase:
        return self.user_repositories_usecase


context = Context()


async def init_app():
    await context.user_repositories_usecase.restore_queue_tasks()
