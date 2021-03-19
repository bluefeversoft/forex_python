from flask import Flask, jsonify
from whitenoise import WhiteNoise

app = Flask(__name__)
app.wsgi_app = WhiteNoise(
    app.wsgi_app, root="static/", index_file=True, autorefresh=True
)

if __name__ == "__main__":
    app.run()
