# Chat App Helm Chart

A Helm chart for deploying the Chat App with music voting functionality on Kubernetes.

## Installation

### Add the Helm repository (if published)

```bash
helm repo add chat-app https://linsun.github.io/chat-app-charts
helm repo update
```

### Install the chart

**First, update dependencies** (downloads the Redis subchart):
```bash
cd charts/chat-app
helm dependency update
cd ../..
```

Then install:
```bash
helm install my-chat-app ./charts/chat-app -n <namespace>
```

Or with custom values:

```bash
helm install my-chat-app ./charts/chat-app -n <namespace> -f my-values.yaml
```

**Note:** Redis is automatically deployed as a subchart when you install. The Redis deployment and service are created by the Bitnami Redis Helm chart, not manually.

## Configuration

The following table lists the configurable parameters and their default values:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Container image repository | `linsun/chat-app` |
| `image.tag` | Container image tag | `v2` |
| `image.pullPolicy` | Image pull policy | `Always` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `80` |
| `service.targetPort` | Container port | `8501` |
| `redis.enabled` | Enable Redis for vote counting (shared across replicas) | `true` |
| `redis.auth.enabled` | Enable Redis authentication | `false` |
| `env` | Environment variables | See values.yaml |
| `resources` | Resource requests/limits | See values.yaml |

## Publishing the Chart

### Option 1: GitHub Pages (Easiest for Public Repos)

1. Create a separate repository for charts (e.g., `chat-app-charts`)
2. Package the chart:
   ```bash
   helm package charts/chat-app
   ```
3. Create an index:
   ```bash
   helm repo index . --url https://linsun.github.io/chat-app-charts
   ```
4. Push to GitHub Pages branch

### Option 2: OCI Registry (Docker Hub, GHCR, etc.)

```bash
# Login to registry
helm registry login <registry-url>

# Package and push
helm package charts/chat-app
helm push chat-app-0.1.0.tgz oci://<registry-url>/charts
```

### Option 3: Artifact Hub

Publish to Artifact Hub by:
1. Creating a GitHub release with the packaged chart
2. Adding your repository to Artifact Hub
3. Artifact Hub will automatically index your charts

## Multiple Replicas

**Yes, Streamlit works with multiple replicas!** The chart uses **Redis** for shared vote counting, which works perfectly with multiple replicas:

- **Redis** is automatically deployed as a subchart (Bitnami Redis)
- All replicas connect to the same Redis instance for shared vote counts
- No persistent volumes needed - Redis handles shared state in memory
- Works on any Kubernetes cluster (including kind)

### Deploy with Multiple Replicas

To deploy with 3 replicas:
```bash
helm install my-chat-app ./charts/chat-app --namespace default --set replicaCount=3
```

**That's it!** Redis will be automatically deployed and all replicas will share vote counts.

### Redis Configuration

By default, Redis runs without authentication and persistence (data in memory). For production:

```bash
helm install my-chat-app ./charts/chat-app -n music \
  --set replicaCount=3 \
  --set redis.auth.enabled=true \
  --set redis.master.persistence.enabled=true
```

**Note:** 
- Redis data is stored in memory by default (fast, but lost on restart)
- Enable `redis.master.persistence.enabled=true` for data persistence
- Enable `redis.auth.enabled=true` for production security

## Usage Example

**Note:** The namespace must exist before installing the chart. Create it with:
```bash
kubectl create namespace music
```

```yaml
# custom-values.yaml
replicaCount: 3
image:
  repository: myregistry/chat-app
  tag: "v3"
service:
  type: LoadBalancer
env:
  - name: OLLAMA_BASE_URL
    value: "http://ollama-service:11434"
```

Then install:
```bash
helm install my-chat-app ./charts/chat-app -n music -f custom-values.yaml
```

