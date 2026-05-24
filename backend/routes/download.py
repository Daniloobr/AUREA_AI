from flask import Blueprint, request, Response, jsonify
import requests
import time
import logging
from urllib.parse import urlparse

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
            'error': 'Parâmetro "url" é obrigatório'
        }), 400

    try:
        # Validate URL scheme
        parsed = urlparse(image_url)
        if parsed.scheme not in ('http', 'https'):
            raise ValueError('Invalid URL scheme')

        # Restringir domínios permitidos (Prevenção de SSRF)
        allowed_domains = [
            'replicate.delivery',
            'replicate.com',
            'supabase.co',
            '127.0.0.1',
            'localhost',
            request.host  # Permite o próprio domínio da API
        ]
        
        domain = parsed.netloc
        # Considera portas no netloc separando pelo :
        domain_without_port = domain.split(':')[0]
        
        if not any(domain_without_port.endswith(d.split(':')[0]) for d in allowed_domains):
            logger.warning(f"Tentativa de download proxy recusada para o domínio: {domain}")
            return jsonify({'success': False, 'error': 'URL de origem não autorizada'}), 403

        # Stream the remote image
        start_time = time.time()
        logger.info(f"Iniciando download da imagem: {image_url}")
        resp = requests.get(image_url, stream=True, timeout=(30, 120))
        elapsed_time = time.time() - start_time
        logger.info(f"Download (headers) recebido em {elapsed_time:.2f}s")
        resp.raise_for_status()

        # Determinar a extensão baseada no content-type
        ct = resp.headers.get('Content-Type', '')
        ext = 'jpg'
        if 'png' in ct:
            ext = 'png'
        elif 'webp' in ct:
            ext = 'webp'
            
        filename = f"ensaio_aureaia.{ext}"

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
    except requests.exceptions.Timeout as e:
        logger.error(f'Timeout fetching image for download (504): {e}')
        return jsonify({
            'success': False,
            'error': 'O servidor demorou muito para responder ao baixar a imagem. Tente novamente.'
        }), 504
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response is not None else 500
        logger.error(f'HTTP error fetching image for download (Status {status_code}): {e}')
        if status_code == 404:
            return jsonify({
                'success': False,
                'error': 'Imagem não encontrada no servidor de origem'
            }), 404
        return jsonify({
            'success': False,
            'error': 'Falha ao baixar a imagem da URL fornecida (imagem não encontrada ou inacessível).'
        }), 404
    except requests.exceptions.RequestException as e:
        logger.error(f'Error fetching image for download (404): {e}')
        return jsonify({
            'success': False,
            'error': 'Imagem não encontrada ou URL inválida. Verifique se a imagem ainda existe.'
        }), 404
    except Exception as e:
        logger.exception('Unexpected error in download_image (500)')
        return jsonify({
            'success': False,
            'error': 'Erro inesperado ao baixar imagem. Tente novamente.'
        }), 500
