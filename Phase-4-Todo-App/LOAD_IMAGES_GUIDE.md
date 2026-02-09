# Load Docker Images into Minikube

## Problem
The pods show "ErrImageNeverPull" because the Docker images are not in Minikube's registry.

## Solution Steps

### Step 1: Load Images into Minikube

Run these commands in PowerShell or Command Prompt:

```powershell
# Method 1: Using minikube image load (Recommended)
minikube image load todo-backend:latest
minikube image load todo-frontend:latest

# Verify images are loaded
minikube ssh "docker images | grep todo"
```

### Step 2: Alternative - Use Minikube's Docker Daemon

```powershell
# Point your Docker CLI to Minikube's Docker daemon
minikube docker-env | Invoke-Expression

# Verify you're using Minikube's Docker
docker ps

# Now rebuild the images (they'll be in Minikube's registry)
cd "C:\Users\king\Desktop\New folder\Phase-3-Todo-Apps\backend"
docker build -t todo-backend:latest .

cd "C:\Users\king\Desktop\New folder\Phase-3-Todo-Apps\frontend"
docker build -t todo-frontend:latest .

# Verify images
docker images | findstr todo
```

### Step 3: Restart the Deployments

```bash
# Delete and recreate the deployments
kubectl delete deployment todo-backend todo-frontend

# Reapply the manifests
kubectl apply -f "C:\Users\king\Desktop\New folder\Phase-3-Todo-Apps\k8s-manifests\"

# Or just restart the deployments
kubectl rollout restart deployment todo-backend
kubectl rollout restart deployment todo-frontend
```

### Step 4: Verify Deployment

```bash
# Watch pods until they're running
kubectl get pods -w

# Check pod status
kubectl get pods

# Check logs if there are issues
kubectl logs -l component=backend
kubectl logs -l component=frontend
```

### Step 5: Access the Application

```bash
# Get Minikube IP
kubectl get nodes -o wide

# Access URLs:
# Frontend: http://192.168.49.2:30300
# Backend: http://192.168.49.2:30800

# Or use kubectl port-forward
kubectl port-forward svc/todo-frontend 3000:3000
kubectl port-forward svc/todo-backend 8000:8000
```

## Quick Commands

```bash
# Check everything
kubectl get all

# Describe pod for troubleshooting
kubectl describe pod <pod-name>

# Get logs
kubectl logs <pod-name>

# Delete everything
kubectl delete -f "C:\Users\king\Desktop\New folder\Phase-3-Todo-Apps\k8s-manifests\"
```

## Current Status

- ✓ Secrets created
- ✓ Backend deployment created
- ✓ Backend service created (NodePort 30800)
- ✓ Frontend deployment created
- ✓ Frontend service created (NodePort 30300)
- ⚠ Images need to be loaded into Minikube
- ⚠ Pods waiting for images

## Next Steps

1. Run: `minikube image load todo-backend:latest`
2. Run: `minikube image load todo-frontend:latest`
3. Run: `kubectl rollout restart deployment todo-backend todo-frontend`
4. Run: `kubectl get pods` to verify
5. Access: http://192.168.49.2:30300
