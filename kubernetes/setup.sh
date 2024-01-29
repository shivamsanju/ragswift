# Prerequisite 
# Create a free qdrant account on qdrant cloud for testing. 
# For production host your own qdrant or get a enterprise subscription


# Step 1: Add Helm repo
helm repo add kuberay https://ray-project.github.io/kuberay-helm/
helm repo update

# Step 2: Install both CRDs and KubeRay operator v1.0.0.
helm install kuberay-operator kuberay/kuberay-operator

# Step 3: Confirm that the operator is running in the namespace `default`.
kubectl get pods
# NAME                                READY   STATUS    RESTARTS   AGE
# kuberay-operator-7fbdbf8c89-pt8bk   1/1     Running   0          27s

# Download your ray cluster config yaml
curl -LO https://raw.githubusercontent.com/shivamsanju/ragswift/main/kubernetes/deploy.yaml

# Apply config
kubectl apply -f deploy.yaml


# Check pods -> 2 head pods should start ray head and ray autoscaler
kubectl get pods

# Check services -> A ray serve service will start if serve application launches successfully
kubectl get services

# If not check logs 
kubectl cp "head_pod_name":/tmp/ray/session_latest/logs/ ./logs/

# Forward ports -> Dashboard and ray serve
kubectl port-forward --address 0.0.0.0 service/"head_service_name" 8265:8265
kubectl port-forward --address 0.0.0.0 service/"ray_serve_service" 8000:8000
