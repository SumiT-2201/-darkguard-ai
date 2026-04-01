import os
import sys

# Ensure the root path is the current directory so app imports resolve
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

flask_app = create_app()

if __name__ == '__main__':
    # Use the config attributes
    host = flask_app.config.get('HOST', '0.0.0.0')
    port = flask_app.config.get('PORT', 5000)
    debug = flask_app.config.get('DEBUG', True)
    flask_app.run(host=host, port=port, debug=debug)
