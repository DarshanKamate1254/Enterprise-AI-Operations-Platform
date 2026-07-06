# Production Deployment Guide

This guide describes how to deploy the **Enterprise AI Operations Platform** in multi-service container environments.

---

## 🐋 1. Deployment via Docker Compose

In a local or single-node production setup, Docker Compose compiles and orchestrates all application layers and databases with standard health checks.

### Build and Launch Services
To build the Docker images and run all services in detached mode:

```bash
docker compose up --build -d
```

### Verify Running Services
Confirm container health status:

```bash
docker compose ps
```

The services will be exposed at:
- **Frontend Client**: `http://localhost:3000`
- **API Gateway**: `http://localhost:8000`
- **RAG Service**: `http://localhost:8001`
- **MCP Server**: `http://localhost:8080`
- **Prometheus**: `http://localhost:9090`
- **Grafana**: `http://localhost:3000` *(accessible on port 3000 if frontend is not mapping container port 80 to it. In our compose config, frontend is exposed at `3000:80` and Grafana at `3000:3000` internally, so Grafana is on port 3000 as well. Make sure port mappings do not overlap).*

---

## ☸️ 2. Production Deployment via Kubernetes

For production deployments, the application is deployed into a Kubernetes cluster under the namespace `enterprise-ai-platform` with active PersistentVolumeClaims (PVCs) and HorizontalPodAutoscalers (HPAs).

### Step 1: Create Namespace and Configs
Apply the namespace and secrets:

```bash
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/secrets.yaml
```

### Step 2: Provision Database Layers
Apply StatefulSets for PostgreSQL, Qdrant, and the Redis deployment:

```bash
kubectl apply -f kubernetes/postgres-statefulset.yaml
kubectl apply -f kubernetes/qdrant-statefulset.yaml
kubectl apply -f kubernetes/redis-deployment.yaml
```

*This will provision persistent storage disks using dynamic volume provisioners.*

### Step 3: Deploy Microservices
Apply deployments for the MCP Server, RAG Service, and API Gateway:

```bash
kubectl apply -f kubernetes/mcp-server-deployment.yaml
kubectl apply -f kubernetes/rag-service-deployment.yaml
kubectl apply -f kubernetes/gateway-api-deployment.yaml
```

### Step 4: Deploy Frontend Client
Apply the client web server:

```bash
kubectl apply -f kubernetes/frontend-deployment.yaml
```

### Step 5: Configure Ingress Routing
Apply the Ingress controller route mappings:

```bash
kubectl apply -f kubernetes/ingress.yaml
```

Verify that Ingress routes path targets successfully:

```bash
kubectl get ingress platform-ingress -n enterprise-ai-platform
```

### Step 6: Verify Auto-scaling
Check the status of the HorizontalPodAutoscaler scaling the Gateway API instances:

```bash
kubectl get hpa gateway-api-hpa -n enterprise-ai-platform
```
