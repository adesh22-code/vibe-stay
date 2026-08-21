import os
import requests
from urllib.parse import urlparse, unquote


IMAGEKIT_API_URL = "https://api.imagekit.io/v1"


def get_private_key():
    print("SERVICE sees IMAGEKIT_PRIVATE_KEY:",
          "YES" if os.environ.get("IMAGEKIT_PRIVATE_KEY") else "NO")

    private_key = os.environ.get("IMAGEKIT_PRIVATE_KEY")

    if not private_key:
        raise RuntimeError("IMAGEKIT_PRIVATE_KEY is not set")

    return private_key


def imagekit_request(method, url, **kwargs):
    """
    Make an authenticated ImageKit API request.
    """

    return requests.request(
        method,
        url,
        auth=(get_private_key(), ""),
        timeout=60,
        **kwargs
    )


def upload_image(file_data, file_name, folder="/vibestay"):

    url = f"{IMAGEKIT_API_URL}/files/upload"

    files = {
        "file": (file_name, file_data)
    }

    data = {
        "fileName": file_name,
        "folder": folder,
        "useUniqueFileName": "true"
    }

    response = imagekit_request(
        "POST",
        url,
        files=files,
        data=data
    )

    if not response.ok:
        print("ImageKit upload status:", response.status_code)
        print("ImageKit upload response:", response.text)
        print(
            "ImageKit request ID:",
            response.headers.get("x-ik-requestId")
        )

    response.raise_for_status()

    return response.json()


def delete_image(file_id):

    url = f"{IMAGEKIT_API_URL}/files/{file_id}"

    response = imagekit_request(
        "DELETE",
        url
    )

    if not response.ok:
        print("ImageKit delete status:", response.status_code)
        print("ImageKit delete response:", response.text)
        print(
            "ImageKit request ID:",
            response.headers.get("x-ik-requestId")
        )

    response.raise_for_status()

    return response.json() if response.content else {}


def find_file_by_url(image_url):

    if not image_url:
        return None

    parsed = urlparse(image_url)

    path = unquote(parsed.path)

    print("ImageKit delivery URL path:", path)

    # Expected URL:
    #
    # /vibestay/vibestay/photo.jpg
    #
    # First "vibestay" = URL endpoint
    # Second "vibestay" = Media Library folder
    #
    # Therefore actual ImageKit filePath:
    #
    # /vibestay/photo.jpg

    prefix = "/vibestay/"

    if not path.startswith(prefix):
        return None

    file_path = path[len(prefix):]

    # Add the Media Library folder.
    file_path = "/vibestay/" + file_path

    print("Searching ImageKit filePath:", file_path)

    url = f"{IMAGEKIT_API_URL}/files"

    response = imagekit_request(
        "GET",
        url,
        params={
            "path": "/vibestay"
        }
    )

    if not response.ok:
        print("ImageKit search status:", response.status_code)
        print("ImageKit search response:", response.text)
        print(
            "ImageKit request ID:",
            response.headers.get("x-ik-requestId")
        )

    response.raise_for_status()

    files = response.json()

    if isinstance(files, list):

        for image_file in files:

            if image_file.get("filePath") == file_path:
                return image_file

    return None
