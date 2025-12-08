from app import create_app


def run():
    app = create_app()
    app.run("127.0.0.1",5050)


if __name__ == "__main__":
    app = create_app()
    app.run("0.0.0.0",5050,debug=True)