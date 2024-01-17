import os
import json
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, send_from_directory, jsonify
)
from werkzeug.exceptions import abort

from vchat.auth import login_required
from vchat.db import get_db


ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'ipynb', 'cpp', 'h', 'c', 'png', 'docx', 'doc', 'xlsx',
    'pptx', 'py', 'js', 'html', 'sql', 'jpeg', 'jpg',
    }

bp = Blueprint("chat", __name__)

@bp.route('/')
@login_required
def index():
    """The Chat homepage where user can select from friends to chat or send files."""
    db = get_db()
    friends = db.execute(
        'SELECT user.id, user.username FROM user'
        ' JOIN contact ON contact.friend_id = user.id'
        ' WHERE contact.user_id = ?', 
        (g.user['id'],)
    ).fetchall()
    return render_template("chat/index.html", friends=friends)


@bp.route('/add', methods=("GET", "POST"))
@login_required
def add():
    """Form for adding a friend user to their friend list."""
    db = get_db()
    sql_users = db.execute(
        "SELECT username FROM user"
    ).fetchall()
    users = [x['username'] for x in sql_users]
    if request.method == "POST":
        friend = request.form["friend"]
        error = None

        if not friend:
            error = "Username is required."

        elif friend not in users:
            error = f"{friend} not found."
        
        if error is not None:
            flash(error)

        else:
            friend_id = db.execute(
                "SELECT id FROM user"
                " WHERE username = ?",
                (friend, )
            ).fetchone()[0]
            db.execute(
                "INSERT INTO contact (user_id, friend_id)"
                " VALUES (?, ?)",
                (g.user['id'], friend_id)
                )
            db.commit()
            db.execute(
                "INSERT INTO contact (user_id, friend_id)"
                " VALUES (?, ?)",
                (friend_id, g.user['id'])
                )
            db.commit()
            print("user added")
            return redirect(url_for("chat.index"))
        
    return render_template("chat/add.html")



@bp.route("/conv/<int:id>", methods=("GET",))
@login_required
def conv(id):
    db = get_db()
    friend = db.execute(
        "SELECT username FROM user WHERE id = ?",
        (id, )
    ).fetchone()
    return render_template("chat/conv.html", friend=friend, friend_id=id)


@bp.route("/fetch-msg/<int:id>/<int:last>", methods=("GET",))
@login_required
def fetch_messages(id, last):
    db = get_db()
    messages = db.execute(
        """SELECT id, from_id, to_id, msg
        FROM message
        WHERE (
            (from_id = ? AND to_id = ?)
            OR (from_id = ? AND to_id = ?)
        ) AND id > ?
        """, (g.user['id'], id, id, g.user['id'], int(last))
    ).fetchall()
    res = [
        {'id': row[0], 'from': row[1], 'to': row[2], 'msg': row[3]}
        for row in messages
    ]
    return json.dumps(res)





@bp.route("/send/<int:id>", methods=("POST", "GET"))
@login_required
def send(id):
    """Posts a message to the database."""
    if request.method == "POST":
        db = get_db()
        msg = request.form["message"]
        db.execute(
            "INSERT INTO message (from_id, to_id, msg)"
            " VALUES (?, ?, ?)",
            (g.user['id'], id, msg)
        )
        db.commit()
    return render_template("chat/send.html")

    
def allowed_file(filename:str) -> bool:
    """Checks the extension to determine if it is an allowed file."""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/files/<int:id>", methods=("GET", ))
@login_required
def file_view(id):
    """The file view, shows files sent between users."""
    db = get_db()
    files = db.execute(
        "SELECT files.id, files.name, files.type"
        " FROM files JOIN shared ON files.id = shared.file_id"
        " WHERE (from_id = ? AND to_id = ?)"
        " OR (from_id = ? AND to_id = ?)",
        (g.user['id'], id, id, g.user['id'])
    ).fetchall()
    return render_template("chat/files.html", files=files)


@bp.route("/file_upload/<int:id>", methods=("GET", "POST"))
@login_required
def upload_file(id):
    """File upload view (displayed as an iFrame) allows uploading files to the server."""
    if request.method == "POST":
        db = get_db()
        f = request.files['file']

        if f and allowed_file(f.filename):
            # Insert the filename into the database and return its id
            # The id will be the name of the file in the upload folder.
            type = f.filename.rsplit('.', 1)[1].lower()
            db.execute(
                "INSERT INTO files (name, type)"
                " VALUES (?, ?)",
                (f.filename, type)
            )
            db.commit()
            file_info = db.execute(
                "SELECT id, type FROM files WHERE name = ?",
                (f.filename, )
            ).fetchone()
            f.save(os.path.join(current_app.config['UPLOAD_FOLDER'], str(file_info['id'])))

            # Then add the file as a message to the shared table in the database.
            db.execute(
                "INSERT INTO shared (from_id, to_id, file_id)"
                " VALUES (?, ?, ?)",
                (g.user['id'], id, file_info['id'])
            )
            db.commit()
    return render_template("chat/upload.html")


@bp.route("/download/<int:file_id>")
@login_required
def download(file_id):
    """Link to download a file from the uploads folder."""
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], str(file_id))






