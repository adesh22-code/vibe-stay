import os
import base64
import json
import requests


GITHUB_OWNER = "adesh22-code"
GITHUB_REPO = "vibe-stay"
GITHUB_FILE_PATH = "docs/data.json"
GITHUB_BRANCH = "main"


def get_github_headers():
    token = os.environ.get("GITHUB_TOKEN")

    if not token:
        raise RuntimeError("GITHUB_TOKEN is not set")

    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }


def get_data():
    url = (
        f"https://api.github.com/repos/"
        f"{GITHUB_OWNER}/{GITHUB_REPO}/contents/"
        f"{GITHUB_FILE_PATH}?ref={GITHUB_BRANCH}"
    )

    response = requests.get(
        url,
        headers=get_github_headers()
    )

    response.raise_for_status()

    github_file = response.json()

    content = base64.b64decode(
        github_file["content"]
    ).decode("utf-8")

    data = json.loads(content)

    return data
