import re
from uuid import UUID, uuid4

import anyio

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.modules.storage.schemas import ImageUploadResponse


class StorageService:
    """Single, scoped integration point for Supabase meal-image storage."""

    allowed_content_types = {"image/jpeg", "image/png", "image/webp"}
    max_image_bytes = 8 * 1024 * 1024

    def __init__(self) -> None:
        self.settings = get_settings()

    async def upload_meal_image(
        self, *, meal_id: UUID, filename: str, content_type: str, content: bytes
    ) -> ImageUploadResponse:
        if content_type not in self.allowed_content_types:
            raise AppError("unsupported_image", "Use a JPEG, PNG, or WebP image", 415)
        if not content or len(content) > self.max_image_bytes:
            raise AppError("invalid_image", "Image must be between 1 byte and 8 MB", 400)
        if not self.settings.supabase_url or not self.settings.supabase_service_role_key:
            raise AppError("storage_unavailable", "Image storage is not configured", 503)

        extension = self._extension(filename, content_type)
        storage_path = f"meals/{meal_id}/{uuid4()}.{extension}"
        await anyio.to_thread.run_sync(self._upload, storage_path, content, content_type)
        public_url = await anyio.to_thread.run_sync(self._public_url, storage_path)
        return ImageUploadResponse(image_url=public_url, storage_path=storage_path)

    @staticmethod
    def _extension(filename: str, content_type: str) -> str:
        safe_name = re.sub(r"[^a-zA-Z0-9._-]", "", filename)
        if "." in safe_name:
            candidate = safe_name.rsplit(".", 1)[1].lower()
            if candidate in {"jpg", "jpeg", "png", "webp"}:
                return candidate
        return {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}[content_type]

    def _client(self):
        from supabase import create_client

        return create_client(
            self.settings.supabase_url,
            self.settings.supabase_service_role_key.get_secret_value(),
        )

    def _upload(self, path: str, content: bytes, content_type: str) -> None:
        try:
            self._client().storage.from_(self.settings.supabase_storage_bucket).upload(
                path, content, {"content-type": content_type, "upsert": "false"}
            )
        except Exception as exc:
            raise AppError("storage_upload_failed", "Unable to upload image. Please try again.", 502) from exc

    def _public_url(self, path: str) -> str:
        try:
            result = self._client().storage.from_(self.settings.supabase_storage_bucket).get_public_url(path)
            return result if isinstance(result, str) else result["publicUrl"]
        except Exception as exc:
            raise AppError("storage_upload_failed", "Unable to prepare image URL. Please try again.", 502) from exc
