def validate_image_url(url: str) -> bool:
    """
    Validates if the provided string is a valid image URL.
    """
    if not url:
        return False
        
    # Basic validation, ensuring it's an HTTP/HTTPS URL
    if not url.startswith("http://") and not url.startswith("https://") and not url.startswith("/uploads/"):
        return False
        
    return True
