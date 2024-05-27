# FeedMail

This Python program fetches RSS feeds and generates emails from them using Fastmail's JMAP client. It retrieves the latest news from the specified RSS feed, formats it into an email, and sends it to the specified recipient.

## Features

- Fetches and parses RSS feeds
- Generates HTML-formatted email content from RSS feed items
- Sends emails using Fastmail's JMAP protocol

## Components

- Database: Store RSS feed URLs, fetch status, and previously fetched posts.
- Job Queue: Manage and retry failed fetches.
- Cron Job: Schedule periodic execution.
- Python Script: Fetch feeds, process posts, and send emails.
- Python CLI: Add feed, list feed, remove feed, set config
- Config: Store Fastmail/JMAP credentials
- Logging

```
── feedmail
│   ├── __init__.py
│   ├── cli.py    Contains the command-line interface for managing feeds.
│   ├── config.py  Handles configuration settings
│   ├── db.py  Contains database connection setup and initialization
│   ├── jmap_client.py  Manages sending email's using Fastmail
│   ├── main.py  The main script to be executed by the cron job
│   └── models.py  Defines the database schema using SQLAlchemy
```

## Technical details

- When a feed is added using the CLI interface, it is added to a database
- The program periodically polls the urls in the database (though a cron job)
- Every time the cron is run, we check the feed urls from the db and store posts
  after the last_fetched time in the DB feed table
- We then send an email with all the new posts (or one email per feed? this
  might be an option to set)
