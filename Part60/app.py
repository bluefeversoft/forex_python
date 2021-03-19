from flask import Flask, jsonify
from whitenoise import WhiteNoise
import json

app = Flask(__name__)
app.wsgi_app = WhiteNoise(
    app.wsgi_app, root="static/", index_file=True, autorefresh=True
)

@app.route("/kpi_data")
def get_kpi_data():
    with open('data.json', 'r') as f:
        data = json.loads(f.read())
        return data

if __name__ == "__main__":
    app.run()
