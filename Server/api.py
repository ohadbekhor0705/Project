from flask import Flask, render_template
from protocol import *


app = Flask(__name__)


@app.route("/")
def home() -> str:
    return render_template("./index.html",message="Hello, World!")


@app.route("/Login")
def Login():
    ...

@app.route("/handle_login", methods=["POST"])
def handle_login(username: str, password: str):
    ...


@app.route("/Register")
def Register():
    ...

@app.route("/handle_register", methods=["POST"])
def handle_login(username: str, password: str):
    ...

@app.route("/files")
def Files():
    ...


@app.route("/file_viewer//<str: file_id>")
def file_viewer(file_id: str) -> str:
    ...


if __name__ == "__main__":
    app.run(debug=True)

def run_api(host: str, port: int) -> None:
    global app
    app.run(host=host, port=port)