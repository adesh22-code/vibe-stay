from flask import Flask, render_template, jsonify, request

from services.github_service import get_data, get_file, update_data

from services.imagekit_service import upload_image, find_file_by_url


app = Flask(__name__)



@app.route("/api/images/upload", methods=["POST"])
def upload_image_api():

    if "file" not in request.files:
        return jsonify({
            "success": False,
            "message": "No image file received"
        }), 400

    file = request.files["file"]

    if not file.filename:
        return jsonify({
            "success": False,
            "message": "No image selected"
        }), 400

    folder = request.form.get("folder", "/vibestay")

    try:

        result = upload_image(
            file_data=file.stream,
            file_name=file.filename,
            folder=folder
        )

        return jsonify({
            "success": True,
            "url": result.get("url"),
            "fileId": result.get("fileId"),
            "name": result.get("name")
        })

    except Exception as error:

        print("ImageKit upload error:", error)

        return jsonify({
            "success": False,
            "message": "Image upload failed"
        }), 500


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

    # Always fetch the latest version from GitHub.
    # This prevents us from editing an old local copy.
    data, sha = get_file()

    # Find the existing record.
    existing_homestay = None
    existing_index = None

    for index, homestay in enumerate(data):

        if str(homestay.get("id")) == str(homestay_id):
            existing_homestay = homestay
            existing_index = index
            break

    if existing_homestay is None:
        return jsonify({
            "success": False,
            "message": f"Homestay {homestay_id} not found"
        }), 404

    # Only fields controlled by our current edit form.
    editable_fields = [
        "name",
        "location",
        "price",
        "scenery",
        "amenities",
        "description",
        "phone",
        "whatsapp",
        "facebook",
        "website",
        "youtube",
        "instagram",
        "googleMap",
        "gallery",
        "image"
    ]

    # Update only those fields.
    # Any other existing fields remain untouched.
    for field in editable_fields:

        if field in updated_homestay:
            existing_homestay[field] = updated_homestay[field]

    # Never allow the ID to be changed through the edit form.
    existing_homestay["id"] = str(homestay_id)

    # Put the modified record back into the original array.
    data[existing_index] = existing_homestay

    try:

        # Commit the updated REAL data.json to GitHub.
        update_data(data, sha)

    except Exception as error:

        print("GitHub update error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to update data.json on GitHub"
        }), 500

    return jsonify({
        "success": True,
        "message": "Homestay updated successfully",
        "homestay": existing_homestay
    })


@app.route("/api/images/info", methods=["POST"])
def image_info():

    data = request.get_json()

    if not data or not data.get("url"):
        return jsonify({
            "success": False,
            "message": "Image URL is required"
        }), 400

    image_url = data["url"]

    try:

        image_file = find_file_by_url(image_url)

        if not image_file:
            return jsonify({
                "success": False,
                "message": "Image not found in ImageKit"
            }), 404

        return jsonify({
            "success": True,
            "fileId": image_file.get("fileId"),
            "url": image_file.get("url"),
            "name": image_file.get("name"),
            "filePath": image_file.get("filePath")
        })

    except Exception as error:

        print("ImageKit lookup error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to find image in ImageKit"
        }), 500





if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )
