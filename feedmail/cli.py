import typer

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


if __name__ == "__main__":
    app()
