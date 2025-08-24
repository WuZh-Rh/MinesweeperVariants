from flask import Flask, redirect
from flask_cors import CORS

from minesweepervariants.server.session import SessionManager

from .config import CORS_resources, github_web
from .model import Model

__all__ = ["create_app"]

def create_app(sm: SessionManager, model: type[Model]) -> Flask:
    app = Flask('Minesweeper Variants')
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

    app.add_url_rule('/api/new', 'generate_board', sm.wrapper(model.generate_board), methods=['GET', 'POST'])
    app.add_url_rule('/api/metadata', 'metadata', sm.wrapper(model.metadata), methods=['GET', 'POST'])
    app.add_url_rule('/api/click', 'click', sm.wrapper(model.click), methods=['GET', 'POST'])
    app.add_url_rule('/api/hint', 'hint_post', sm.wrapper(model.hint_post), methods=['GET', 'POST'])
    app.add_url_rule('/api/rules', 'get_rule_list', sm.wrapper(model.get_rule_list), methods=['GET', 'POST'])
    app.add_url_rule('/api/reset', 'reset', sm.wrapper(model.reset), methods=['GET', 'POST'])
    app.add_url_rule('/api/new_token', 'gen_token_route', sm.gen_token_route(), methods=['GET', 'POST'])

    return app