import json
import os

from lib.feedreader import FeedReader
from lib.jmap_client import JMAPClient


def load_config():
    default_config_path = os.path.expanduser("~/.config/feedmail/config.json")
    config_path = os.getenv("FEEDMAIL_CONFIG", default_config_path)

    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Configuration file not found at {config_path}")

    with open(config_path, "r") as file:
        config = json.load(file)

    return config


def main():
    feedreader = FeedReader()
    feedreader.parse_feeds()

    if feedreader.new_posts:
        config = load_config()
        jmap = JMAPClient(
            token=config["token"],
            username=config["username"],
            to=config["to"],
        )
        for post in feedreader.new_posts:
            jmap.send_email(post["subject"], post["body"], post["author"])


if __name__ == "__main__":
    main()
