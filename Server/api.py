from flask import Flask, render_template
from Server.protocol import *

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("./index.html",message="Hello, World!")





if __name__ == "__main__":
    app.run(debug=True)

def run_api(host: str, port: int) -> None:
    app.run(host=host,
            port=port
            )