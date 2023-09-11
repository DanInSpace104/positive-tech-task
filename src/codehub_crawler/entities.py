from enum import Enum
from typing import Optional, TypeAlias

from core.base_entity import BaseEntity


class Repository(BaseEntity):
    name: str
    stars: int = 0
    forks: int = 0
    # owner: 'User'


class User(BaseEntity):
    name: str
    repositories: list[Repository] = []


class TaskStatus(str, Enum):
    PENDING = 'pending'
    DONE = 'done'
    FAILED = 'failed'


class Task(BaseEntity):
    id: int
    user: User
    status: TaskStatus = TaskStatus.PENDING
