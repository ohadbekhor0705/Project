from app import create_app

PORT = 8843

def run():
    app = create_app()
    app.run("127.0.0.1",PORT)


if __name__ == "__main__":
    app = create_app()
    app.run("0.0.0.0",PORT,debug=True,ssl_context='adhoc')