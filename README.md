# Docker rm WEBHOOK

## Description

This is a simple webhook that listens for POST requests and runs a shell script. It is intended to be used in a Docker container.

## Usage

### BUILD

### Set the environment variables

```bash
export WEBHOOK_SECRET=secret
```

### Build the Docker image

```bash
docker build -t webhook .
```

### Or get them from github docker registry
    
```bash
docker pull ghcr.io/danildzambrana/docker-webhook:main
```

### Run the Docker container

```bash
docker run -p 5030:80 --privileged --name webhook -v /var/run/docker.sock:/var/run/docker.sock webhook  uvicorn main:app --host 0.0.0.0 --port 80
``` 
or you can run the compose file [compose.yml](compose.yml) with the following command:
```bash
docker-compose up -d
```

### Test the webhook

```bash
curl -X POST http://localhost:5030/webhook
```

### Configure the webhook on github
1. Go to the repository settings
2. Click on Webhooks
3. Click on Add webhook
4. Set the Payload URL to http://localhost:5030/webhook
5. Set the Content type to application/json
6. Set the Secret to the value of the environment variable WEBHOOK_SECRET
7. Select the event DELETE in the events section
8. Click on Add webhook
9. Delete a branch in the repository
10. Check the logs of the webhook container
11. The webhook should have received the POST request and executed the shell script
12. The branch should have been deleted

### Stop the Docker container

```bash
docker stop webhook
```

### Remove the Docker container

```bash
docker rm webhook
```

