from pydantic import BaseModel, HttpUrl

class UserInfoBase(BaseModel):
    """Base schema for user information, allowing optional identification."""
    platform_user_id: str | None = None
    username: str | None = None

class LinkCrawlRequest(BaseModel):
    """Request schema for initiating a crawl based on a URL."""
    link: HttpUrl
    user_info: UserInfoBase

class RawTextCrawlRequest(BaseModel):
    """Request schema for initiating a crawl based on raw text content."""
    text: str
    user_info: UserInfoBase
    metadata: dict | None = None

class CrawlSuccessResponse(BaseModel):
    """Response schema indicating successful crawl submission or completion."""
    status: str
    document_id: str | None = None # Optional, might be returned if processed synchronously