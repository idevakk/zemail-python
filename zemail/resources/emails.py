from typing import TYPE_CHECKING, Optional

from ..models import AttachmentDownload, DeletedObject, EmailDetail, EmailList, EmailReadState

if TYPE_CHECKING:
    from ..client import ZemailClient


class EmailsResource:
    def __init__(self, client: "ZemailClient"):
        self._client = client

    def list(
        self,
        mailbox_id: int,
        limit: Optional[int] = None,
        page: Optional[int] = None,
        search: Optional[str] = None,
    ) -> EmailList:
        """
        List emails for a mailbox.
        """
        params = {}
        if limit is not None:
            params["limit"] = limit
        if page is not None:
            params["page"] = page
        if search is not None:
            params["search"] = search

        response = self._client.get(f"/mailboxes/{mailbox_id}/emails", params=params)
        return EmailList.model_validate(response)

    def get(self, mailbox_id: int, email_id: int) -> EmailDetail:
        """
        Get full email details.
        """
        response = self._client.get(f"/mailboxes/{mailbox_id}/emails/{email_id}")
        return EmailDetail.model_validate(response["data"])

    def delete(self, mailbox_id: int, email_id: int) -> DeletedObject:
        """
        Delete an email.
        """
        response = self._client.delete(f"/mailboxes/{mailbox_id}/emails/{email_id}")
        return DeletedObject.model_validate(response["data"])

    def mark_read(self, mailbox_id: int, email_id: int) -> EmailReadState:
        """
        Mark an email as read.
        """
        response = self._client.post(f"/mailboxes/{mailbox_id}/emails/{email_id}/mark-read")
        return EmailReadState.model_validate(response["data"])

    def mark_as_read(self, mailbox_id: int, email_id: int) -> EmailReadState:
        """
        Mark an email as read (alias for mark_read).
        """
        return self.mark_read(mailbox_id, email_id)

    def get_attachment_download_url(
        self, mailbox_id: int, email_id: int, attachment_id: str
    ) -> AttachmentDownload:
        """
        Create a temporary attachment download URL.
        """
        response = self._client.post(
            f"/mailboxes/{mailbox_id}/emails/{email_id}/attachments/{attachment_id}/download-url"
        )
        return AttachmentDownload.model_validate(response["data"])
