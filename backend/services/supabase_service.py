import os
from supabase import create_client, Client
from config import Config
import logging

logger = logging.getLogger(__name__)

class SupabaseService:
    def __init__(self):
        self.url = Config.SUPABASE_URL
        self.key = Config.SUPABASE_SERVICE_ROLE_KEY or Config.SUPABASE_KEY
        self.client: Client = None
        
        if self.url and self.key:
            try:
                self.client = create_client(self.url, self.key)
                logger.info("Supabase Client initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase Client: {e}")

    def upload_image(self, file_path: str, bucket: str = "images") -> str:
        """
        Uploads a local image to Supabase Storage and returns the public URL.
        """
        if not self.client:
            logger.warning("Supabase Client not initialized. Skipping upload.")
            return None

        try:
            filename = os.path.basename(file_path)
            with open(file_path, "rb") as f:
                # Upload to bucket
                self.client.storage.from_(bucket).upload(
                    path=filename,
                    file=f,
                    file_options={"upsert": "true", "content-type": "image/jpeg"}
                )
            
            # Get public URL
            res = self.client.storage.from_(bucket).get_public_url(filename)
            return res
        except Exception as e:
            logger.error(f"Error uploading to Supabase: {e}")
            return None

# Singleton instance
supabase_service = SupabaseService()
