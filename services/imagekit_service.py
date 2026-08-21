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
    Find an ImageKit file using its exact URL.
    Returns the ImageKit file information or None.
    """

    url = f"{IMAGEKIT_API_URL}/files"

    response = requests.get(
        url,
        auth=(get_private_key(), ""),
        params={
            "searchQuery": f'url:"{image_url}"'
        }
    )

    response.raise_for_status()

    files = response.json()

    for image_file in files:

        if image_file.get("url") == image_url:
            return image_file

    return None
