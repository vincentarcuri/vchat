import sqlite3

import click
from flask import current_app, g

def get_db() -> sqlite3.Connection:
    """
    Retrieves the database stored in `g`, if no database in `g` creates
    a sqlite3 Connection and stores in `g`.
    """
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    
    return g.db


def close_db(e=None):
    """Closes the database if there is a connection."""
    db: sqlite3.Connection = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    """Executes the SQL file to create the database."""
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf-8"))


@click.command("init-db")
def init_db_command():
    """
    Creates a CLI command for initializing the database.
        `flask --app vchat init-db`
    """
    init_db()
    click.echo("Initialized the database.")


# The `close_db` & `init_db_command` functions need to be registered with the
# application instance, but since we are using are using a factory function in
# 'vchat/__init__.py' we will have to create a function that takes the
# the application and does the registration.
    
def init_app(app):
    # Tell flask to call `close_db` when cleaning up.
    app.teardown_appcontext(close_db)
    # Adds the command
    app.cli.add_command(init_db_command)