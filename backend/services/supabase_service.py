import os
import logging
from typing import Optional, Union
from io import BytesIO
from supabase import create_client, Client
from config import Config

logger = logging.getLogger(__name__)

class SupabaseService:
    def __init__(self):
        self.url = os.environ.get('SUPABASE_URL')
        # Use Service Role Key if available to bypass RLS for backend operations
        self.key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('SUPABASE_KEY')
        self.client: Optional[Client] = None
        
        # Logs de depuração (seguros e mascarados)
        logger.info(f"[Supabase] URL carregada: {self.url}")
        logger.info(f"[Supabase] Chave configurada: {'Sim (Tamanho: ' + str(len(self.key)) + ')' if self.key else 'Não'}")
        
        if self.url and self.key:
            try:
                # Inicialização direta sem proxy
                self.client = create_client(self.url, self.key)
                logger.info("Supabase Client initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase Client: {e}")
        else:
            logger.error("Falha ao inicializar o Supabase: SUPABASE_URL ou chave de autenticação ausente.")

    def upload_image(self, file_source: Union[str, bytes, BytesIO], filename: str, bucket: str = "images") -> Optional[str]:
        """
        Uploads an image to Supabase Storage and returns the public URL.
        file_source: Can be a local path (str) or bytes/BytesIO.
        """
        if not self.client:
            logger.warning("Supabase Client not initialized. Skipping upload.")
            return None

        try:
            # Ensure bucket exists
            self._ensure_bucket_exists(bucket)

            if isinstance(file_source, str):
                # It's a file path
                if not os.path.exists(file_source):
                    logger.error(f"File path does not exist: {file_source}")
                    return None
                with open(file_source, "rb") as f:
                    file_data = f.read()
            elif isinstance(file_source, BytesIO):
                file_data = file_source.getvalue()
            else:
                file_data = file_source

            # Determine content type
            content_type = "image/jpeg"
            if filename.lower().endswith(".png"):
                content_type = "image/png"
            elif filename.lower().endswith(".webp"):
                content_type = "image/webp"

            # Upload to bucket
            path_on_bucket = filename
            res = self.client.storage.from_(bucket).upload(
                path=path_on_bucket,
                file=file_data,
                file_options={"upsert": "true", "content-type": content_type}
            )
            
            # Get public URL
            public_url = self.client.storage.from_(bucket).get_public_url(path_on_bucket)
            logger.info(f"Successfully uploaded {filename} to Supabase bucket '{bucket}'")
            return public_url
        except Exception as e:
            logger.error(f"Error uploading to Supabase Storage: {e}")
            return None

    def _ensure_bucket_exists(self, bucket_name: str):
        """Internal helper to create bucket if it doesn't exist."""
        try:
            buckets = self.client.storage.list_buckets()
            if not any(b.name == bucket_name for b in buckets):
                logger.info(f"Creating missing bucket: {bucket_name}")
                self.client.storage.create_bucket(bucket_name, options={"public": True})
        except Exception as e:
            logger.warning(f"Could not verify/create bucket {bucket_name}: {e}")

# Singleton instance
supabase_service = SupabaseService()
