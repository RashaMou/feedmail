from datetime import datetime
from typing import Any

import feedparser
from database.db_setup import Feed, Post, get_engine, get_session
from sqlalchemy import insert, select, update
from sqlalchemy.exc import SQLAlchemyError

from feedmail import logger


class FeedReader:
    def __init__(self) -> None:
        self.new_posts = []
        self.updates = []
        self.inserts = []
        self.session = self._get_db_session()

    def _get_db_session(self) -> Any:
        try:
            engine = get_engine()
            session = get_session(engine)
            return session
        except SQLAlchemyError as e:
            logger.error(f"Error getting database session: {e}")
            raise

    def _get_feed_urls(self) -> list:
        try:
            with self.session as session:
                feeds = session.execute(select(Feed))
                feed_urls = [
                    {
                        "feed_id": feed.id,
                        "feed_url": feed.url,
                        "etag": feed.etag,
                        "modified": feed.last_modified,
                    }
                    for feed in feeds.scalars()
                ]

                return feed_urls
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving feed urls: {e}")
            raise

    def _fetch_feed_data(self, feed: dict):
        if feed["etag"]:
            return feedparser.parse(feed["feed_url"], etag=feed["etag"])
        elif feed["modified"]:
            return feedparser.parse(feed["feed_url"], modified=feed["modified"])
        else:
            return feedparser.parse(feed["feed_url"])

    def parse_feeds(self) -> None:
        feeds = self._get_feed_urls()

        for feed in feeds:
            try:
                feed_data = self._fetch_feed_data(feed)
                if feed_data.status == 304:
                    continue

                self._process_feed_entries(feed, feed_data)
                self._process_feed_updates(feed, feed_data)

            except Exception as e:
                logger.error(f"Error processing feed {feed["feed_url"]}: {e}")
                continue

            print(self.new_posts)

            self._update_database()

    def _process_feed_updates(self, feed, feed_data) -> None:
        if feed_data.get("etag"):
            self.updates.append(
                {
                    "id": feed["feed_id"],
                    "etag": feed_data.etag,
                }
            )
        elif feed_data.get("last_modified"):
            modified_date = datetime(*feed_data.last_modified_parsed[:6])
            self.updates.append(
                {
                    "id": feed["feed_id"],
                    "last_modified": modified_date
                }
            )

    def _process_feed_entries(self, feed, feed_data) -> None:
        for entry in feed_data.entries:
                updated_date = datetime(*entry.updated_parsed[:6])
                self.inserts.append(
                    {
                        "feed_id": feed["feed_id"],
                        "title": entry.title,
                        "link": entry.link,
                        "published": updated_date,
                        "content": entry.content[0].value,
                    }
                )


                self.new_posts.append(
                    {"subject": entry.title, "body": entry.content[0].value,
                     "author": feed_data.feed.author}
                )

    def _update_database(self) -> None:
        try:
            with self.session as session:
                with session.begin():
                    if self.inserts:
                        session.execute(insert(Post), self.inserts)
                    if self.updates:
                        session.execute(update(Feed), self.updates)
        except SQLAlchemyError as e:
            logger.error(f"Error updating database: {e}")
            raise
