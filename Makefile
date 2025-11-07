.PHONY: help build push deploy undeploy clean test

# Variables
REGISTRY ?= localhost:5000
IMAGE_NAME ?= chat-app
IMAGE_TAG ?= latest
NAMESPACE ?= chat-spotify
KUBECON_IMAGE_NAME ?= kubecon-chat-app

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build the Docker image (chat app)
	@echo "Building Docker image..."
	docker build -t $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG) ./chat_app
	@echo "Built: $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)"

build-kubecon: ## Build the KubeCon chat app Docker image
	@echo "Building KubeCon chat app Docker image..."
	docker build -t $(REGISTRY)/$(KUBECON_IMAGE_NAME):$(IMAGE_TAG) ./kubecon_chat_app
	@echo "Built: $(REGISTRY)/$(KUBECON_IMAGE_NAME):$(IMAGE_TAG)"

push: build ## Build and push Docker image to registry
	@echo "Pushing Docker image..."
	docker push $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)
	@echo "Pushed: $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)"

push-kubecon: build-kubecon ## Build and push KubeCon chat app Docker image
	@echo "Pushing KubeCon chat app Docker image..."
	docker push $(REGISTRY)/$(KUBECON_IMAGE_NAME):$(IMAGE_TAG)
	@echo "Pushed: $(REGISTRY)/$(KUBECON_IMAGE_NAME):$(IMAGE_TAG)"

deploy: ## Deploy to Kubernetes
	@echo "Deploying to Kubernetes..."
	./deploy.sh

deploy-ingress: ## Deploy with Ingress
	@echo "Deploying to Kubernetes with Ingress..."
	./deploy.sh --with-ingress

update-secret: ## Update Spotify credentials secret (requires manual editing)
	@echo "Updating Spotify credentials..."
	@echo "Please update k8s/secret-spotify.yaml first, then:"
	@echo "kubectl apply -f k8s/secret-spotify.yaml"

logs-chat: ## View chat app logs
	kubectl logs -n $(NAMESPACE) -l app=chat-app --tail=100 -f

logs-kubecon: ## View KubeCon chat app logs
	kubectl logs -n $(NAMESPACE) -l app=kubecon-chat --tail=100 -f

logs-ollama: ## View Ollama logs (runs on localhost)
	@echo "Note: Ollama runs on localhost, not in Kubernetes"
	@echo "Check Ollama logs locally or with: journalctl -u ollama"

status: ## Show deployment status
	@echo "=== Pods ==="
	kubectl get pods -n $(NAMESPACE)
	@echo ""
	@echo "=== Services ==="
	kubectl get svc -n $(NAMESPACE)
	@echo ""
	@echo "=== PVCs ==="
	kubectl get pvc -n $(NAMESPACE)

port-forward: ## Port forward chat app service
	kubectl port-forward -n $(NAMESPACE) service/chat-app-service 8080:80

port-forward-kubecon: ## Port forward KubeCon chat app service
	kubectl port-forward -n $(NAMESPACE) service/kubecon-chat-service 8081:80

init-ollama: ## Initialize Ollama with llama3.2 model (runs on localhost)
	@echo "Note: Ollama runs on localhost, not in Kubernetes"
	@echo "Make sure Ollama is installed and running:"
	@echo "  Install: https://ollama.ai"
	@echo "  Start: ollama serve"
	@echo "  Pull model: ollama pull llama3.2"

undeploy: ## Remove all resources
	@echo "Removing all resources..."
	kubectl delete -f k8s/ --ignore-not-found=true

clean: ## Clean up local Docker images
	docker rmi $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG) || true

test: ## Run tests (placeholder)
	@echo "Running tests..."
	@echo "Tests not yet implemented"

.DEFAULT_GOAL := help

