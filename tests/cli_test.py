import os

import pytest

os.environ["DATABASE_URL"] = "sqlite:///test_feeds.db"
from cli import add, list, remove
from database.db_setup import Base, Feed, get_engine, get_session, init_db


@pytest.fixture(scope="module")
def db_session():
    print(f"DATABASE_URL: {os.getenv("DATABASE_URL")}")
    engine = get_engine()
    init_db(engine)
    print("DB intialized")

    session = get_session(engine)
    yield session

    session.rollback()
    session.close()
    print("Session closed. Dropping tables...")
    Base.metadata.drop_all(engine)
    print("Tables dropped.")
    del os.environ["DATABASE_URL"]


def test_add(db_session):
    add("http://testfeed.com/rss", "Test Feed")

    feed_in_db = db_session.query(Feed).filter_by(name="Test Feed").one()
    assert feed_in_db.url == "http://testfeed.com/rss"

def test_list():
    feeds = list()
    assert feeds == [('Test Feed', 'http://testfeed.com/rss')]

def test_remove(db_session):
    remove("Test Feed")
    feed_in_db = db_session.query(Feed).filter_by(name="Test Feed").one_or_none()
    assert feed_in_db is None

