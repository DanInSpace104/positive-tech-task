from typing import Annotated

from fastapi import APIRouter, Depends

from .context import context, init_app
from .entities import Task, User
from .use_cases import UserRepositoriesUseCase

router = APIRouter()
router.on_startup.append(init_app)

UserReposDeps = Annotated[UserRepositoriesUseCase, Depends(context.get_user_repositories_usecase)]


@router.get('/task', response_model=Task)
async def get_task(task_id: int, usecase: UserReposDeps) -> Task:
    task = await usecase.get_task_result(task_id)
    return task


@router.post('/task')
async def create_task(
    user: User,
    usecase: UserReposDeps,
):
    task_id = await usecase.create_task(user)
    return {'task_id': task_id}
