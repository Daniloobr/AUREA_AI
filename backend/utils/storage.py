import os

def get_storage_url(path):
    """
    Returns the absolute URL for a file.
    Environment Variable: STORAGE_BACKEND ('local' or 's3')
    """
    storage_type = os.getenv('STORAGE_BACKEND', 'local').lower()
    
    if storage_type == 's3':
        bucket = os.getenv('S3_BUCKET_NAME')
        region = os.getenv('AWS_REGION', 'us-east-1')
        return f"https://{bucket}.s3.{region}.amazonaws.com/{path}"
    
    if storage_type == 'r2':
        account_id = os.getenv('R2_ACCOUNT_ID')
        bucket = os.getenv('R2_BUCKET_NAME')
        return f"https://{account_id}.r2.cloudflarestorage.com/{bucket}/{path}"

    # Default Local
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
    return f"{base_url}/uploads/{path}"

def delete_file(path):
    """
    Deletes a file from the configured storage.
    """
    storage_type = os.getenv('STORAGE_BACKEND', 'local').lower()
    
    if storage_type == 'local':
        # Ensure path is just the filename or relative to uploads/
        filename = os.path.basename(path)
        full_path = os.path.join('uploads', filename)
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
    
    # Placeholder for S3/R2 deletion
    # elif storage_type in ['s3', 'r2']:
    #    ... delete from bucket ...
    
    return False
