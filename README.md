# Chat Apps with Ollama

A collection of Streamlit-based chat applications powered by Ollama LLM, designed to run in Kubernetes clusters.

## Applications

### 1. Chat App with Spotify MCP

A chat application that integrates with Ollama (LLM) and Spotify via MCP (Model Context Protocol) for music control.


## Architecture

```
┌─────────────────┐
│   Chat App      │
│   (Streamlit)   │
└────────┬────────┘
         │
         ├─────────► Ollama Service (LLM)
         │
         └─────────► Spotify MCP (WIP)
```

## Prerequisites

1. **Kubernetes Cluster** with:
   - kubectl configured
   - PersistentVolume support (for Ollama models)
   - Ingress controller (optional, for external access)

2. **Spotify API Credentials**:
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create an app
   - Set redirect URI to: `http://127.0.0.1:8080/callback`
   - Get Client ID and Client Secret

3. **Docker** and container registry access


## Local Development

### 1. Setup Environment

```bash
cd chat_app
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file or export:

```bash
export OLLAMA_BASE_URL=http://localhost:11434
```

### 3. Run Ollama Locally

```bash
# Install Ollama (if not already installed)
# Visit https://ollama.ai for installation instructions

# Pull a model
ollama pull llama3.2

# Start Ollama server
ollama serve
```

### 4. Run Chat App

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## Kubernetes Deployment

**Important**: This deployment assumes Ollama is running on your localhost (the machine running the Kubernetes cluster). The chat app will connect to it via `host.docker.internal` or host networking.

If you want to run Ollama in Kubernetes instead, you can use the commented-out Ollama resources in `k8s/` directory and update the configmap to point to the Ollama service.

### 1. Build and Push Container Images

#### Build Chat App Image

```bash
cd chat_app
docker build -t your-registry/chat-app:latest .
docker push your-registry/chat-app:latest
```

Update `k8s/deployment-chat-app.yaml` with your image:

```yaml
image: your-registry/chat-app:latest
```

### 3. Deploy to Kubernetes

Deploy all resources:

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Deploy Chat App
kubectl apply -f k8s/deployment-chat-app.yaml
kubectl apply -f k8s/service-chat-app.yaml

```

### 4. Access the Application

#### Option 1: Port Forward

```bash
kubectl port-forward -n chat-spotify service/chat-app-service 8080:80
```

Access at: `http://localhost:8080`

#### Option 2: LoadBalancer

Change service type in `k8s/service-chat-app.yaml`:

```yaml
type: LoadBalancer
```

Get external IP:

```bash
kubectl get svc -n chat-spotify chat-app-service
```

