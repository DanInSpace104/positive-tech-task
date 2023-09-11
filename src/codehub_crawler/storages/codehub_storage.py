from typing import Protocol

import aiohttp

from codehub_crawler.entities import Repository, User
from codehub_crawler.interfaces import CodeHubStorage


class CodeHubStorageConfiguration(Protocol):
    BASE_URL: str
    REPO_LIST_URL: str
    REPO_DETAIL_URL: str


class EmulatorCodeHubStorage(CodeHubStorage):
    def __init__(self, config: CodeHubStorageConfiguration):
        self.config = config

    async def get_user_repos(self, user: User) -> list[Repository]:
        async with aiohttp.ClientSession(self.config.BASE_URL) as session:
            async with session.get(
                self.config.REPO_LIST_URL.format(username=user.name)
            ) as response:
                response.raise_for_status()
                repos = await response.json()
                return [Repository(name=repo) for repo in repos]

    async def get_repo_data(self, owner: User, repo: Repository) -> Repository:
        async with aiohttp.ClientSession(self.config.BASE_URL) as session:
            async with session.get(
                self.config.REPO_DETAIL_URL.format(username=owner.name, repo_name=repo.name)
            ) as response:
                response.raise_for_status()
                repo_data = await response.json()
                return Repository(
                    name=repo_data["name"], stars=repo_data["stars"], forks=repo_data["forks"]
                )


class GithubStorageConfiguration(Protocol):
    GH_BASE_URL: str
    GH_REPO_LIST_URL: str
    GH_REPO_DETAIL_URL: str
    GH_API_TOKEN: str


class GithubStorage(CodeHubStorage):
    def __init__(self, config: GithubStorageConfiguration):
        self.config = config
        if self.config.GH_API_TOKEN == '':
            raise ValueError('Github API token is empty')

    async def get_user_repos(self, user: User) -> list[Repository]:
        async with self.session() as session:
            async with session.get(
                self.config.GH_REPO_LIST_URL.format(username=user.name)
            ) as response:
                response.raise_for_status()
                repos = await response.json()
                return [Repository(name=repo['name']) for repo in repos]

    async def get_repo_data(self, owner: User, repo: Repository) -> Repository:
        async with self.session() as session:
            async with session.get(
                self.config.GH_REPO_DETAIL_URL.format(username=owner.name, repo_name=repo.name)
            ) as response:
                response.raise_for_status()
                repo_data = await response.json()
                return Repository(
                    name=repo_data["name"],
                    stars=repo_data["stargazers_count"],
                    forks=repo_data["forks_count"],
                )

    def session(self):
        headers = {'Authorization': f'Bearer {self.config.GH_API_TOKEN}'}
        return aiohttp.ClientSession(self.config.GH_BASE_URL, headers=headers)
