import os

os.environ["IMAGEKIT_PRIVATE_KEY"] = "private_xxxxxxxxxxxxxxxxx"
os.environ["IMAGEKIT_URL_ENDPOINT"] = "https://ik.imagekit.io/vibestay"

from flask import Flask, render_template, jsonify, request

from services.github_service import get_data, get_file, update_data

from services.imagekit_service import (
    upload_image,
    find_file_by_url,
    delete_image
)


app = Flask(__name__)

os.environ["IMAGEKIT_PRIVATE_KEY"] = "private_CYRHDBDLYGDNY/Ejc/+ceyKVL+E="
os.environ["IMAGEKIT_URL_ENDPOINT"] = "https://ik.imagekit.io/vibestay"



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



@app.route("/api/images/delete", methods=["POST"])
def delete_image_api():

    data = request.get_json()

    if not data or not data.get("url"):
        return jsonify({
            "success": False,
            "message": "Image URL is required"
        }), 400

    image_url = data["url"]

    try:
        # 1. Get the latest REAL data.json from GitHub
        github_data, sha = get_file()

        # 2. Find the image in ImageKit
        image_file = find_file_by_url(image_url)

        if not image_file:
            return jsonify({
                "success": False,
                "message": "Image was not found in ImageKit. Nothing was deleted."
            }), 404

        file_id = image_file.get("fileId")

        if not file_id:
            return jsonify({
                "success": False,
                "message": "ImageKit file ID was not found. Nothing was deleted."
            }), 500

        # 3. Find the image in our REAL data.json
        affected_records = []

        for homestay in github_data:

            # Main/profile image
            if homestay.get("image") == image_url:
                affected_records.append(homestay)

            # Gallery images
            gallery = homestay.get("gallery", "")

            gallery_urls = [
                url.strip()
                for url in gallery.split("|")
                if url.strip()
            ]

            if image_url in gallery_urls:
                if homestay not in affected_records:
                    affected_records.append(homestay)

        if not affected_records:
            return jsonify({
                "success": False,
                "message": "Image URL is not present in data.json. Nothing was deleted."
            }), 404

        # 4. Prepare the modified JSON
        for homestay in affected_records:

            if homestay.get("image") == image_url:
                homestay["image"] = ""

            gallery = homestay.get("gallery", "")

            gallery_urls = [
                url.strip()
                for url in gallery.split("|")
                if url.strip() and url.strip() != image_url
            ]

            homestay["gallery"] = "|".join(gallery_urls)

        # 5. Delete from ImageKit
        delete_image(file_id)

        # 6. Update GitHub with the modified JSON
        try:

            update_data(github_data, sha)

        except Exception as github_error:

            print("GitHub update failed after ImageKit deletion:")
            print(github_error)

            return jsonify({
                "success": False,
                "message": (
                    "Image was deleted from ImageKit, "
                    "but GitHub update failed. "
                    "The URL may still exist in data.json."
                ),
                "imageDeleted": True,
                "githubUpdated": False
            }), 500

        return jsonify({
            "success": True,
            "message": "Image deleted successfully",
            "imageDeleted": True,
            "githubUpdated": True,
            "fileId": file_id,
            "url": image_url
        })

    except Exception as error:

        print("Image deletion error:")
        print(error)

        return jsonify({
            "success": False,
            "message": "Image deletion failed. Nothing was confirmed as deleted."
        }), 500





if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )
