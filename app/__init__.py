from flask import Flask
import base64


def create_app():
    app = Flask(__name__)

    # Register Blueprints
    from app.routes import routes_app
    app.register_blueprint(routes_app)
        # Custom filter for Base64 encoding
    def b64encode(value):
        return base64.b64encode(value.encode('utf-8')).decode('utf-8')

    # Register the filter with Jinja2
    app.jinja_env.filters['b64encode'] = b64encode


    return app
