import json
from datetime import datetime

import feedparser
from database.db_setup import Feed, Post, get_engine, get_session
from sqlalchemy import insert, select, update

# this is going to be run via cron. make it a class
# get feed urls from db


class FeedReader:
    def __init__(self) -> None:
        self.new_posts = []
        self.session = self._get_db_session()

    def _get_db_session(self):
        engine = get_engine()
        session = get_session(engine)
        return session

    def _get_feed_urls(self):
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

    def parse_feeds(self):
        updates = []
        inserts = []

        feeds = self._get_feed_urls()

        for feed in feeds:
            if feed["etag"]:
                feed_data = feedparser.parse(feed["feed_url"], etag=feed["etag"])
                updates.append(
                    {
                        "id": feed["feed_id"],
                        "etag": feed_data.etag,
                    }
                )
            elif feed["modified"]:
                feed_data = feedparser.parse(
                    feed["feed_url"], modified=feed["modified"]
                )
                modified_date = datetime(*feed_data.last_modified_parsed[:6])
                updates.append(
                    {
                        "id": feed["feed_id"],
                        "last_modified": modified_date,
                    }
                )
            else:
                print("we should be here")
                feed_data = feedparser.parse(feed["feed_url"])
                if feed_data.etag:
                    updates.append(
                        {
                            "id": feed["feed_id"],
                            "etag": feed_data.etag,
                        }
                    )
                elif feed_data.last_modified:
                    modified_date = datetime(*feed_data.last_modified_parsed[:6])
                    updates.append(
                        {
                            "id": feed["feed_id"],
                            "last_modified": modified_date,
                        }
                    )

            # nothing new, onto next feed
            if feed_data.status == 304:
                continue

            for entry in feed_data.entries:
                updated_date = datetime(*entry.updated_parsed[:6])
                inserts.append(
                    {
                        "feed_id": feed["feed_id"],
                        "title": entry.title,
                        "link": entry.link,
                        "published": updated_date,
                        "content": entry.content[0].value,
                    }
                )

        with self.session as session:
            with session.begin():
                session.execute(insert(Post), inserts)
                session.execute(update(Feed), updates)
