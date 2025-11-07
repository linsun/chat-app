#!/bin/bash
# Script to package and prepare Helm chart for publishing

set -e

CHART_DIR="chat-app"
CHART_NAME="chat-app"
VERSION=$(grep '^version:' ${CHART_DIR}/Chart.yaml | awk '{print $2}')

echo "📦 Packaging Helm chart ${CHART_NAME} version ${VERSION}..."

# Update dependencies (downloads Redis subchart)
echo "📥 Updating chart dependencies..."
helm dependency update ${CHART_DIR}

# Package the chart
echo "📦 Packaging chart..."
helm package ${CHART_DIR}

# Create or update index
if [ -f index.yaml ]; then
    echo "📝 Updating existing index.yaml..."
    helm repo index . --url https://linsun.github.io/chat-app-charts --merge index.yaml
else
    echo "📝 Creating new index.yaml..."
    helm repo index . --url https://linsun.github.io/chat-app-charts
fi

echo "✅ Chart packaged successfully!"
echo ""
echo "📋 Next steps to publish:"
echo "1. Create a new repository: chat-app-charts (or use existing)"
echo "2. Push the packaged chart and index.yaml to the gh-pages branch:"
echo "   git init"
echo "   git checkout -b gh-pages"
echo "   git add ${CHART_NAME}-${VERSION}.tgz index.yaml"
echo "   git commit -m 'Add chart version ${VERSION}'"
echo "   git remote add origin https://github.com/linsun/chat-app-charts.git"
echo "   git push -u origin gh-pages"
echo ""
echo "3. Enable GitHub Pages in repository settings (Source: gh-pages branch)"
echo "4. Add the repo: helm repo add chat-app https://linsun.github.io/chat-app-charts"
echo "5. Install: helm install my-chat-app chat-app/chat-app"

