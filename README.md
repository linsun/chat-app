# Chat Apps with Ollama

A collection of Streamlit-based chat applications powered by Ollama LLM, designed to run in Kubernetes clusters.

## Applications

### 1. Chat App with Spotify MCP
A chat application that integrates with Ollama (LLM) and Spotify via MCP (Model Context Protocol) for music control.

### 2. KubeCon NA 2025 Agenda Assistant
A chat application that helps users explore and query the KubeCon + CloudNativeCon North America 2025 schedule.

See [KUBECON_CHAT_README.md](./KUBECON_CHAT_README.md) for details.

## Features

- 💬 Chat with Ollama LLM models
- 🎵 Control Spotify playback via MCP
- 🔍 Search for tracks, albums, artists, and playlists
- ⏯️ Play, pause, skip, and queue management
- ☸️ Full Kubernetes deployment support

## Architecture

```
┌─────────────────┐
│   Chat App      │
│   (Streamlit)   │
└────────┬────────┘
         │
         ├─────────► Ollama Service (LLM)
         │
         └─────────► Spotify MCP (via stdio subprocess)
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

## Project Structure

```
.
├── chat_app/                    # Spotify MCP chat app
│   ├── app.py
│   ├── mcp_client.py
│   ├── requirements.txt
│   └── Dockerfile
├── kubecon_chat_app/            # KubeCon agenda chat app
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── k8s/                         # Kubernetes manifests
│   ├── namespace.yaml
│   ├── secret-spotify.yaml
│   ├── configmap-chat-app.yaml
│   ├── deployment-chat-app.yaml
│   ├── service-chat-app.yaml
│   ├── configmap-kubecon-chat.yaml
│   ├── deployment-kubecon-chat.yaml
│   └── service-kubecon-chat.yaml
├── deploy.sh                    # Deploy Spotify chat app
├── deploy-kubecon.sh            # Deploy KubeCon chat app
├── Makefile
├── README.md
└── KUBECON_CHAT_README.md       # KubeCon chat app docs
```

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
export SPOTIFY_CLIENT_ID=your_client_id
export SPOTIFY_CLIENT_SECRET=your_client_secret
export SPOTIFY_REDIRECT_URI=http://127.0.0.1:8080/callback
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

### 2. Configure Secrets

Update `k8s/secret-spotify.yaml` with your Spotify credentials:

```yaml
stringData:
  SPOTIFY_CLIENT_ID: "your_actual_client_id"
  SPOTIFY_CLIENT_SECRET: "your_actual_client_secret"
```

### 3. Deploy to Kubernetes

Deploy all resources:

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets (update with your credentials first!)
kubectl apply -f k8s/secret-spotify.yaml

# Create config maps
kubectl apply -f k8s/configmap-chat-app.yaml

# Create PVC for Ollama
kubectl apply -f k8s/pvc-ollama.yaml

# Deploy Ollama
kubectl apply -f k8s/deployment-ollama.yaml
kubectl apply -f k8s/service-ollama.yaml

# Deploy Chat App
kubectl apply -f k8s/deployment-chat-app.yaml
kubectl apply -f k8s/service-chat-app.yaml

# Deploy Ingress (optional)
kubectl apply -f k8s/ingress.yaml
```

### 4. Ensure Ollama is Running Locally

Make sure Ollama is installed and running on your localhost:

```bash
# Install Ollama (if not already installed)
# Visit https://ollama.ai for installation instructions

# Start Ollama server (if not running as service)
ollama serve

# Pull a model
ollama pull llama3.2
# or: ollama pull mistral
```

### 5. Access the Application

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

#### Option 3: Ingress

Update `k8s/ingress.yaml` with your domain and apply. Then access via your configured domain.

## Usage

### MCP Communication Modes

The app supports two modes for communicating with the Spotify MCP server:

#### 1. stdio Mode (Default)
- Direct subprocess communication via standard input/output
- Faster, lower overhead
- Good for production use

#### 2. HTTP Mode (For Testing with MCP Inspector)
- Runs spotify-mcp as an HTTP server using uvicorn
- Accessible at `http://localhost:8080/mcp`
- Perfect for testing with MCP Inspector

**To enable HTTP mode:**
```bash
export MCP_MODE=http
export SPOTIFY_MCP_HTTP_URL=http://localhost:8080/mcp
export SPOTIFY_MCP_HTTP_PORT=8080
```

**Using MCP Inspector:**
1. Install: `npx @modelcontextprotocol/inspector`
2. Start the chat app with HTTP mode enabled
3. In MCP Inspector, add server:
   - **Transport**: Streamable HTTP
   - **URL**: `http://localhost:8080/mcp`
4. Connect and test!

### Chat Commands

1. **Regular Chat**: Type any message to chat with Ollama
2. **Spotify Commands**: Use `/spotify` prefix:
   - `/spotify play <song/artist name>` - Play a song
   - `/spotify pause` - Pause playback
   - `/spotify resume` - Resume playback
   - `/spotify skip` - Skip to next track
   - `/spotify search <query>` - Search for music
   - `/spotify current` - Show currently playing track

### Example Interactions

```
User: Hello! Can you help me find some music?
Assistant: I'd be happy to help you find music! You can use the /spotify search command 
          to search for tracks, albums, artists, or playlists. 
          Would you like me to help you play something specific?

User: /spotify play Imagine Dragons
Assistant: ✅ Playing: Imagine Dragons

User: /spotify pause
Assistant: ⏸️ Playback paused
```

## Important Notes

### Spotify OAuth Flow

The Spotify MCP server requires OAuth authentication. On first run, it will attempt to open a browser for authentication. In Kubernetes:

1. **For Development**: Use port-forwarding to access the app, then authenticate through your local browser
2. **For Production**: Consider using a service account with pre-authenticated tokens or implementing a separate OAuth proxy service
3. **Alternative**: Pre-authenticate locally and copy tokens to the cluster (if supported by the MCP server)

The redirect URI `http://127.0.0.1:8080/callback` works when accessing via port-forward, as the app runs on your local machine's loopback interface.

## Troubleshooting

### Chat App can't connect to Ollama

**Note**: Ollama runs on your localhost, not in Kubernetes.

1. **Verify Ollama is running locally**:
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. **Check Ollama is accessible from the cluster**:
   - For Docker Desktop/kind: Uses `host.docker.internal` (default in configmap)
   - For Minikube: May need to use `host.docker.internal` or enable host network
   - For other clusters: May need to enable `hostNetwork: true` in deployment or use cluster gateway IP

3. **If host.docker.internal doesn't work**, try enabling host network:
   ```yaml
   # In deployment-chat-app.yaml, uncomment:
   hostNetwork: true
   # And update configmap to use: http://localhost:11434
   ```

4. **Check chat app logs**:
   ```bash
   kubectl logs -n chat-spotify -l app=chat-app
   ```

### Spotify MCP Connection Issues

1. Verify Spotify credentials are correct in the secret:
   ```bash
   kubectl get secret -n chat-spotify spotify-credentials -o yaml
   ```

2. Check chat app logs:
   ```bash
   kubectl logs -n chat-spotify -l app=chat-app
   ```

3. Ensure Spotify MCP repository was cloned successfully in the container

### Ollama Model Not Found

Since Ollama runs on localhost:

1. **Pull a model locally**:
   ```bash
   ollama pull llama2
   # or another model like: ollama pull mistral
   ```

2. **Verify model is available**:
   ```bash
   ollama list
   ```

3. Update the model name in `app.py` if using a different model than "llama3.2" (default)

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_BASE_URL` | Ollama service URL | `http://ollama-service:11434` |
| `SPOTIFY_CLIENT_ID` | Spotify API Client ID | Required |
| `SPOTIFY_CLIENT_SECRET` | Spotify API Client Secret | Required |
| `SPOTIFY_REDIRECT_URI` | OAuth redirect URI | `http://127.0.0.1:8080/callback` |
| `MCP_MODE` | MCP communication mode | `stdio` or `http` |
| `SPOTIFY_MCP_HTTP_URL` | HTTP endpoint URL (HTTP mode only) | `http://localhost:8080/mcp` |
| `SPOTIFY_MCP_HTTP_PORT` | HTTP server port (HTTP mode only) | `8080` |

### Resource Requirements

The default resource limits are:
- **Chat App**: 2Gi memory, 1000m CPU
- **Ollama**: 8Gi memory, 2000m CPU (adjust based on model size)

Update in deployment YAMLs as needed.

## Development

### Running Tests

```bash
cd chat_app
python -m pytest tests/  # If tests are added
```

### Local Testing with Docker

```bash
# Build image
docker build -t chat-app:local ./chat_app

# Run with environment variables
docker run -p 8501:8501 \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  -e SPOTIFY_CLIENT_ID=your_id \
  -e SPOTIFY_CLIENT_SECRET=your_secret \
  chat-app:local
```

## License

MIT

## Acknowledgments

- [Ollama](https://ollama.ai) - Local LLM runtime
- [Spotify MCP](https://github.com/varunneal/spotify-mcp) - Spotify integration
- [Streamlit](https://streamlit.io) - Web app framework

