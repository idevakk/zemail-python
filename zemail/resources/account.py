from typing import TYPE_CHECKING

from ..models import Account, Subscription, Usage

if TYPE_CHECKING:
    from ..client import ZemailClient


class AccountResource:
    def __init__(self, client: "ZemailClient"):
        self._client = client

    def get(self) -> Account:
        """
        Get the authenticated account snapshot.
        """
        response = self._client.get("/account")
        return Account.model_validate(response["data"])

    def get_subscription(self) -> Subscription:
        """
        Get the current subscription snapshot.
        """
        response = self._client.get("/account/subscription")
        return Subscription.model_validate(response["data"])

    def subscription(self) -> Subscription:
        """
        Get the current subscription snapshot (alias for get_subscription).
        """
        return self.get_subscription()

    def get_usage(self) -> Usage:
        """
        Get mailbox, storage and Developer API usage.
        """
        response = self._client.get("/account/usage")
        return Usage.model_validate(response["data"])

    def usage(self) -> Usage:
        """
        Get mailbox, storage and Developer API usage (alias for get_usage).
        """
        return self.get_usage()
