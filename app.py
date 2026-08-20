from flask import Flask, render_template, jsonify

from services.github_service import get_data


app = Flask(__name__)


@app.route("/")
def admin():
    return render_template("admin.html")


@app.route("/api/homestays")
def homestays():
    data = get_data()
    return jsonify(data)


if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )
