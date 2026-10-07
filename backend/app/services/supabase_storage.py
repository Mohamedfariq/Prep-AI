import logging
import uuid
from supabase import create_client, Client
from app.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_supabase_client: Client | None = None


def get_supabase_client() -> Client:
    global _supabase_client
    if _supabase_client is None:
        if not settings.supabase_url or not settings.supabase_service_role_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be configured")
        _supabase_client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    return _supabase_client


def upload_resume_file(user_id: str, file_bytes: bytes, original_filename: str) -> str:
    """
    Uploads a resume PDF to the private Supabase storage bucket.
    Returns the storage path key.
    """
    client = get_supabase_client()
    bucket_name = settings.supabase_bucket_name
    
    clean_name = original_filename.replace(" ", "_").replace("/", "_")
    storage_path = f"resumes/{user_id}/{uuid.uuid4().hex[:8]}_{clean_name}"

    try:
        client.storage.from_(bucket_name).upload(
            path=storage_path,
            file=file_bytes,
            file_options={"content-type": "application/pdf", "upsert": "true"},
        )
        return storage_path
    except Exception as e:
        logger.error(f"Failed to upload resume to Supabase storage: {e}")
        raise RuntimeError(f"Storage upload failed: {e}")


def get_resume_signed_url(storage_path: str, expiry_seconds: int | None = None) -> str | None:
    """
    Generates a temporary signed URL for private resume access.
    """
    if not storage_path:
        return None
    try:
        client = get_supabase_client()
        bucket_name = settings.supabase_bucket_name
        expiry = expiry_seconds or settings.supabase_signed_url_expiry_seconds
        res = client.storage.from_(bucket_name).create_signed_url(
            path=storage_path,
            expires_in=expiry,
        )
        return res.get("signedURL") or res.get("signedUrl")
    except Exception as e:
        logger.error(f"Failed to create signed URL for {storage_path}: {e}")
        return None


def delete_resume_file(storage_path: str) -> bool:
    """
    Removes the resume file from Supabase storage for privacy compliance.
    """
    if not storage_path:
        return False
    try:
        client = get_supabase_client()
        bucket_name = settings.supabase_bucket_name
        client.storage.from_(bucket_name).remove([storage_path])
        return True
    except Exception as e:
        logger.error(f"Failed to delete resume {storage_path}: {e}")
        return False
