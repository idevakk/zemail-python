from typing import TYPE_CHECKING

from ..models import DomainList

if TYPE_CHECKING:
    from ..client import ZemailClient


class DomainsResource:
    def __init__(self, client: "ZemailClient"):
        self._client = client

    def list(self) -> DomainList:
        """
        List domains available for mailbox creation.
        """
        response = self._client.get("/domains")
        return DomainList.model_validate(response)
