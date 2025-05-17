from flask import Blueprint, send_from_directory
import os

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def serve_index():
    """Serve a página inicial do frontend."""
    return send_from_directory('/app/frontend', 'index.html')

@web_bp.route('/<path:path>')
def serve_static(path):
    """Serve arquivos estáticos do frontend."""
    return send_from_directory('/app/frontend', path)
