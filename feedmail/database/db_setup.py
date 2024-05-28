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
    updated_at = Column(DateTime, nullable=True)
    active = Column(Boolean, default=True)
    posts = relationship("Post", back_populates="feed")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    feed_id = Column(Integer, ForeignKey("feeds.id"))
    title = Column(String(200))
    link = Column(String(200), unique=True)
    published = Column(DateTime)
    feed = relationship("Feed", back_populates="posts")


def get_engine():
    return create_engine(DATABASE_URL, echo=True)


def get_session(engine):
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return Session()


def init_db(engine):
    Base.metadata.create_all(bind=engine)
