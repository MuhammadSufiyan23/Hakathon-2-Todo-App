# Todo App - Minikube Deployment Script (PowerShell)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Todo App - Minikube Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Load images
Write-Host "Step 1: Loading Docker images into Minikube..." -ForegroundColor Yellow
Write-Host ""

Write-Host "Loading backend image..." -ForegroundColor White
minikube image load todo-backend:latest
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to load backend image" -ForegroundColor Red
    Write-Host "Make sure Minikube is running: minikube status" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Backend image loaded successfully" -ForegroundColor Green
Write-Host ""

Write-Host "Loading frontend image..." -ForegroundColor White
minikube image load todo-frontend:latest
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to load frontend image" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Frontend image loaded successfully" -ForegroundColor Green
Write-Host ""

# Step 2: Verify images
Write-Host "Step 2: Verifying images in Minikube..." -ForegroundColor Yellow
minikube ssh "docker images | grep todo"
Write-Host ""

# Step 3: Restart deployments
Write-Host "Step 3: Restarting deployments..." -ForegroundColor Yellow
kubectl rollout restart deployment todo-backend
kubectl rollout restart deployment todo-frontend
Write-Host ""

# Step 4: Wait and check pods
Write-Host "Step 4: Waiting for pods to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
kubectl get pods
Write-Host ""

# Step 5: Get access info
Write-Host "Step 5: Getting access information..." -ForegroundColor Yellow
$minikubeIp = kubectl get nodes -o jsonpath="{.items[0].status.addresses[?(@.type=='InternalIP')].address}"
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access your application at:" -ForegroundColor Yellow
Write-Host "  Frontend: http://$minikubeIp:30300" -ForegroundColor White
Write-Host "  Backend:  http://$minikubeIp:30800" -ForegroundColor White
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  Check pods:    kubectl get pods" -ForegroundColor White
Write-Host "  Frontend logs: kubectl logs -l component=frontend" -ForegroundColor White
Write-Host "  Backend logs:  kubectl logs -l component=backend" -ForegroundColor White
Write-Host ""

# Open frontend in browser
$openBrowser = Read-Host "Open frontend in browser? (Y/N)"
if ($openBrowser -eq "Y" -or $openBrowser -eq "y") {
    Start-Process "http://$minikubeIp:30300"
}
