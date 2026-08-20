from flask import Flask, render_template, jsonify, request

from services.github_service import get_data, get_file, update_data


app = Flask(__name__)


@app.route("/")
def admin():
    return render_template("admin.html")


@app.route("/api/homestays")
def homestays():
    data = get_data()
    return jsonify(data)


@app.route("/api/homestays/<homestay_id>", methods=["PUT"])
def update_homestay(homestay_id):

    updated_homestay = request.get_json()

    if not updated_homestay:
        return jsonify({
            "success": False,
            "message": "No data received"
        }), 400

    # Get the current REAL data from GitHub
    data, sha = get_file()

    # Find the homestay
    found = False

    for index, homestay in enumerate(data):

        if str(homestay.get("id")) == str(homestay_id):

            # Preserve the existing record structure
            data[index] = updated_homestay

            found = True
            break

    if not found:
        return jsonify({
            "success": False,
            "message": f"Homestay {homestay_id} not found"
        }), 404

    # Update the REAL docs/data.json on GitHub
    update_data(data, sha)

    return jsonify({
        "success": True,
        "message": "Homestay updated successfully",
        "homestay": updated_homestay
    })


if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )
