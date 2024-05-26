import typer
from db import init_db

app = typer.Typer()


@app.command()
def add(feed: str, name: str):
    """
    Add a feed to the database
    """
    pass


@app.command()
def remove(feed_name: str):
    """
    Remove a feed from the database by name
    """
    pass


@app.command()
def list():
    """
    List all the feeds by name and url
    """
    pass


@app.command()
def config():
    """
    Set Fastmail config
    """
    pass


@app.command()
def initdb():
    """
    Initialize the database
    """
    init_db()
    typer.echo("Database initialized")


if __name__ == "__main__":
    app()
