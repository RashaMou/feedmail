import typer
from db import Feed, get_db_session, init_db
from sqlalchemy import select

app = typer.Typer()


@app.command()
def add(feed: str, name: str):
    """
    Add a feed to the database
    """
    engine = get_engine()

    with get_session(engine) as session:
        try:
            new_feed = Feed(url=feed, name=name)
            typer.echo(f"Adding feed: {feed} with name: {name}")
            session.add(new_feed)
            session.commit()
        except Exception as e:
            typer.echo(f"Error adding feed: {e}")
            session.rollback()


@app.command()
def remove(feed_name: str):
    """
    Remove a feed from the database by name
    """

    with get_db_session() as session:
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
def list():
    """
    List all the feeds by name and url
    """
    with get_db_session() as session:
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
