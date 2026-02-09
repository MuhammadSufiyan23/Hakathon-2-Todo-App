@echo off
REM Todo App - Minikube Deployment Script
REM Run this script in Command Prompt or PowerShell

echo ========================================
echo Todo App - Minikube Deployment
echo ========================================
echo.

echo Step 1: Loading Docker images into Minikube...
echo.

echo Loading backend image...
minikube image load todo-backend:latest
if %errorlevel% neq 0 (
    echo ERROR: Failed to load backend image
    echo Make sure Minikube is running: minikube status
    pause
    exit /b 1
)
echo ✓ Backend image loaded successfully
echo.

echo Loading frontend image...
minikube image load todo-frontend:latest
if %errorlevel% neq 0 (
    echo ERROR: Failed to load frontend image
    pause
    exit /b 1
)
echo ✓ Frontend image loaded successfully
echo.

echo Step 2: Verifying images in Minikube...
minikube ssh "docker images | grep todo"
echo.

echo Step 3: Restarting deployments...
kubectl rollout restart deployment todo-backend
kubectl rollout restart deployment todo-frontend
echo.

echo Step 4: Waiting for pods to be ready...
timeout /t 10 /nobreak >nul
kubectl get pods
echo.

echo Step 5: Getting access information...
echo.
echo Minikube IP:
kubectl get nodes -o jsonpath="{.items[0].status.addresses[?(@.type=='InternalIP')].address}"
echo.
echo.

echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Access your application at:
echo   Frontend: http://192.168.49.2:30300
echo   Backend:  http://192.168.49.2:30800
echo.
echo To check pod status: kubectl get pods
echo To view logs: kubectl logs -l component=frontend
echo               kubectl logs -l component=backend
echo.

pause
