# CountryFlag Deployment Guide

This guide provides comprehensive instructions for deploying the CountryFlag package in production environments using various deployment options.

## Table of Contents

- [Docker Containerization](#docker-containerization)
- [Docker Compose Setup](#docker-compose-setup)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Cloud Platform Deployments](#cloud-platform-deployments)
  - [AWS Deployment](#aws-deployment)
  - [Google Cloud Platform](#google-cloud-platform)
  - [Microsoft Azure](#microsoft-azure)
- [Performance Monitoring](#performance-monitoring)
- [High Availability Setup](#high-availability-setup)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

## Docker Containerization

The CountryFlag package can be easily containerized using Docker. We provide a ready-to-use Dockerfile that builds an optimized container for the service.

### Building the Docker Image

1. Navigate to the project root directory
2. Build the Docker image:

```bash
docker build -t countryflag-api:latest -f deploy/Dockerfile .
```

### Running the Container

```bash
docker run -p 8000:8000 countryflag-api:latest
```

### Configuration Options

The container supports the following environment variables:

- `LOG_LEVEL`: Sets the logging level (DEBUG, INFO, WARNING, ERROR)
- `ENABLE_CACHE`: Enables in-memory caching (true/false)
- `CACHE_TTL`: Cache time-to-live in seconds
- `REDIS_HOST`: Optional Redis host for distributed caching
- `REDIS_PORT`: Optional Redis port (default: 6379)

Example with configuration:

```bash
docker run -p 8000:8000 \
  -e LOG_LEVEL=INFO \
  -e ENABLE_CACHE=true \
  -e CACHE_TTL=3600 \
  countryflag-api:latest
```

## Docker Compose Setup

For a more complete setup including a web frontend and Redis cache, we provide a Docker Compose configuration.

### Starting the Stack

```bash
cd deploy
docker-compose up -d
```

This will start:
- The CountryFlag API service
- An Nginx web server for the frontend
- A Redis cache for improved performance

### Scaling the Service

```bash
docker-compose up -d --scale countryflag-api=3
```

### Stopping the Stack

```bash
docker-compose down
```

## Kubernetes Deployment

For production deployments, Kubernetes provides better scalability and reliability.

### Prerequisites

- A running Kubernetes cluster
- `kubectl` configured to connect to your cluster
- Optional: Helm for more advanced deployments

### Deployment Process

1. Update the image repository in the deployment files:

```bash
sed -i 's|${YOUR_REGISTRY}|your-registry.example.com|g' deploy/kubernetes/deployment.yaml
```

2. Apply the deployment:

```bash
kubectl apply -f deploy/kubernetes/deployment.yaml
```

3. Apply the ingress configuration:

```bash
kubectl apply -f deploy/kubernetes/ingress.yaml
```

4. Set up auto-scaling:

```bash
kubectl apply -f deploy/kubernetes/hpa.yaml
```

### Monitoring the Deployment

```bash
kubectl get pods -l app=countryflag
kubectl get services -l app=countryflag
kubectl get ingress countryflag-ingress
```

### Accessing the Service

Once deployed, the service will be available at:
- Inside the cluster: `http://countryflag-api`
- External URL: The URL configured in your ingress (e.g., `https://api.countryflag.example.com`)

## Cloud Platform Deployments

### AWS Deployment

#### Using Amazon ECS (Elastic Container Service)

1. Create an ECR (Elastic Container Registry) repository:

```bash
aws ecr create-repository --repository-name countryflag-api
```

2. Build and push the Docker image:

```bash
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com
docker build -t YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/countryflag-api:latest -f deploy/Dockerfile .
docker push YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/countryflag-api:latest
```

3. Create an ECS cluster, task definition, and service using the AWS console or CLI.

#### Using AWS EKS (Elastic Kubernetes Service)

1. Create an EKS cluster:

```bash
eksctl create cluster --name countryflag-cluster --region us-west-2 --nodegroup-name standard-nodes --node-type t3.medium --nodes 3 --nodes-min 2 --nodes-max 5
```

2. Configure kubectl:

```bash
aws eks update-kubeconfig --name countryflag-cluster --region us-west-2
```

3. Follow the standard Kubernetes deployment steps above.

### Google Cloud Platform

#### Using Google Kubernetes Engine (GKE)

1. Create a GKE cluster:

```bash
gcloud container clusters create countryflag-cluster --zone us-central1-a --num-nodes 3
```

2. Configure kubectl:

```bash
gcloud container clusters get-credentials countryflag-cluster --zone us-central1-a
```

3. Build and push the Docker image to Google Container Registry:

```bash
docker build -t gcr.io/YOUR_PROJECT_ID/countryflag-api:latest -f deploy/Dockerfile .
docker push gcr.io/YOUR_PROJECT_ID/countryflag-api:latest
```

4. Update the image in the deployment files:

```bash
sed -i 's|${YOUR_REGISTRY}|gcr.io/YOUR_PROJECT_ID|g' deploy/kubernetes/deployment.yaml
```

5. Follow the standard Kubernetes deployment steps above.

#### Using Google Cloud Run

For serverless deployments:

```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/countryflag-api
gcloud run deploy countryflag-api --image gcr.io/YOUR_PROJECT_ID/countryflag-api --platform managed --region us-central1 --allow-unauthenticated
```

### Microsoft Azure

#### Using Azure Kubernetes Service (AKS)

1. Create an AKS cluster:

```bash
az aks create --resource-group myResourceGroup --name countryflagAKSCluster --node-count 3 --enable-addons monitoring --generate-ssh-keys
```

2. Configure kubectl:

```bash
az aks get-credentials --resource-group myResourceGroup --name countryflagAKSCluster
```

3. Build and push the Docker image to Azure Container Registry:

```bash
az acr create --resource-group myResourceGroup --name countryflagacr --sku Basic
az acr login --name countryflagacr
docker build -t countryflagacr.azurecr.io/countryflag-api:latest -f deploy/Dockerfile .
docker push countryflagacr.azurecr.io/countryflag-api:latest
```

4. Grant AKS access to ACR:

```bash
az aks update -n countryflagAKSCluster -g myResourceGroup --attach-acr countryflagacr
```

5. Update the image in the deployment files:

```bash
sed -i 's|${YOUR_REGISTRY}|countryflagacr.azurecr.io|g' deploy/kubernetes/deployment.yaml
```

6. Follow the standard Kubernetes deployment steps above.

## Performance Monitoring

### Prometheus and Grafana Setup

1. Install Prometheus and Grafana on your Kubernetes cluster:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack
```

2. Access Grafana:

```bash
kubectl port-forward svc/prometheus-grafana 3000:80
```

3. Import the CountryFlag dashboard (available in the `deploy/monitoring` directory).

### Metrics to Monitor

- Request rate and latency
- Error rate
- CPU and memory usage
- Cache hit/miss ratio
- External API call rate (if applicable)

### Logging Configuration

For centralized logging, consider using:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Fluentd with Cloud Logging
- AWS CloudWatch Logs

## High Availability Setup

### Multi-region Deployment

For global high availability, deploy the service in multiple regions:

1. Set up DNS-based routing (e.g., AWS Route 53 or GCP Cloud DNS)
2. Deploy the application in at least two regions
3. Configure health checks and failover policies

### Redis Cluster for Caching

For distributed caching:

1. Set up a Redis cluster:

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install redis bitnami/redis --set cluster.enabled=true --set cluster.slaveCount=3
```

2. Configure the application to use the Redis cluster for caching.

### Database Replication (if applicable)

If your deployment uses a database:

1. Set up primary-replica replication
2. Configure automatic failover
3. Use connection pooling for efficient resource usage

## Security Considerations

### Container Security

1. Run containers as non-root users (already configured in the provided Dockerfile)
2. Use minimal base images (e.g., Python slim)
3. Regularly scan images for vulnerabilities:

```bash
docker scan countryflag-api:latest
```

### Network Security

1. Use TLS for all external endpoints
2. Implement proper network policies in Kubernetes
3. Configure Web Application Firewall (WAF) for API endpoints

### Access Control

1. Use RBAC (Role-Based Access Control) in Kubernetes
2. Implement API authentication if needed
3. Rotate service account credentials regularly

## Troubleshooting

### Common Issues

#### Container Startup Failures

Check logs:
```bash
docker logs <container_id>
# or in Kubernetes
kubectl logs <pod_name>
```

#### Performance Issues

1. Check if caching is enabled and working
2. Monitor resource usage
3. Look for slow database queries or external API calls

#### Network Connectivity

1. Check service discovery and DNS resolution
2. Verify network policies and security groups
3. Test connectivity between services:

```bash
kubectl exec -it <pod_name> -- curl http://countryflag-api
```

### Getting Support

For additional help:
- Open an issue on the GitHub repository
- Contact the maintainers via email
- Join our community chat
