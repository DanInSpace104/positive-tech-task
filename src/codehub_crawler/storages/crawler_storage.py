from sqlalchemy import ForeignKey, UniqueConstraint, select
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from codehub_crawler.entities import Repository, Task, TaskStatus, User
from codehub_crawler.interfaces import CrawlerStorage


class Base(AsyncAttrs, DeclarativeBase):
    pass


class DBUser(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    repositories: Mapped[list["DBRepository"]] = relationship(
        back_populates="owner", lazy='immediate'
    )

    def to_dto(self) -> User:
        return User(name=self.name, repositories=[repo.to_dto() for repo in self.repositories])

    @classmethod
    def from_dto(cls, user: User) -> 'DBUser':
        return cls(name=user.name)


class DBRepository(Base):
    __tablename__ = "repos"
    __table_args__ = (UniqueConstraint('owner_id', 'name'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    stars: Mapped[int] = mapped_column(default=0)
    forks: Mapped[int] = mapped_column(default=0)
    owner: Mapped["DBUser"] = relationship(back_populates="repositories")
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    def to_dto(self) -> Repository:
        return Repository(name=self.name, stars=self.stars, forks=self.forks)


class DBTask(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[TaskStatus] = mapped_column(default=TaskStatus.PENDING)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[DBUser] = relationship(lazy='joined')

    def to_dto(self) -> Task:
        return Task(id=self.id, user=self.user.to_dto(), status=self.status)

    @classmethod
    def from_dto(cls, task: Task) -> 'DBTask':
        return cls(status=task.status)


class CrawlerSQLiteStorage(CrawlerStorage):
    def __init__(self, engine: AsyncEngine) -> None:
        self.engine = engine
        self.session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    async def _create_task(self, session: AsyncSession, user: User) -> DBTask:
        db_user = await self._get_or_create_user(session, user)
        task = DBTask(user=db_user)
        session.add(task)
        await session.commit()
        return task

    async def _create_user(self, session: AsyncSession, user: User) -> DBUser:
        dbuser = DBUser.from_dto(user)
        session.add(dbuser)
        await session.commit()
        return dbuser

    async def get_or_create_task(self, user: User) -> tuple[Task, bool]:
        created = False
        async with self.session() as session:
            dbuser = await self._get_or_create_user(session, user)
            stmt = select(DBTask).where(DBTask.user_id == dbuser.id)
            task = (await session.execute(stmt)).scalar_one_or_none()
            if task is None:
                created = True
                task = await self._create_task(session, user)

            return task.to_dto(), created

    async def _get_or_create_user(self, session: AsyncSession, user: User) -> DBUser:
        dbuser = (
            (await session.execute(select(DBUser).where(DBUser.name == user.name)))
            .unique()
            .scalar_one_or_none()
        )
        if dbuser is None:
            dbuser = await self._create_user(session, user)
        return dbuser

    async def _get_or_create_repository(
        self, session: AsyncSession, name: str, owner: DBUser
    ) -> tuple[DBRepository, bool]:
        created = False
        stmt = select(DBRepository).where(DBRepository.name == name, DBRepository.owner == owner)
        repo = (await session.execute(stmt)).scalar_one_or_none()
        if repo is None:
            created = True
            repo = await self._create_repository(session, name, owner)
        return repo, created

    async def _create_repository(
        self, session: AsyncSession, name: str, owner: DBUser
    ) -> DBRepository:
        repo = DBRepository(name=name, owner=owner)
        session.add(repo)
        await session.commit()
        return repo

    async def get_task(self, task_id: int) -> Task:
        async with self.session() as session:
            stmt = select(DBTask).where(DBTask.id == task_id)
            task = (await session.execute(stmt)).unique().scalar_one()
            return task.to_dto()

    async def _create_all(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def set_task_status(self, task: Task, status: TaskStatus):
        async with self.session() as session, session.begin():
            dbtask = (
                await session.execute(select(DBTask).where(DBTask.id == task.id))
            ).scalar_one()

            dbtask.status = status
            session.add(dbtask)
            await session.commit()

    async def get_pending_tasks(self) -> list[Task]:
        async with self.session() as session:
            stmt = select(DBTask).where(DBTask.status == TaskStatus.PENDING)
            tasks = (await session.execute(stmt)).scalars().all()
            return [task.to_dto() for task in tasks]

    async def update_or_create_repository(
        self, repo: Repository, owner: User
    ) -> tuple[Repository, bool]:
        async with self.session() as session:
            dbowner = await self._get_user(session, owner)
            dbrepo, created = await self._get_or_create_repository(session, repo.name, dbowner)
            dbrepo.stars = repo.stars
            dbrepo.forks = repo.forks
            session.add(dbrepo)
            await session.commit()

            return dbrepo.to_dto(), created

    async def _get_user(self, session: AsyncSession, user: User) -> DBUser:
        dbuser = await session.execute(select(DBUser).where(DBUser.name == user.name))
        return dbuser.scalar_one()
