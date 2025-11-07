#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Deploying Chat App with Ollama & Spotify MCP to Kubernetes...${NC}\n"

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed or not in PATH${NC}"
    exit 1
fi

# Check if namespace exists
if kubectl get namespace chat-spotify &> /dev/null; then
    echo -e "${YELLOW}Namespace 'chat-spotify' already exists${NC}"
else
    echo -e "${GREEN}Creating namespace...${NC}"
    kubectl apply -f k8s/namespace.yaml
fi

# Check if secrets exist
if kubectl get secret -n chat-spotify spotify-credentials &> /dev/null; then
    echo -e "${YELLOW}Secret 'spotify-credentials' already exists. Skipping...${NC}"
    echo -e "${YELLOW}If you need to update credentials, delete the secret first:${NC}"
    echo -e "${YELLOW}  kubectl delete secret -n chat-spotify spotify-credentials${NC}\n"
else
    echo -e "${GREEN}Creating Spotify credentials secret...${NC}"
    echo -e "${YELLOW}NOTE: Update k8s/secret-spotify.yaml with your credentials first!${NC}"
    kubectl apply -f k8s/secret-spotify.yaml
fi

# Apply ConfigMaps
echo -e "${GREEN}Applying ConfigMaps...${NC}"
kubectl apply -f k8s/configmap-chat-app.yaml

# Note: Ollama runs on localhost:11434, not in Kubernetes
echo -e "${YELLOW}Note: Ollama should be running on localhost:11434${NC}"
echo -e "${YELLOW}The chat app will connect to it via host.docker.internal${NC}\n"

# Deploy Chat App
echo -e "${GREEN}Deploying Chat App...${NC}"
kubectl apply -f k8s/deployment-chat-app.yaml
kubectl apply -f k8s/service-chat-app.yaml

# Deploy Ingress (optional)
if [ "$1" == "--with-ingress" ]; then
    echo -e "${GREEN}Deploying Ingress...${NC}"
    kubectl apply -f k8s/ingress.yaml
fi

echo -e "\n${GREEN}Deployment complete!${NC}\n"

# Show status
echo -e "${GREEN}Pod Status:${NC}"
kubectl get pods -n chat-spotify

echo -e "\n${GREEN}Service Status:${NC}"
kubectl get svc -n chat-spotify

echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "1. Ensure Ollama is running on localhost:11434"
echo -e "   - Install: https://ollama.ai"
echo -e "   - Start: ollama serve"
echo -e "   - Pull model: ollama pull llama3.2"
echo -e ""
echo -e "2. Access the app:"
echo -e "   kubectl port-forward -n chat-spotify service/chat-app-service 8080:80"
echo -e "   Then open: http://localhost:8080"
echo -e ""
echo -e "3. Check logs:"
echo -e "   kubectl logs -n chat-spotify -l app=chat-app"
echo -e ""
echo -e "4. Troubleshooting:"
echo -e "   If chat app can't reach Ollama, try:"
echo -e "   - Enable hostNetwork in deployment-chat-app.yaml"
echo -e "   - Or update OLLAMA_BASE_URL in configmap to use your cluster's gateway IP"

