# FeedMail

This Python program fetches RSS feeds and sends emails of new posts using
Fastmail's JMAP client. It retrieves the latest news from the specified RSS
feed, formats it into an email, and sends it to the specified recipient.

## Features

- Fetches and parses RSS feeds
- Generates HTML-formatted email content from RSS feed items
- Sends emails using Fastmail's JMAP protocol

```
── feedmail
├── __init__.py
├── database
│   ├── __init__.py
│   └── db_setup.py
├── lib
│   ├── __init__.py
│   ├── cli.py
│   ├── feedreader.py
│   └── jmap_client.py
└── main.py
```

## How it works

- When a feed is added using the CLI interface, it is added to a database
- The program periodically checks the urls in the database for new feeds via a cron job
  after the last_fetched time in the DB feed table
- If new posts are found, each post is sent to the email specified in the config
  file

## How to use

- Clone this repository
- Install dependencies specified in `pyproject.toml`
- To use this program, you need a Fastmail account and the ability to generate
  an API token
- Store the token in a config file (see `example_config.json`)
- Run the `initdb` command in the CLI, and then add some feeds
- Set up a cronjob to run `main.py` periodically, or just run it manually once a
  day
