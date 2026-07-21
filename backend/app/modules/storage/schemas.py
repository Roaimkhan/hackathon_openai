from pydantic import BaseModel, Field


class ImageUploadRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content_type: str = Field(pattern=r"^image/(jpeg|png|webp)$")


class ImageUploadResponse(BaseModel):
    image_url: str
    storage_path: str
