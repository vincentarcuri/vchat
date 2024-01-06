import os
from flask import Flask

UPLOADS = os.path.join(os.getcwd(), "vchat", "uploads")



def create_app(test_config=None) -> Flask:
    """The Application Factory function builds the app."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "vchat.sqlite"),
        UPLOAD_FOLDER=UPLOADS,
    )

    if test_config is None:
        # Load the instance configuration if it exists (when not testing)
        app.config.from_pyfile("config.py", silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Ensure Uploads Folder exists
    try:
        os.makedirs(UPLOADS)
    except OSError:
        pass

    # Add initializing db function to app
    from . import db
    db.init_app(app)

    # Add authorization blueprint
    from . import auth
    app.register_blueprint(auth.bp)

    # Add chat pages
    from . import chat
    app.register_blueprint(chat.bp)
    app.add_url_rule('/', endpoint="index")

    return app
