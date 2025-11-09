# Chat App Helm Chart

A Helm chart for deploying the Chat App with music voting functionality on Kubernetes.

## Installation

### Add the Helm repository (if published)

```bash
helm repo add chat-app https://linsun.github.io/chat-app-charts
helm repo update
```

### Install the chart

```bash
helm install my-chat-app ./charts/chat-app
```

Or with custom values:

```bash
helm install my-chat-app ./charts/chat-app -f my-values.yaml
```

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
| `namespace` | Namespace to deploy to (must exist) | `music` |
| `persistence.enabled` | Enable persistent volume for shared database | `true` |
| `persistence.size` | Size of persistent volume | `1Gi` |
| `persistence.storageClass` | Storage class (empty for default) | `""` |
| `persistence.accessMode` | Access mode (ReadWriteMany for multiple replicas) | `ReadWriteMany` |
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

**Yes, Streamlit works with multiple replicas!** The chart is configured to support multiple replicas by default:

- A PersistentVolume is automatically created to share the SQLite database across all replicas
- The volume uses `ReadWriteMany` access mode so all pods can access it simultaneously
- SQLite is configured with WAL (Write-Ahead Logging) mode for better concurrency

To deploy with 3 replicas:
```bash
helm install my-chat-app ./charts/chat-app --set replicaCount=3
```

**Note:** Your Kubernetes cluster must support `ReadWriteMany` volumes. If your storage class doesn't support it, you may need to:
- Use a different storage class that supports ReadWriteMany (e.g., NFS, CephFS)
- Or set `persistence.enabled: false` and use only 1 replica

## Usage Example

**Note:** The namespace must exist before installing the chart. Create it with:
```bash
kubectl create namespace music
```

```yaml
# custom-values.yaml
replicaCount: 3
namespace: my-namespace
image:
  repository: myregistry/chat-app
  tag: "v3"
service:
  type: LoadBalancer
persistence:
  enabled: true
  size: 2Gi
  storageClass: "nfs-client"  # Use a storage class that supports ReadWriteMany
env:
  - name: OLLAMA_BASE_URL
    value: "http://ollama-service:11434"
```

Then install:
```bash
helm install my-chat-app ./charts/chat-app -f custom-values.yaml
```

