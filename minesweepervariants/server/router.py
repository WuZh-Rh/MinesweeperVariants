from flask import Flask, redirect
from flask_cors import CORS

from .config import CORS_resources, github_web
from .model import Model

__all__ = ["create_app"]

def create_app(wrapper, name: str = __name__) -> Flask:
    app = Flask(__name__)
    CORS(app, resources=CORS_resources, supports_credentials=True)

    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Referrer-Policy'] = 'unsafe-url'
        if 'Access-Control-Allow-Credentials' in response.headers:
            try:
                del response.headers['Access-Control-Allow-Credentials']
            except Exception:
                pass
        return response

    @app.route('/')
    def root():
        return redirect(github_web)

    app.add_url_rule('/api/new', 'generate_board', wrapper(Model.generate_board), methods=['GET', 'POST'])
    app.add_url_rule('/api/metadata', 'metadata', wrapper(Model.metadata), methods=['GET', 'POST'])
    app.add_url_rule('/api/click', 'click', wrapper(Model.click), methods=['GET', 'POST'])
    app.add_url_rule('/api/hint', 'hint_post', wrapper(Model.hint_post), methods=['GET', 'POST'])
    app.add_url_rule('/api/rules', 'get_rule_list', wrapper(Model.get_rule_list), methods=['GET', 'POST'])
    app.add_url_rule('/api/reset', 'reset', wrapper(Model.reset), methods=['GET', 'POST'])

    return app