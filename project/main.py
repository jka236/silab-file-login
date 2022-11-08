from flask import Blueprint, render_template, redirect, flash, request, session, url_for
from .auth import login_required
import json
from werkzeug.utils import secure_filename
import os
import subprocess

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/myinfo")
@login_required
def myinfo():
    f = open("project/user.json")
    data = json.load(f)
    username = session["username"]
    return render_template("myinfo.html", name=username, email=data[username]["email"])


@main.route("/monitoring")
def monitoring():
    return render_template("monitoring.html")


@main.route("/file_upload", methods=["POST"])
def upload_file():
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("No file selected for uploading")
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join("./upload_file", filename))
            flash("File successfully uploaded")
            return redirect("/file_upload")
        else:
            flash("File Upload failed")
            return redirect(request.url)


@main.route("/file_upload")
def upload_form():
    file_name = (
        subprocess.Popen("ls upload_file", shell=True, stdout=subprocess.PIPE)
        .stdout.read()
        .decode("utf-8")
        .split("\n")
    )

    attributes = (
        subprocess.Popen("ls -l upload_file", shell=True, stdout=subprocess.PIPE)
        .stdout.read()
        .decode("utf-8")
        .split("\n")[1:]
    )

    file_att_dict = {}
    for i in range(len(file_name) - 1):
        file_att_dict[file_name[i]] = attributes[i]

    return render_template("upload.html", files=file_att_dict)


@main.route("/file_upload/<file_name>")
def remove_file(file_name):
    file_path = "./upload_file/" + file_name
    os.remove(file_path)

    return redirect(url_for("main.upload_form"))
