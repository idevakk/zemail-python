import os

from zemail import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    ZemailAPIError,
    ZemailClient,
)


def main():
    api_key = os.environ.get("ZEMAIL_API_KEY", "zm_live_dummy_key_for_testing")
    print(f"Initializing Zemail SDK with key: {api_key[:10]}...")

    with ZemailClient(api_key=api_key) as client:
        try:
            # 1. Account & Subscription details
            print("\n--- 1. Account & Usage ---")
            account = client.account.get()
            print(f"Account: {account.email} (ID: {account.id}, Tier: {account.tier})")

            subscription = client.account.subscription()
            print(f"Subscription Status: {subscription.status}")

            usage = client.account.usage()
            print(
                f"Mailboxes in use: {usage.mailboxes.active_count}/{usage.mailboxes.active_limit}"
            )

            # 2. Domains
            print("\n--- 2. Available Domains ---")
            domains = client.domains.list()
            for domain in domains.data:
                print(f"Domain: {domain.name} (Allowed: {domain.allowed_types})")

            # 3. Mailboxes
            print("\n--- 3. Creating Random Mailbox ---")
            mailbox = client.mailboxes.create(type="random")
            print(f"Created Mailbox: {mailbox.address} (ID: {mailbox.id})")

            # 4. Emails
            print(f"\n--- 4. Checking Emails for Mailbox #{mailbox.id} ---")
            emails = client.emails.list(mailbox_id=mailbox.id)
            print(f"Found {len(emails.data)} email(s).")

            # 5. Clean up
            print(f"\n--- 5. Deleting Mailbox #{mailbox.id} ---")
            deleted = client.mailboxes.delete(mailbox_id=mailbox.id)
            print(f"Deleted successfully: {deleted.deleted}")

        except AuthenticationError as e:
            print(f"\nAuthentication Error: {e.message}")
            print("Provide a valid ZEMAIL_API_KEY environment variable to test live endpoints.")
        except ValidationError as e:
            print(f"\nValidation Error: {e.message}, details: {e.errors}")
        except RateLimitError as e:
            print(f"\nRate Limit Error: {e.message}")
        except NotFoundError as e:
            print(f"\nResource Not Found: {e.message}")
        except ZemailAPIError as e:
            print(f"\nAPI Error [{e.status}]: {e.message}")


if __name__ == "__main__":
    main()
