import os
import json
import logging
from app import create_app
from database import db
from models.db_models import GenerationJob
from services.supabase_service import supabase_service
from config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Migration")

def migrate():
    app = create_app()
    with app.app_context():
        logger.info("Starting comprehensive migration to Supabase Storage...")
        
        jobs = GenerationJob.query.all()
        logger.info(f"Found {len(jobs)} jobs to analyze.")
        
        updated_count = 0
        
        for job in jobs:
            modified = False
            
            # 1. Migrate Input Images (bucket: inputs)
            if job.input_image_url:
                try:
                    # Check if it's a JSON list or a single path
                    try:
                        urls = json.loads(job.input_image_url)
                        is_list = isinstance(urls, list)
                    except:
                        urls = [job.input_image_url]
                        is_list = False

                    new_urls = []
                    for url in urls:
                        if url and (url.startswith('/uploads/') or not url.startswith('http')):
                            filename = os.path.basename(url)
                            local_path = os.path.join(Config.UPLOAD_FOLDER, filename)
                            
                            if os.path.exists(local_path):
                                logger.info(f"Migrating input for job {job.id}: {filename}")
                                cloud_url = supabase_service.upload_image(local_path, filename, bucket="inputs")
                                if cloud_url:
                                    new_urls.append(cloud_url)
                                    modified = True
                                else:
                                    new_urls.append(url)
                            else:
                                new_urls.append(url)
                        else:
                            new_urls.append(url)
                    
                    if modified:
                        job.input_image_url = json.dumps(new_urls) if is_list else new_urls[0]
                except Exception as e:
                    logger.error(f"Error migrating input for job {job.id}: {e}")

            # 2. Migrate Metadata Crops (bucket: crops)
            try:
                meta = json.loads(job.metadata_json) if job.metadata_json else {}
                if "best_face_crop" in meta and not meta["best_face_crop"].startswith('http'):
                    filename = os.path.basename(meta["best_face_crop"])
                    local_path = os.path.join(Config.FACE_CROPS_FOLDER, filename)
                    if os.path.exists(local_path):
                        logger.info(f"Migrating face crop for job {job.id}: {filename}")
                        cloud_url = supabase_service.upload_image(local_path, filename, bucket="crops")
                        if cloud_url:
                            meta["best_face_crop"] = cloud_url
                            job.set_metadata(meta)
                            modified = True
            except Exception as e:
                logger.error(f"Error migrating metadata for job {job.id}: {e}")

            # 3. Migrate Output Images (bucket: outputs)
            try:
                images = json.loads(job.images_json) if job.images_json else []
                if images and any(not img.startswith('http') for img in images):
                    new_images = []
                    for img_url in images:
                        if not img_url.startswith('http'):
                            filename = os.path.basename(img_url)
                            local_path = os.path.join(Config.OUTPUTS_FOLDER, filename)
                            # Fallback check
                            if not os.path.exists(local_path):
                                local_path = os.path.join(Config.UPLOAD_FOLDER, filename)
                                
                            if os.path.exists(local_path):
                                logger.info(f"Migrating output for job {job.id}: {filename}")
                                cloud_url = supabase_service.upload_image(local_path, filename, bucket="outputs")
                                if cloud_url:
                                    new_images.append(cloud_url)
                                    modified = True
                                else:
                                    new_images.append(img_url)
                            else:
                                new_images.append(img_url)
                        else:
                            new_images.append(img_url)
                    
                    if modified:
                        job.set_images(new_images)
            except Exception as e:
                logger.error(f"Error migrating outputs for job {job.id}: {e}")

            if modified:
                updated_count += 1
                db.session.commit()
                logger.info(f"Job {job.id} fully cloudified.")

        logger.info(f"Migration complete. {updated_count} jobs updated and moved to Supabase.")

if __name__ == "__main__":
    migrate()
