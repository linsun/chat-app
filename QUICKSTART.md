# Quick Start Guide

Get your chat app with Ollama and Spotify running in Kubernetes quickly.

## Prerequisites

- Kubernetes cluster with kubectl configured
- Docker for building images
- Spotify API credentials

## Step 1: Get Spotify API Credentials

1. Go to https://developer.spotify.com/dashboard
2. Create a new app
3. Add redirect URI: `http://127.0.0.1:8080/callback`
4. Copy Client ID and Client Secret

## Step 2: Configure Secrets

Edit `k8s/secret-spotify.yaml`:

```yaml
stringData:
  SPOTIFY_CLIENT_ID: "your_actual_client_id_here"
  SPOTIFY_CLIENT_SECRET: "your_actual_client_secret_here"
```

## Step 3: Update Image Registry

Edit `k8s/deployment-chat-app.yaml` and update the image:

```yaml
image: your-registry/chat-app:latest
```

## Step 4: Build and Push (or use local registry)

```bash
# Option 1: Build and push to your registry
make build push

# Option 2: Use kind/minikube local registry
# For kind: kind load docker-image chat-app:latest
# For minikube: eval $(minikube docker-env) && make build
```

## Step 5: Deploy

```bash
# Use the deployment script
./deploy.sh

# Or use make
make deploy
```

## Step 6: Setup Ollama Locally

Ensure Ollama is running on your localhost:

```bash
# Install Ollama (if not already)
# Visit https://ollama.ai

# Start Ollama
ollama serve

# Pull a model
ollama pull llama3.2
```

**Note**: The chat app in Kubernetes will connect to your local Ollama via `host.docker.internal:11434`

## Step 7: Access the App

```bash
# Port forward
make port-forward

# Or manually:
kubectl port-forward -n chat-spotify service/chat-app-service 8080:80
```

Open http://localhost:8080 in your browser.

## Step 8: Use the App

1. Click "Connect Spotify MCP" in the sidebar
2. Start chatting with Ollama
3. Use Spotify commands:
   - `/spotify play Imagine Dragons`
   - `/spotify pause`
   - `/spotify skip`
   - `/spotify search jazz`

## Troubleshooting

### Check status
```bash
make status
```

### View logs
```bash
make logs-chat    # Chat app logs
make logs-ollama  # Ollama logs
```

### Restart pods
```bash
kubectl rollout restart deployment/chat-app -n chat-spotify
kubectl rollout restart deployment/ollama -n chat-spotify
```

### Clean up
```bash
make undeploy
```

## Common Issues

**Issue**: Chat app can't connect to Ollama
- **Fix**: Wait for Ollama pod to be ready, check service exists

**Issue**: Spotify MCP fails to connect
- **Fix**: Verify credentials in secret, check chat app logs

**Issue**: Ollama model not found
- **Fix**: Run `make init-ollama` to pull a model

## Next Steps

- Configure Ingress for external access
- Adjust resource limits based on your cluster
- Set up monitoring and logging
- Add custom Ollama models

