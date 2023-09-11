import asyncio
import time

import uvicorn
from fastapi import FastAPI

app = FastAPI()


REPOS = {
    'linux': {'name': 'linux', 'forks': 100, 'stars': 100},
    'windows': {'name': 'windows', 'forks': 100, 'stars': 100},
    'python': {'name': 'python', 'forks': 100, 'stars': 100},
    # 'failure': {'name': 'failure', 'forks': 100, 'stars': 100},
}


@app.get("/users/{username}/repos")
async def repo_list(username):
    await asyncio.sleep(10)
    return REPOS


@app.get('/repos/{username}/{repo}')
async def repo_detail(username, repo):
    if repo == 'failure':
        raise Exception('failure')
    await asyncio.sleep(1)
    return REPOS[repo]


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
