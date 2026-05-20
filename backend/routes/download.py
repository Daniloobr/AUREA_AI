from flask import Blueprint, request, Response, jsonify, current_app
import requests
import os
import logging
from urllib.parse import urlparse, unquote

logger = logging.getLogger(__name__)

download_bp = Blueprint('download', __name__)

@download_bp.route('/download-image', methods=['GET'])
def download_image():
    """Proxy endpoint to download an image from a given URL.

    Query Params:
        url: str - The absolute URL of the image to download.
    Returns:
        Flask Response with streamed image data and appropriate headers.
    """
    image_url = request.args.get('url')
    if not image_url:
        logger.warning('download-image called without url parameter')
        return jsonify({
            'success': False,
            'error': 'Missing required query parameter: url'
        }), 400

    try:
        # Validate URL scheme
        parsed = urlparse(image_url)
        if parsed.scheme not in ('http', 'https'):
            raise ValueError('Invalid URL scheme')

        # Stream the remote image
        resp = requests.get(image_url, stream=True, timeout=30)
        resp.raise_for_status()

        # Determine filename
        filename = os.path.basename(parsed.path)
        filename = unquote(filename) or 'downloaded_image'
        # Fallback to generic extension if missing
        if '.' not in filename:
            # Try to guess from content-type
            ct = resp.headers.get('Content-Type', '')
            ext = ct.split('/')[-1] if '/' in ct else 'bin'
            filename = f"{filename}.{ext}"

        # Content-Type header
        content_type = resp.headers.get('Content-Type', 'application/octet-stream')

        def generate():
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk

        return Response(
            generate(),
            mimetype=content_type,
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Cache-Control': 'no-store'
            }
        )
    except requests.exceptions.RequestException as e:
        logger.error(f'Error fetching image for download: {e}')
        return jsonify({
            'success': False,
            'error': f'Failed to fetch image: {str(e)}'
        }), 502
    except Exception as e:
        logger.exception('Unexpected error in download_image')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
