from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Feed(Base):
    __tablename__ = "feeds"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    url = Column(String(200), unique=True)
    last_accessed = Column(DateTime, nullable=True)
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


engine = create_engine("sqlite:///feedmail.db", echo=True)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session():
    return Session()


def init_db():
    Base.metadata.create_all(bind=engine)
