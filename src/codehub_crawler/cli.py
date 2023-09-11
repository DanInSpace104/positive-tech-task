import asyncio

import click
import requests

from .context import context
from .entities import User


@click.group()
def crawler_cli():
    pass


@crawler_cli.command()
@click.argument('username')
def create_task(username: str):
    async def wrapper():
        task_id = await context.user_repositories_usecase.create_task(User(name=username))
        await asyncio.sleep(5)
        print(task_id)

    asyncio.run(wrapper())


@crawler_cli.command()
@click.argument('task_id')
def get_task(task_id: int):
    async def wrapper():
        result = await context.user_repositories_usecase.get_task_result(task_id)
        print(result)

    asyncio.run(wrapper())


@crawler_cli.command()
def init_database():
    async def wrapper():
        await context.crawler_storage._create_all()  # type: ignore

    asyncio.run(wrapper())


@crawler_cli.command()
@click.argument('username')
def request_create_task(username: str):
    resp = requests.post('http://localhost:5000/api/v1/codehub/task', json={'name': username})
    print(resp.json())


@crawler_cli.command()
@click.argument('id')
def request_get_task(id: int):
    resp = requests.get('http://localhost:5000/api/v1/codehub/task', {'task_id': id})
    print(resp.json())
