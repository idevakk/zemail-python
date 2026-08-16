from zemail.models import (
    Account,
    AttachmentDownload,
    DeletedObject,
    DomainList,
    EmailDetail,
    EmailList,
    EmailReadState,
    Mailbox,
    Subscription,
    Usage,
)


def test_get_account(client, mock_api):
    mock_data = {
        "id": 1,
        "name": "Test User",
        "email": "test@example.com",
        "tier": "plus",
        "tier_label": "PLUS",
        "developer_api": {
            "enabled": True,
            "limits": {
                "apps_limit": 3,
                "keys_limit": 10,
                "webhook_endpoints_limit": 0,
                "requests_per_minute": 120,
                "requests_per_day": 25000,
                "mailboxes_page_size": 100,
                "emails_page_size": 50,
                "request_log_retention_days": 7,
            },
        },
    }

    mock_api.get("/account").respond(json={"object": "account", "data": mock_data, "meta": {}})

    account = client.account.get()
    assert isinstance(account, Account)
    assert account.email == "test@example.com"
    assert account.tier == "plus"


def test_subscription(client, mock_api):
    mock_data = {
        "status": "active",
        "tier": "pro",
        "plan": {"slug": "pro-monthly", "name": "Pro Monthly", "tier_role": "pro"},
        "starts_at": "2026-01-01T00:00:00Z",
        "ends_at": "2026-12-31T23:59:59Z",
        "cancelled_at": None,
    }

    mock_api.get("/account/subscription").respond(
        json={"object": "subscription", "data": mock_data, "meta": {}}
    )

    sub1 = client.account.get_subscription()
    sub2 = client.account.subscription()
    assert isinstance(sub1, Subscription)
    assert isinstance(sub2, Subscription)
    assert sub1.status == "active"
    assert sub1.tier == "pro"
    assert sub1.plan.name == "Pro Monthly"


def test_usage(client, mock_api):
    mock_data = {
        "mailboxes": {
            "active_count": 5,
            "active_limit": 50,
            "daily_count": 10,
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
                "requests_per_day": 10000,
                "mailboxes_page_size": 100,
                "emails_page_size": 50,
                "request_log_retention_days": 7,
            },
        },
    }

    mock_api.get("/account/usage").respond(json={"object": "usage", "data": mock_data, "meta": {}})

    usage1 = client.account.get_usage()
    usage2 = client.account.usage()
    assert isinstance(usage1, Usage)
    assert isinstance(usage2, Usage)
    assert usage1.mailboxes.active_count == 5
    assert usage1.storage.limit_bytes == 104857600


def test_list_domains(client, mock_api):
    mock_data = [{"id": 1, "name": "zemail.me", "allowed_types": ["public", "custom"]}]

    mock_api.get("/domains").respond(
        json={"object": "list", "data": mock_data, "has_more": False, "meta": {"count": 1}}
    )

    domains = client.domains.list()
    assert isinstance(domains, DomainList)
    assert len(domains.data) == 1
    assert domains.data[0].name == "zemail.me"


def test_create_and_get_and_delete_mailbox(client, mock_api):
    mock_data = {
        "id": 10,
        "address": "random123@zemail.me",
        "type": "public",
        "domain": "zemail.me",
        "unread_count": 0,
        "emails_count": 0,
    }

    mock_api.post("/mailboxes").respond(
        status_code=201, json={"object": "mailbox", "data": mock_data, "meta": {}}
    )
    mock_api.get("/mailboxes/10").respond(json={"object": "mailbox", "data": mock_data, "meta": {}})
    mock_api.delete("/mailboxes/10").respond(
        json={"object": "mailbox", "data": {"deleted": True, "id": 10}, "meta": {}}
    )

    mailbox = client.mailboxes.create(type="random")
    assert isinstance(mailbox, Mailbox)
    assert mailbox.address == "random123@zemail.me"
    assert mailbox.id == 10

    fetched = client.mailboxes.get(mailbox_id=10)
    assert isinstance(fetched, Mailbox)
    assert fetched.id == 10

    deleted = client.mailboxes.delete(mailbox_id=10)
    assert isinstance(deleted, DeletedObject)
    assert deleted.deleted is True
    assert deleted.id == 10


def test_emails_workflow(client, mock_api):
    list_mock = [
        {
            "id": 100,
            "sender": "sender@example.com",
            "sender_email": "sender@example.com",
            "subject": "Hello",
            "preview": "World",
            "is_read": False,
            "is_blocked": False,
            "attachments_count": 1,
        }
    ]
    detail_mock = {
        "id": 100,
        "sender": "sender@example.com",
        "sender_email": "sender@example.com",
        "subject": "Hello",
        "preview": "World",
        "is_read": False,
        "is_blocked": False,
        "body_text": "Hello world text",
        "body_html": "<p>Hello world html</p>",
        "attachments": [
            {
                "id": "att_1",
                "name": "invoice.pdf",
                "size": 1024,
                "downloadable": True,
            }
        ],
    }

    mock_api.get("/mailboxes/10/emails").respond(
        json={"object": "list", "data": list_mock, "has_more": False, "meta": {}}
    )
    mock_api.get("/mailboxes/10/emails/100").respond(
        json={"object": "email", "data": detail_mock, "meta": {}}
    )
    mock_api.post("/mailboxes/10/emails/100/mark-read").respond(
        json={"object": "email", "data": {"id": 100, "is_read": True}, "meta": {}}
    )
    mock_api.post("/mailboxes/10/emails/100/attachments/att_1/download-url").respond(
        json={
            "object": "attachment_download",
            "data": {
                "url": "https://download.zemail.me/att_1",
                "expires_at": "2026-08-17T12:00:00Z",
            },
            "meta": {},
        }
    )
    mock_api.delete("/mailboxes/10/emails/100").respond(
        json={"object": "email", "data": {"deleted": True, "id": 100}, "meta": {}}
    )

    # Test accessing through client.mailboxes.emails chaining
    emails = client.mailboxes.emails.list(mailbox_id=10)
    assert isinstance(emails, EmailList)
    assert len(emails.data) == 1
    assert emails.data[0].subject == "Hello"

    # Get email detail
    email = client.emails.get(mailbox_id=10, email_id=100)
    assert isinstance(email, EmailDetail)
    assert email.body_text == "Hello world text"
    assert len(email.attachments) == 1
    assert email.attachments[0].name == "invoice.pdf"

    # Mark as read
    read1 = client.emails.mark_read(mailbox_id=10, email_id=100)
    assert isinstance(read1, EmailReadState)
    assert read1.is_read is True

    read2 = client.emails.mark_as_read(mailbox_id=10, email_id=100)
    assert isinstance(read2, EmailReadState)
    assert read2.is_read is True

    # Download URL
    download = client.emails.get_attachment_download_url(
        mailbox_id=10, email_id=100, attachment_id="att_1"
    )
    assert isinstance(download, AttachmentDownload)
    assert download.url == "https://download.zemail.me/att_1"

    # Delete email
    deleted = client.emails.delete(mailbox_id=10, email_id=100)
    assert isinstance(deleted, DeletedObject)
    assert deleted.deleted is True
