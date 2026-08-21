import os
import requests


IMAGEKIT_API_URL = "https://api.imagekit.io/v1"


def get_private_key():
    private_key = os.environ.get("IMAGEKIT_PRIVATE_KEY")

    if not private_key:
        raise RuntimeError("IMAGEKIT_PRIVATE_KEY is not set")

    return private_key


def upload_image(file_data, file_name, folder):
    url = f"{IMAGEKIT_API_URL}/files/upload"

    files = {
        "file": (file_name, file_data)
    }

    data = {
        "fileName": file_name,
        "folder": folder,
        "useUniqueFileName": "true"
    }

    response = requests.post(
        url,
        auth=(get_private_key(), ""),
        files=files,
        data=data
    )

    response.raise_for_status()

    return response.json()


def delete_image(file_id):
    url = f"{IMAGEKIT_API_URL}/files/{file_id}"

    response = requests.delete(
        url,
        auth=(get_private_key(), "")
    )

    response.raise_for_status()

    return response.json() if response.content else {}


def find_file_by_url(image_url):
    """
    Find an ImageKit file using the path contained in its delivery URL.
    """

    from urllib.parse import urlparse, unquote

    parsed = urlparse(image_url)

    path = unquote(parsed.path)

    # Example:
    # /vibestay/vibestay/photo.webp
    #
    # We need the ImageKit file path:
    # /vibestay/photo.webp

    if "/vibestay/" not in path:
        return None

    file_path = "/" + path.split("/vibestay/", 1)[1]

    url = f"{IMAGEKIT_API_URL}/files"

    response = requests.get(
        url,
        auth=(get_private_key(), ""),
        params={
            "path": file_path
        }
    )

    response.raise_for_status()

    files = response.json()

    if isinstance(files, list):
        for image_file in files:

            if image_file.get("filePath") == file_path:
                return image_file

    return None
