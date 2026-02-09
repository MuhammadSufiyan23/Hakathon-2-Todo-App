# Todo App - Minikube Deployment Guide

## Prerequisites
- Minikube running ✓
- kubectl installed ✓
- Docker images built ✓
  - todo-backend:latest
  - todo-frontend:latest

## Step 1: Load Docker Images into Minikube

Since Minikube uses its own Docker daemon, you need to load the images:

### Option A: Using Minikube Command (Recommended)
```bash
# Open PowerShell or Command Prompt and run:
minikube image load todo-backend:latest
minikube image load todo-frontend:latest

# Verify images are loaded
minikube image ls | findstr todo
```

### Option B: Using Docker Environment
```bash
# Set Docker to use Minikube's daemon
minikube docker-env | Invoke-Expression

# Rebuild images (they'll be in Minikube's registry)
cd "C:\Users\king\Desktop\New folder\Phase-3-Todo-Apps\backend"
docker build -t todo-backend:latest .

cd "C:\Users\king\Desktop\New folder\Phase-3-Todo-Apps\frontend"
docker build -t todo-frontend:latest .
```

## Step 2: Install Helm (if not installed)

### Windows Installation:
```powershell
# Using Chocolatey
choco install kubernetes-helm

# Or using Scoop
scoop install helm

# Or download from: https://github.com/helm/helm/releases
```

## Step 3: Deploy Using Helm

```bash
# Navigate to the Helm chart directory
cd "C:\Users\king\Desktop\New folder\Phase-3-Todo-Apps\todo-chatbot"

# Validate the Helm chart
helm lint .

# Install the application
helm install todo-app . --namespace default

# Or upgrade if already installed
helm upgrade --install todo-app . --namespace default
```

## Step 4: Verify Deployment

```bash
# Check pods status
kubectl get pods

# Check services
kubectl get services

# Get Minikube IP
minikube ip

# Access the application
# Frontend: http://<minikube-ip>:30300
# Backend: http://<minikube-ip>:30800
```

## Step 5: Access the Application

```bash
# Get the Minikube IP address
minikube ip

# Open in browser:
# Frontend: http://<minikube-ip>:30300
# Backend API: http://<minikube-ip>:30800

# Or use minikube service command to open automatically
minikube service todo-app-frontend
minikube service todo-app-backend
```

## Troubleshooting

### Images Not Found
If you get "ImagePullBackOff" errors:
```bash
# Verify images are in Minikube
minikube ssh
docker images | grep todo
exit
```

### Pods Not Starting
```bash
# Check pod logs
kubectl logs <pod-name>

# Describe pod for events
kubectl describe pod <pod-name>
```

### Port Already in Use
If NodePorts 30300 or 30800 are in use, edit `values.yaml`:
```yaml
frontend:
  service:
    nodePort: 30301  # Change to available port

backend:
  service:
    nodePort: 30801  # Change to available port
```

## Uninstall

```bash
# Remove the Helm release
helm uninstall todo-app

# Verify cleanup
kubectl get all
```

## Alternative: Deploy Without Helm

If Helm is not available, use the manual Kubernetes manifests in the `k8s-manifests/` directory:

```bash
kubectl apply -f k8s-manifests/
```

## Configuration

To modify environment variables or secrets, edit `values.yaml`:

```yaml
backend:
  secrets:
    cohereApiKey: "your-api-key"
    betterAuthSecret: "your-secret"
  env:
    databaseUrl: "sqlite:///./todo.db"
```

Then upgrade the deployment:
```bash
helm upgrade todo-app .
```
