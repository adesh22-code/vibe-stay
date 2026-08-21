import os

# Set environment variables for ImageKit
os.environ["IMAGEKIT_PRIVATE_KEY"] = "private_CYRHDBDLYGDNy/Ejc/+ceyKVL+E="
                                      
os.environ["IMAGEKIT_URL_ENDPOINT"] = "https://ik.imagekit.io/vibestay"

from flask import Flask, render_template, jsonify, request
from services.github_service import get_data, get_file, update_data
from services.imagekit_service import (
    upload_image,
    find_file_by_url,
    delete_image
)

app = Flask(__name__)

@app.route("/api/homestays", methods=["POST"])
def add_homestay():
    new_homestay = request.get_json()

    if not new_homestay:
        return jsonify({"success": False, "message": "No data received"}), 400

    data, sha = get_file()

    # Find the highest existing ID to create the next one
    max_id = 0
    for homestay in data:
        try:
            current_id = int(homestay.get("id", 0))
            if current_id > max_id:
                max_id = current_id
        except ValueError:
            pass

    new_id = str(max_id + 1)
    
    # Structure the new record
    editable_fields = [
        "name", "location", "price", "scenery", "amenities",
        "description", "phone", "whatsapp", "facebook",
        "website", "youtube", "instagram", "googleMap",
        "gallery", "image"
    ]

    final_homestay = {"id": new_id}
    for field in editable_fields:
        final_homestay[field] = new_homestay.get(field, "")

    data.append(final_homestay)

    try:
        update_data(data, sha)
    except Exception as error:
        print("GitHub add error:", error)
        return jsonify({"success": False, "message": "Unable to update GitHub"}), 500

    return jsonify({
        "success": True,
        "message": "Homestay added successfully",
        "homestay": final_homestay
    })



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

    data, sha = get_file()
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

    editable_fields = [
        "name", "location", "price", "scenery", "amenities",
        "description", "phone", "whatsapp", "facebook",
        "website", "youtube", "instagram", "googleMap",
        "gallery", "image"
    ]

    for field in editable_fields:
        if field in updated_homestay:
            existing_homestay[field] = updated_homestay[field]

    existing_homestay["id"] = str(homestay_id)
    data[existing_index] = existing_homestay

    try:
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

    def match_url(db_url, target_url):
        if not db_url: return False
        return db_url == target_url or target_url.endswith(db_url) or db_url.endswith(target_url)

    try:
        github_data, sha = get_file()
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

        affected_records = []

        for homestay in github_data:
            if match_url(homestay.get("image"), image_url):
                affected_records.append(homestay)

            gallery = homestay.get("gallery", "")
            gallery_urls = [url.strip() for url in gallery.split("|") if url.strip()]

            for g_url in gallery_urls:
                if match_url(g_url, image_url):
                    if homestay not in affected_records:
                        affected_records.append(homestay)
                    break

        if not affected_records:
            return jsonify({
                "success": False,
                "message": "Image URL is not present in data.json. Nothing was deleted."
            }), 404

        for homestay in affected_records:
            if match_url(homestay.get("image"), image_url):
                homestay["image"] = ""

            gallery = homestay.get("gallery", "")
            gallery_urls = [
                url.strip()
                for url in gallery.split("|")
                if url.strip() and not match_url(url.strip(), image_url)
            ]
            homestay["gallery"] = "|".join(gallery_urls)

        delete_image(file_id)

        try:
            update_data(github_data, sha)
        except Exception as github_error:
            print("GitHub update failed after ImageKit deletion:", github_error)
            return jsonify({
                "success": False,
                "message": "Image deleted from ImageKit, but GitHub update failed.",
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
        print("Image deletion error:", error)
        return jsonify({
            "success": False,
            "message": "Image deletion failed. Nothing was confirmed as deleted."
        }), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
