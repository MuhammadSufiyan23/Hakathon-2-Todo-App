@echo off
echo ========================================
echo Loading Docker Images into Minikube
echo ========================================
echo.

echo This script will load your Docker images into Minikube's registry.
echo.

echo Step 1: Loading backend image...
minikube image load todo-backend:latest
if %errorlevel% neq 0 (
    echo ERROR: Failed to load backend image
    echo Make sure Docker Desktop is running and images exist
    pause
    exit /b 1
)
echo SUCCESS: Backend image loaded
echo.

echo Step 2: Loading frontend image...
minikube image load todo-frontend:latest
if %errorlevel% neq 0 (
    echo ERROR: Failed to load frontend image
    pause
    exit /b 1
)
echo SUCCESS: Frontend image loaded
echo.

echo Step 3: Verifying images in Minikube...
minikube ssh "docker images | grep todo"
echo.

echo Step 4: Restarting deployments...
kubectl rollout restart deployment todo-backend
kubectl rollout restart deployment todo-frontend
echo.

echo Step 5: Waiting for pods to start (30 seconds)...
timeout /t 30 /nobreak
echo.

echo Step 6: Checking pod status...
kubectl get pods
echo.

echo ========================================
echo Deployment Status
echo ========================================
kubectl get all
echo.

echo ========================================
echo Access Information
echo ========================================
echo.
echo Frontend: http://192.168.49.2:30300
echo Backend:  http://192.168.49.2:30800
echo.
echo To check logs:
echo   kubectl logs -l component=frontend
echo   kubectl logs -l component=backend
echo.

pause
