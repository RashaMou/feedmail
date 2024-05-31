import json
import logging
from typing import Dict

import requests

from feedmail import logger


class JMAPClient:
    def __init__(self, token: str, accountid: str, username: str, to: str):
        self.token = token
        self.accountid = accountid
        self.hostname = "https://api.fastmail.com/.well-known/jmap"
        self.session = {}
        self.draft_mailbox_id: str = ""
        self.username = username
        self.to = to
        self.identityid: str = ""
        self.api_url: str = ""

    def get_session(self) -> Dict:
        """Return JMAP session as python dict"""
        if self.session:
            return self.session

        try:
            res = requests.get(
                self.hostname,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.token}",
                },
            )

            res.raise_for_status()
            self.session = res.json()
            self.api_url = self.session["apiUrl"]
        except requests.RequestException as e:
            logger.error(f"Failed to get session: {e}")
            raise

        return self.session

    def get_identityid(self) -> str:
        """Return the identityId for an address matching self.username"""
        if self.identityid:
            return self.identityid

        try:
            res = self.send_request(
                [["Identity/get", {"accountId": self.accountid}, "i"]],
            )

            identityid = next(
                filter(
                    lambda i: i["email"] == self.username,
                    res["methodResponses"][0][1]["list"],
                )
            )["id"]

            self.identityid = str(identityid)
        except (KeyError, StopIteration) as e:
            logger.error(f"Failed to get identity id: {e}")
            raise

        return self.identityid

    def send_request(self, call: list) -> Dict:
        self.get_session()

        data = {
            "using": [
                "urn:ietf:params:jmap:core",
                "urn:ietf:params:jmap:mail",
                "urn:ietf:params:jmap:submission",
            ],
            "methodCalls": call,
        }

        try:
            res = requests.post(
                self.api_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.token}",
                },
                data=json.dumps(data),
            )
            res.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

        return res.json()

    def get_draft_mailbox_id(self) -> str:
        if self.draft_mailbox_id:
            return self.draft_mailbox_id

        try:
            res = self.send_request(
                [
                    [
                        "Mailbox/query",
                        {"accountId": self.accountid, "filter": {"name": "Drafts"}},
                        "a",
                    ]
                ],
            )
            self.draft_mailbox_id = res["methodResponses"][0][1]["ids"][0]
        except KeyError as e:
            logger.error(f"Failed to get draft mailbox id: {e}")
            raise

        return self.draft_mailbox_id

    def send_email(self, subject, body, author):
        identityid = self.get_identityid()
        draft_mailbox_id = self.get_draft_mailbox_id()

        draft = {
            "from": [{"email": self.username, "name": author}],
            "to": [{"email": self.to}],
            "subject": subject,
            "keywords": {"$draft": True},
            "mailboxIds": {draft_mailbox_id: True},
            "bodyValues": {"body": {"value": body, "charset": "utf-8"}},
            "textBody": [{"partId": "body", "type": "text/plain"}],
            "htmlBody": [{"partId": "body", "type": "text/html"}],
        }

        try:
            res = self.send_request(
                [
                    [
                        "Email/set",
                        {"accountId": self.accountid, "create": {"draft": draft}},
                        "a",
                    ],
                    [
                        "EmailSubmission/set",
                        {
                            "accountId": self.accountid,
                            "onSuccessDestroyEmail": ["#sendIt"],
                            "create": {
                                "sendIt": {
                                    "emailId": "#draft",
                                    "identityId": identityid,
                                }
                            },
                        },
                        "b",
                    ],
                ],
            )
            print(res)
        except KeyError as e:
            logger.error(f"Failed to send email: {e}")
            raise
