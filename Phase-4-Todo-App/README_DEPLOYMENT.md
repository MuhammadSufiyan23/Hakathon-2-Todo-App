# 🚀 Todo App - Complete Deployment Guide

## ✅ What's Been Done

### 1. Docker Images
- ✓ Backend image built: `todo-backend:latest` (182MB)
- ✓ Frontend image built: `todo-frontend:latest` (71.2MB)
- ✓ Both images tested and working locally

### 2. Kubernetes Configuration
- ✓ Helm charts created and configured
- ✓ Kubernetes manifests created
- ✓ Deployed to Minikube cluster
- ✓ Services exposed via NodePort

### 3. Current Deployment Status
```
✓ Secrets created
✓ Backend deployment created
✓ Backend service created (NodePort 30800)
✓ Frontend deployment created
✓ Frontend service created (NodePort 30300)
⚠ Pods waiting for images to be loaded
```

## 🎯 Final Step: Load Images into Minikube

### Quick Start (Recommended)

**Option 1: Run the deployment script**

Open PowerShell and run:
```powershell
cd "C:\Users\king\Desktop\New folder\Phase-3-Todo-Apps"
.\deploy-to-minikube.ps1
```

Or in Command Prompt:
```cmd
cd "C:\Users\king\Desktop\New folder\Phase-3-Todo-Apps"
deploy-to-minikube.bat
```

**Option 2: Manual commands**

```powershell
# Load images
minikube image load todo-backend:latest
minikube image load todo-frontend:latest

# Restart deployments
kubectl rollout restart deployment todo-backend
kubectl rollout restart deployment todo-frontend

# Check status
kubectl get pods
```

## 🌐 Access Your Application

Once pods are running (status: `Running`):

**Minikube IP**: `192.168.49.2`

- **Frontend**: http://192.168.49.2:30300
- **Backend API**: http://192.168.49.2:30800

## 📊 Verify Deployment

```bash
# Check all resources
kubectl get all

# Check pod status (should show "Running")
kubectl get pods

# View logs
kubectl logs -l component=frontend
kubectl logs -l component=backend

# Test backend health
curl http://192.168.49.2:30800/
```

## 🔧 Troubleshooting

### Pods still showing ErrImageNeverPull
```bash
# Verify images are in Minikube
minikube ssh "docker images | grep todo"

# If not present, load them again
minikube image load todo-backend:latest
minikube image load todo-frontend:latest
```

### Pods in CrashLoopBackOff
```bash
# Check logs for errors
kubectl logs <pod-name>

# Check pod events
kubectl describe pod <pod-name>
```

### Cannot access via NodePort
```bash
# Use port-forward instead
kubectl port-forward svc/todo-frontend 3000:3000
kubectl port-forward svc/todo-backend 8000:8000

# Access at:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

## 📁 Project Files

```
Phase-3-Todo-Apps/
├── backend/
│   ├── Dockerfile                    # Optimized Python container
│   └── .dockerignore                 # Excludes unnecessary files
├── frontend/
│   ├── Dockerfile                    # Multi-stage Next.js build
│   ├── .dockerignore                 # Excludes node_modules, etc.
│   └── next.config.js                # Standalone output enabled
├── todo-chatbot/                     # Helm Chart
│   ├── Chart.yaml
│   ├── values.yaml                   # Configured for Minikube
│   └── templates/
│       ├── backend-deployment.yaml
│       ├── backend-service.yaml
│       ├── frontend-deployment.yaml
│       ├── frontend-service.yaml
│       └── secrets.yaml
├── k8s-manifests/                    # Standalone manifests
│   ├── 01-secrets.yaml
│   ├── 02-backend-deployment.yaml
│   ├── 03-backend-service.yaml
│   ├── 04-frontend-deployment.yaml
│   └── 05-frontend-service.yaml
├── deploy-to-minikube.ps1           # PowerShell deployment script
├── deploy-to-minikube.bat           # Batch deployment script
├── DEPLOYMENT_SUMMARY.md            # Detailed deployment info
├── MINIKUBE_DEPLOYMENT.md           # Minikube setup guide
└── LOAD_IMAGES_GUIDE.md             # Image loading instructions
```

## 🎉 Success Criteria

Your deployment is successful when:
1. ✓ `kubectl get pods` shows both pods as `Running`
2. ✓ Frontend accessible at http://192.168.49.2:30300
3. ✓ Backend health check returns `{"status":"ok"}` at http://192.168.49.2:30800/
4. ✓ Frontend can communicate with backend API

## 🗑️ Cleanup

To remove the deployment:
```bash
kubectl delete -f k8s-manifests/
```

To stop Minikube:
```bash
minikube stop
```

## 📝 Next Steps After Deployment

1. Test the application functionality
2. Check logs for any errors
3. Monitor resource usage: `kubectl top pods`
4. Scale if needed: `kubectl scale deployment todo-backend --replicas=2`

## 🔗 Useful Links

- Kubernetes Dashboard: `minikube dashboard`
- View services: `minikube service list`
- SSH into Minikube: `minikube ssh`

---

**Need Help?**
- Check pod logs: `kubectl logs <pod-name>`
- Describe resources: `kubectl describe <resource-type> <name>`
- View events: `kubectl get events --sort-by=.metadata.creationTimestamp`
