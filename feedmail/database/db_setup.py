import os

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///feeds.db")


class Feed(Base):
    __tablename__ = "feeds"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    url = Column(String(200), unique=True)
    last_modified = Column(DateTime, nullable=True)
    etag = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    posts = relationship("Post", back_populates="feed")

    def __repr__(self):
        return f"Feed:\n id: {self.id}, url: {self.url}, updated_at: {self.updated_at}, active: {self.active}, name: {self.name}"


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    feed_id = Column(Integer, ForeignKey("feeds.id"))
    title = Column(String(200))
    link = Column(String(200), unique=True)
    published = Column(DateTime)
    content = Column(String)
    feed = relationship("Feed", back_populates="posts")


def get_engine():
    return create_engine(DATABASE_URL)


def get_session(engine):
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return Session()


def init_db(engine):
    Base.metadata.create_all(bind=engine)
