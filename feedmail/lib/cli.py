import os
import sys

import typer
from sqlalchemy import select
from typing_extensions import Annotated

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from feedmail.database.db_setup import Feed, get_engine, get_session, init_db

app = typer.Typer()


@app.command()
def addfeed(
    name: Annotated[str, typer.Option(help="Feed name")],
    url: Annotated[str, typer.Option(help="Feed url")],
):
    """
    Add a feed to the database
    """
    engine = get_engine()

    with get_session(engine) as session:
        try:
            new_feed = Feed(url=url, name=name)
            typer.echo(f"Adding feed: {url} with name: {name}")
            session.add(new_feed)
            session.commit()
        except Exception as e:
            typer.echo(f"Error adding feed: {e}")
            session.rollback()


@app.command()
def removefeed(feed_name: str):
    """
    Remove a feed from the database by name
    """

    engine = get_engine()
    with get_session(engine) as session:
        feed_to_delete = (
            session.query(Feed).filter(Feed.name == feed_name).one_or_none()
        )
        try:
            session.delete(feed_to_delete)
            session.commit()
        except Exception as e:
            typer.echo(f"Error deleting feed: {e}")
            session.rollback()


@app.command()
def listfeeds():
    engine = get_engine()
    with get_session(engine) as session:
        stmt = select(Feed.name, Feed.url)
        result = session.execute(stmt)
        feeds = result.all()

        for name, url in feeds:
            typer.echo(f"Feed name: {name}\nUrl: {url}")
            return feeds


@app.command()
def config():
    """
    Set Fastmail config
    """
    # if we don't have a config file specified, say so
    pass


@app.command()
def initdb():
    """
    Initialize the database
    """
    engine = get_engine()
    init_db(engine)
    typer.echo("Database initialized")


if __name__ == "__main__":
    app()
