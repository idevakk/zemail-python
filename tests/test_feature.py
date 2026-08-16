import pytest

from zemail.exceptions import (
    NotFoundError,
    PermissionError,
    ZemailAPIError,
)
from zemail.models import (
    Account,
    AttachmentDownload,
    DeletedObject,
    DomainList,
    EmailDetail,
    EmailList,
    EmailReadState,
    Mailbox,
    MailboxList,
    Subscription,
    Usage,
)


def test_feature_account_profile_subscription_and_usage(client, mock_api):
    # 1. Account profile
    mock_api.get("/account").respond(
        json={
            "object": "account",
            "data": {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "email_verified_at": "2026-01-01T00:00:00Z",
                "tier": "pro",
                "tier_label": "Pro Plan",
                "current_plan": {"slug": "pro", "name": "Pro"},
                "developer_api": {
                    "enabled": True,
                    "default_version": "2026-04-23",
                    "limits": {
                        "apps_limit": 5,
                        "keys_limit": 10,
                        "webhook_endpoints_limit": 2,
                        "requests_per_minute": 120,
                        "requests_per_day": 25000,
                        "mailboxes_page_size": 100,
                        "emails_page_size": 50,
                        "request_log_retention_days": 14,
                    },
                },
            },
            "meta": {},
        }
    )

    # 2. Subscription
    mock_api.get("/account/subscription").respond(
        json={
            "object": "subscription",
            "data": {
                "status": "active",
                "tier": "pro",
                "plan": {"slug": "pro-monthly", "name": "Pro Monthly", "tier_role": "pro"},
                "starts_at": "2026-01-01T00:00:00Z",
                "ends_at": "2026-12-31T23:59:59Z",
                "cancelled_at": None,
            },
            "meta": {},
        }
    )

    # 3. Usage
    mock_api.get("/account/usage").respond(
        json={
            "object": "usage",
            "data": {
                "mailboxes": {
                    "active_count": 5,
                    "active_limit": 50,
                    "daily_count": 12,
                    "daily_limit": 100,
                },
                "storage": {
                    "limit_bytes": 104857600,
                    "actual_used_bytes": 1024000,
                    "visible_used_bytes": 1024000,
                    "hidden_email_count": 0,
                    "percent": 0.98,
                },
                "developer_api": {
                    "apps_count": 1,
                    "keys_count": 2,
                    "limits": {
                        "apps_limit": 5,
                        "keys_limit": 10,
                        "webhook_endpoints_limit": 2,
                        "requests_per_minute": 120,
                        "requests_per_day": 25000,
                        "mailboxes_page_size": 100,
                        "emails_page_size": 50,
                        "request_log_retention_days": 14,
                    },
                },
            },
            "meta": {},
        }
    )

    account = client.account.get()
    assert isinstance(account, Account)
    assert account.id == 1
    assert account.name == "John Doe"
    assert account.email == "john@example.com"
    assert account.tier == "pro"
    assert account.developer_api.enabled is True

    subscription = client.account.subscription()
    assert isinstance(subscription, Subscription)
    assert subscription.status == "active"
    assert subscription.tier == "pro"
    assert subscription.plan.name == "Pro Monthly"

    usage = client.account.usage()
    assert isinstance(usage, Usage)
    assert usage.mailboxes.active_count == 5
    assert usage.storage.limit_bytes == 104857600
    assert usage.developer_api.keys_count == 2


def test_feature_domains_list(client, mock_api):
    mock_api.get("/domains").respond(
        json={
            "object": "list",
            "data": [
                {"id": 10, "name": "zemail.me", "allowed_types": ["random", "custom"]},
                {"id": 11, "name": "mail.zemail.me", "allowed_types": ["public"]},
            ],
            "has_more": False,
            "next_cursor": None,
            "meta": {"total": 2},
        }
    )

    domains = client.domains.list()
    assert isinstance(domains, DomainList)
    assert len(domains.data) == 2
    assert domains.data[0].id == 10
    assert domains.data[0].name == "zemail.me"
    assert domains.data[0].allowed_types == ["random", "custom"]
    assert domains.data[1].id == 11


def test_feature_mailboxes_crud_and_pagination(client, mock_api):
    # 1. List mailboxes with pagination
    mock_api.get("/mailboxes").respond(
        json={
            "object": "list",
            "data": [
                {
                    "id": 101,
                    "address": "box1@zemail.me",
                    "type": "random",
                    "domain": "zemail.me",
                    "expires_at": None,
                    "created_at": "2026-08-01T00:00:00Z",
                    "unread_count": 2,
                    "emails_count": 5,
                }
            ],
            "has_more": True,
            "next_cursor": "cursor_123",
            "meta": {"current_page": 1, "per_page": 1, "total": 20},
        }
    )

    mailboxes = client.mailboxes.list(page=1, limit=1)
    assert isinstance(mailboxes, MailboxList)
    assert len(mailboxes.data) == 1
    assert mailboxes.has_more is True
    assert mailboxes.next_cursor == "cursor_123"
    assert mailboxes.data[0].address == "box1@zemail.me"

    # 2. Create custom mailbox
    mock_api.post("/mailboxes").respond(
        status_code=201,
        json={
            "object": "mailbox",
            "data": {
                "id": 102,
                "address": "my-inbox@zemail.me",
                "type": "custom",
                "domain": "zemail.me",
                "expires_at": None,
                "created_at": "2026-08-17T00:00:00Z",
                "unread_count": 0,
                "emails_count": 0,
            },
            "meta": {},
        },
    )

    custom_mailbox = client.mailboxes.create(
        type="custom",
        domain="zemail.me",
        username="my-inbox",
        google_alias_mode="prefix",
    )
    assert isinstance(custom_mailbox, Mailbox)
    assert custom_mailbox.address == "my-inbox@zemail.me"
    assert custom_mailbox.type == "custom"

    # 3. Get mailbox details
    mock_api.get("/mailboxes/102").respond(
        json={
            "object": "mailbox",
            "data": {
                "id": 102,
                "address": "my-inbox@zemail.me",
                "type": "custom",
                "domain": "zemail.me",
                "expires_at": None,
                "created_at": "2026-08-17T00:00:00Z",
                "unread_count": 3,
                "emails_count": 10,
            },
            "meta": {},
        }
    )

    fetched = client.mailboxes.get(mailbox_id=102)
    assert isinstance(fetched, Mailbox)
    assert fetched.unread_count == 3
    assert fetched.emails_count == 10

    # 4. Delete mailbox
    mock_api.delete("/mailboxes/102").respond(
        json={"object": "mailbox", "data": {"deleted": True, "id": 102}, "meta": {}}
    )

    deleted = client.mailboxes.delete(mailbox_id=102)
    assert isinstance(deleted, DeletedObject)
    assert deleted.deleted is True
    assert deleted.id == 102


def test_feature_emails_full_lifecycle(client, mock_api):
    # 1. List emails with search
    mock_api.get("/mailboxes/102/emails").respond(
        json={
            "object": "list",
            "data": [
                {
                    "id": 501,
                    "sender": "Service <noreply@service.com>",
                    "sender_email": "noreply@service.com",
                    "subject": "Your verification code: 123456",
                    "preview": "Your single-use login code is 123456",
                    "received_at": "2026-08-17T01:00:00Z",
                    "is_read": False,
                    "is_blocked": False,
                    "attachments_count": 1,
                }
            ],
            "has_more": False,
            "next_cursor": None,
            "meta": {"total": 1},
        }
    )

    emails = client.mailboxes.emails.list(mailbox_id=102, page=1, limit=25, search="verification")
    assert isinstance(emails, EmailList)
    assert len(emails.data) == 1
    assert emails.data[0].id == 501
    assert "123456" in emails.data[0].subject

    # 2. Get full email detail
    mock_api.get("/mailboxes/102/emails/501").respond(
        json={
            "object": "email",
            "data": {
                "id": 501,
                "sender": "Service <noreply@service.com>",
                "sender_name": "Service",
                "sender_email": "noreply@service.com",
                "subject": "Your verification code: 123456",
                "preview": "Your single-use login code is 123456",
                "received_at": "2026-08-17T01:00:00Z",
                "is_read": False,
                "is_blocked": False,
                "blocked_domain": None,
                "body_text": "Your code is 123456",
                "body_html": "<p>Your code is <b>123456</b></p>",
                "attachments": [
                    {
                        "id": "att_999",
                        "name": "statement.pdf",
                        "size": 20480,
                        "downloadable": True,
                    }
                ],
            },
            "meta": {},
        }
    )

    detail = client.emails.get(mailbox_id=102, email_id=501)
    assert isinstance(detail, EmailDetail)
    assert detail.sender_name == "Service"
    assert detail.body_text == "Your code is 123456"
    assert len(detail.attachments) == 1
    assert detail.attachments[0].id == "att_999"
    assert detail.attachments[0].name == "statement.pdf"

    # 3. Mark as read
    mock_api.post("/mailboxes/102/emails/501/mark-read").respond(
        json={"object": "email", "data": {"id": 501, "is_read": True}, "meta": {}}
    )

    read_state = client.emails.mark_as_read(mailbox_id=102, email_id=501)
    assert isinstance(read_state, EmailReadState)
    assert read_state.is_read is True

    # 4. Attachment download URL
    mock_api.post("/mailboxes/102/emails/501/attachments/att_999/download-url").respond(
        json={
            "object": "attachment_download",
            "data": {
                "url": "https://storage.zemail.me/att_999.pdf?token=xyz",
                "expires_at": "2026-08-17T02:00:00Z",
            },
            "meta": {},
        }
    )

    download = client.emails.get_attachment_download_url(
        mailbox_id=102, email_id=501, attachment_id="att_999"
    )
    assert isinstance(download, AttachmentDownload)
    assert "storage.zemail.me" in download.url

    # 5. Delete email
    mock_api.delete("/mailboxes/102/emails/501").respond(
        json={"object": "email", "data": {"deleted": True, "id": 501}, "meta": {}}
    )

    deleted = client.emails.delete(mailbox_id=102, email_id=501)
    assert isinstance(deleted, DeletedObject)
    assert deleted.deleted is True
    assert deleted.id == 501


def test_feature_error_responses(client, mock_api):
    # 403 Permission error
    mock_api.get("/account").respond(
        status_code=403,
        json={
            "error": {
                "type": "permission_error",
                "code": "insufficient_permissions",
                "message": "You do not have access to this resource.",
                "request_id": "req_perm_1",
            }
        },
    )
    with pytest.raises(PermissionError) as exc_perm:
        client.account.get()
    assert exc_perm.value.status == 403
    assert exc_perm.value.code == "insufficient_permissions"

    # 404 Not Found error
    mock_api.get("/mailboxes/99999").respond(
        status_code=404,
        json={
            "error": {
                "type": "not_found_error",
                "code": "mailbox_not_found",
                "message": "Mailbox not found.",
                "request_id": "req_404",
            }
        },
    )
    with pytest.raises(NotFoundError) as exc_404:
        client.mailboxes.get(mailbox_id=99999)
    assert exc_404.value.status == 404
    assert exc_404.value.code == "mailbox_not_found"

    # 400 Invalid Request
    mock_api.post("/mailboxes").respond(
        status_code=400,
        json={
            "error": {
                "type": "invalid_request_error",
                "code": "invalid_payload",
                "message": "Malformed request payload.",
            }
        },
    )
    with pytest.raises(ZemailAPIError) as exc_400:
        client.mailboxes.create(type="unknown")
    assert exc_400.value.status == 400
