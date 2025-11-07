# Publishing Your Helm Chart

This guide covers the **easiest ways** to publish your Helm chart so others can install it.

## 🚀 Option 1: GitHub Pages (Recommended - Easiest)

This is the simplest method for public repositories and doesn't require any external services.

### Step 1: Create a Charts Repository

Create a new GitHub repository (e.g., `chat-app-charts`) or use an existing one.

### Step 2: Package and Index Your Chart

```bash
cd charts

# Package the chart
helm package chat-app

# Create index (first time)
helm repo index . --url https://YOUR_USERNAME.github.io/chat-app-charts

# Or update existing index
helm repo index . --url https://YOUR_USERNAME.github.io/chat-app-charts --merge index.yaml
```

### Step 3: Push to GitHub Pages

```bash
# Initialize git if needed
git init
git checkout -b gh-pages

# Add files
git add chat-app-*.tgz index.yaml
git commit -m "Add chart version 0.1.0"
git remote add origin https://github.com/YOUR_USERNAME/chat-app-charts.git
git push -u origin gh-pages
```

### Step 4: Enable GitHub Pages

1. Go to your repository settings
2. Navigate to "Pages"
3. Set source to `gh-pages` branch
4. Save

### Step 5: Use Your Chart

```bash
# Add your repo
helm repo add chat-app https://YOUR_USERNAME.github.io/chat-app-charts
helm repo update

# Install
helm install my-chat-app chat-app/chat-app
```

## 🐳 Option 2: OCI Registry (Docker Hub / GHCR)

Works with any OCI-compatible registry (Docker Hub, GitHub Container Registry, etc.)

### Using GitHub Container Registry (GHCR)

```bash
# Login to GHCR
echo $GITHUB_TOKEN | helm registry login ghcr.io -u YOUR_USERNAME --password-stdin

# Package and push
helm package charts/chat-app
helm push chat-app-0.1.0.tgz oci://ghcr.io/YOUR_USERNAME/helm-charts
```

### Using Docker Hub

```bash
# Login
helm registry login registry-1.docker.io -u YOUR_USERNAME

# Package and push
helm package charts/chat-app
helm push chat-app-0.1.0.tgz oci://registry-1.docker.io/YOUR_USERNAME
```

### Install from OCI

```bash
helm install my-chat-app oci://ghcr.io/YOUR_USERNAME/helm-charts/chat-app --version 0.1.0
```

## 📦 Option 3: Artifact Hub

Artifact Hub automatically indexes Helm charts from various sources.

### Steps:

1. **Publish your chart** using one of the methods above (GitHub Pages or OCI)
2. **Add your repository** to Artifact Hub:
   - Go to https://artifacthub.io
   - Sign in with GitHub
   - Click "Add repository"
   - Select "Helm charts"
   - Enter your repository URL (e.g., `https://YOUR_USERNAME.github.io/chat-app-charts`)
3. Artifact Hub will automatically index your charts and make them discoverable

## 🔧 Quick Start Script

Use the provided script to automate packaging:

```bash
cd charts
chmod +x publish.sh
./publish.sh
```

Then follow the instructions it prints.

## 📝 Versioning

When updating your chart:

1. Update `version` in `Chart.yaml`
2. Package: `helm package charts/chat-app`
3. Update index: `helm repo index . --url https://YOUR_USERNAME.github.io/chat-app-charts --merge index.yaml`
4. Commit and push the new `.tgz` and updated `index.yaml`

## ✅ Verification

Test your published chart:

```bash
# Add repo
helm repo add chat-app https://YOUR_USERNAME.github.io/chat-app-charts
helm repo update

# Test installation (dry-run)
helm install --dry-run --debug my-chat-app chat-app/chat-app

# Or actually install
helm install my-chat-app chat-app/chat-app
```

## 🎯 Recommendation

**For most users, GitHub Pages (Option 1) is the easiest** because:
- ✅ No external services needed
- ✅ Free for public repos
- ✅ Simple setup
- ✅ Works with standard `helm repo add` commands
- ✅ Automatically discoverable on Artifact Hub if you add it there

