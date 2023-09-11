import os


class Config:
    BASE_URL: str = 'http://localhost:8000'
    REPO_LIST_URL: str = '/users/{username}/repos'
    REPO_DETAIL_URL: str = '/repos/{username}/{repo_name}'

    SQLITE_DB_FILE: str = "database.sqlite"

    GH_BASE_URL: str = 'https://api.github.com'
    GH_REPO_LIST_URL: str = '/users/{username}/repos'
    GH_REPO_DETAIL_URL: str = '/repos/{username}/{repo_name}'
    GH_API_TOKEN: str = os.environ.get('GH_API_TOKEN') or ''


settings = Config()
