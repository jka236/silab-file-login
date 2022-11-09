from flask import (
    Blueprint,
    render_template,
    redirect,
    flash,
    request,
    session,
    url_for,
    send_from_directory,
)
from .auth import login_required
import json
from werkzeug.utils import secure_filename
import os
import subprocess
import stat


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


@main.route("/download/<file_name>")
def download_file(file_name):
    cwd = os.getcwd()
    path = os.path.join(cwd, "upload_file")
    return send_from_directory(path, file_name, as_attachment=True)


@main.route("/att_update/<file_name>", methods=["POST"])
def att_update(file_name):
    update = request.form.get("update")
    file_path = "./upload_file/" + file_name
    update = perm2mask(update)
    if type(update) == str:
        flash({file_name:update})
    else:
        os.chmod(file_path, update)
        flash({file_name:'success'})

    return redirect(url_for("main.upload_form"))


def perm2mask(p):

    if len(p) != 9:
        return "Bad permission length"
    if not all(p[k] in "rw-" for k in [0, 1, 3, 4, 6, 7]):
        return "Bad permission format (read-write)"

    if not all(p[k] in "xs-" for k in [2, 5]):
        return "Bad permission format (execute)"
        
    if not p[8] in "xt-":
        return "Bad permission format (execute other)"

    m = 0

    if p[0] == "r":
        m |= stat.S_IRUSR
    if p[1] == "w":
        m |= stat.S_IWUSR
    if p[2] == "x":
        m |= stat.S_IXUSR
    if p[2] == "s":
        m |= stat.S_IXUSR | stat.S_ISUID

    if p[3] == "r":
        m |= stat.S_IRGRP
    if p[4] == "w":
        m |= stat.S_IWGRP
    if p[5] == "x":
        m |= stat.S_IXGRP
    if p[5] == "s":
        m |= stat.S_IXGRP | stat.S_ISGID

    if p[6] == "r":
        m |= stat.S_IROTH
    if p[7] == "w":
        m |= stat.S_IWOTH
    if p[8] == "x":
        m |= stat.S_IXOTH
    if p[8] == "t":
        m |= stat.S_IXOTH | stat.S_ISVTX

    return m
