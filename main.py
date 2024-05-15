from fastapi import FastAPI, HTTPException, Request
from urllib.parse import unquote
import json
import subprocess
import os
from hmac import compare_digest, new
from hashlib import sha1

app = FastAPI(docs_url=None, redoc_url=None)

SECRET = os.getenv('WEBHOOK_SECRET')


def remove_docker_container_if_exists(name: str) -> bool:
    """
    Remove a docker container if it exists
    :param name: the name of the container
    :return: True if the container was removed, False otherwise
    """
    result = subprocess.run(['docker', 'ps', '-a', '-q', '--filter', f'name={name}'], stdout=subprocess.PIPE)
    containers = result.stdout.decode('utf-8').splitlines()

    if containers:
        subprocess.run(['docker', 'stop', name])
        subprocess.run(['docker', 'rm', '-f', name])
        return True
    else:
        return False


def getName(repo, branch):
    """
    Get the name of the container based on the repo and branch name
    :param repo: the repo name
    :param branch: the branch name
    :return: the name of the container in lowercase with the format {repo}_{branch} and spaces replaced by underscores
    """
    return f"{repo}_{branch}".replace(" ", "_").lower()


@app.post("/webhook")
async def github_webhook(request: Request):
    body = await request.body()
    decoded_body = unquote(body.decode())
    event = json.loads(decoded_body.replace('payload=', '', 1))

    signature_header = request.headers.get("X-Hub-Signature")
    if not signature_header:
        raise HTTPException(status_code=400, detail="Invalid signature")

    _, signature = signature_header.split('=')
    mac = new(bytes(SECRET, 'utf-8'), msg=body, digestmod=sha1)
    expected_signature = mac.hexdigest()

    if not compare_digest(signature, expected_signature):
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_header = request.headers.get("X-GitHub-Event")

    if event_header == "delete" and 'ref' in event:
        name = getName(event['repository']['name'], event['ref'])
        if remove_docker_container_if_exists(name):
            return {"message": f"Webhook received - Container {name} removed", "status": 200}
        else:
            return {"message": f"Webhook received - Can't remove the container {name}", "status": 200}

    return {"message": "Webhook received", "status": 200}
