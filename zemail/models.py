from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, EmailStr


class PlanLimits(BaseModel):
    apps_limit: int
    keys_limit: int
    webhook_endpoints_limit: int
    requests_per_minute: int
    requests_per_day: int
    mailboxes_page_size: int
    emails_page_size: int
    request_log_retention_days: int


class CurrentPlan(BaseModel):
    slug: str
    name: str


class AccountDeveloperApi(BaseModel):
    enabled: bool
    default_version: Optional[str] = None
    limits: PlanLimits


class Account(BaseModel):
    id: int
    name: str
    email: EmailStr
    email_verified_at: Optional[datetime] = None
    tier: str
    tier_label: str
    current_plan: Optional[CurrentPlan] = None
    developer_api: AccountDeveloperApi


class SubscriptionPlan(BaseModel):
    slug: str
    name: str
    tier_role: str


class Subscription(BaseModel):
    status: str
    tier: str
    plan: Optional[SubscriptionPlan] = None
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None


class MailboxUsage(BaseModel):
    active_count: int
    active_limit: int
    daily_count: int
    daily_limit: int


class StorageUsage(BaseModel):
    limit_bytes: int
    actual_used_bytes: int
    visible_used_bytes: int
    hidden_email_count: int
    percent: float


class DeveloperApiUsage(BaseModel):
    apps_count: int
    keys_count: int
    limits: PlanLimits


class Usage(BaseModel):
    mailboxes: MailboxUsage
    storage: StorageUsage
    developer_api: DeveloperApiUsage


class Domain(BaseModel):
    id: int
    name: str
    allowed_types: List[str]


class Mailbox(BaseModel):
    id: int
    address: EmailStr
    type: str
    domain: str
    expires_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    unread_count: int
    emails_count: int


class EmailAttachmentSummary(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    size: Optional[int] = None
    downloadable: bool


class EmailSummary(BaseModel):
    id: int
    sender: str
    sender_email: EmailStr
    subject: str
    preview: str
    received_at: Optional[datetime] = None
    is_read: bool
    is_blocked: bool
    attachments_count: int


class EmailDetail(BaseModel):
    id: int
    sender: str
    sender_name: Optional[str] = None
    sender_email: EmailStr
    subject: str
    preview: str
    received_at: Optional[datetime] = None
    is_read: bool
    is_blocked: bool
    blocked_domain: Optional[str] = None
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    attachments: List[EmailAttachmentSummary]


class EmailReadState(BaseModel):
    id: int
    is_read: bool


class AttachmentDownload(BaseModel):
    url: str
    expires_at: str


class DeletedObject(BaseModel):
    deleted: bool
    id: int


class PageMeta(BaseModel):
    # Depending on what the API actually returns for pagination meta, this can be fleshed out.
    pass


class ListEnvelope(BaseModel):
    object: str
    has_more: bool
    next_cursor: Optional[Union[str, int]] = None
    # Data is implemented in subclasses
    # Meta is implemented in subclasses


class MailboxList(ListEnvelope):
    data: List[Mailbox]
    meta: Dict[str, Any]


class EmailList(ListEnvelope):
    data: List[EmailSummary]
    meta: Dict[str, Any]


class DomainList(ListEnvelope):
    data: List[Domain]
    meta: Dict[str, Any]


EmailAttachment = EmailAttachmentSummary
