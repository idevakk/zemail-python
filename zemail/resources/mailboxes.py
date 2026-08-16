from typing import TYPE_CHECKING, Optional

from ..models import DeletedObject, Mailbox, MailboxList

if TYPE_CHECKING:
    from ..client import ZemailClient
    from .emails import EmailsResource


class MailboxesResource:
    def __init__(self, client: "ZemailClient"):
        self._client = client

    @property
    def emails(self) -> "EmailsResource":
        """
        Access emails resource.
        """
        return self._client.emails

    def list(self, limit: Optional[int] = None, page: Optional[int] = None) -> MailboxList:
        """
        List owned mailboxes.
        """
        params = {}
        if limit is not None:
            params["limit"] = limit
        if page is not None:
            params["page"] = page

        response = self._client.get("/mailboxes", params=params)
        return MailboxList.model_validate(response)

    def create(
        self,
        type: str,
        domain: Optional[str] = None,
        username: Optional[str] = None,
        google_alias_mode: Optional[str] = None,
    ) -> Mailbox:
        """
        Create a mailbox.
        """
        payload = {"type": type}
        if domain is not None:
            payload["domain"] = domain
        if username is not None:
            payload["username"] = username
        if google_alias_mode is not None:
            payload["google_alias_mode"] = google_alias_mode

        response = self._client.post("/mailboxes", json=payload)
        return Mailbox.model_validate(response["data"])

    def get(self, mailbox_id: int) -> Mailbox:
        """
        Get a single mailbox.
        """
        response = self._client.get(f"/mailboxes/{mailbox_id}")
        return Mailbox.model_validate(response["data"])

    def delete(self, mailbox_id: int) -> DeletedObject:
        """
        Delete a mailbox.
        """
        response = self._client.delete(f"/mailboxes/{mailbox_id}")
        return DeletedObject.model_validate(response["data"])
