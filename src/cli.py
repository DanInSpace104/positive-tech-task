import click
import uvicorn

from codehub_crawler.cli import crawler_cli
from config import settings


@click.group()
def cli():
    pass


@cli.group()
def server():
    pass


@server.command()
@click.option('--host', default=settings.SERVER_HOST)
@click.option('--port', default=settings.SERVER_PORT)
@click.option('--reload', is_flag=settings.SERVER_RELOAD)
def run(host: str, port: int, reload: bool):
    """Run the server."""
    uvicorn.run('main:app', host=host, port=port, reload=settings.SERVER_RELOAD)


if __name__ == '__main__':
    cli.add_command(crawler_cli, 'crawler')
    cli()
