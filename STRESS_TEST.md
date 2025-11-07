# Stress Testing the Vote App

This guide shows how to stress test the vote app with 30 concurrent users.

## Option 1: Using Locust (Recommended)

Locust is a popular Python-based load testing tool.

### Installation

```bash
pip install locust
```

### Running the Test

1. **Start your app** (if not already running):
   ```bash
   # Local
   streamlit run chat_app/app.py
   
   # Or port-forward if running in Kubernetes
   kubectl port-forward -n default service/my-chat-app-service 8501:80
   ```

2. **Run Locust**:
   ```bash
   locust -f locustfile.py --host=http://localhost:8501
   ```

3. **Open Locust Web UI**:
   - Open http://localhost:8089 in your browser
   - Set:
     - Number of users: 30
     - Spawn rate: 5 (users per second)
   - Click "Start swarming"

4. **Monitor Results**:
   - Watch real-time statistics
   - Check response times
   - Monitor error rates

### Command Line (Headless Mode)

```bash
# Run for 2 minutes with 30 users
locust -f locustfile.py \
  --host=http://localhost:8501 \
  --users 30 \
  --spawn-rate 5 \
  --run-time 2m \
  --headless \
  --html report.html
```

## Option 2: Using the Python Script

### Installation

```bash
pip install -r requirements-stress-test.txt
```

### Running the Test

```bash
# Basic usage (defaults: 30 users, 5 votes each, localhost:8501)
python stress_test_vote.py

# Custom URL
python stress_test_vote.py http://localhost:8501

# Custom users and votes
python stress_test_vote.py http://localhost:8501 30 10
```

### For Kubernetes Deployment

If your app is running in Kubernetes:

```bash
# Port-forward first
kubectl port-forward -n default service/my-chat-app-service 8501:80

# Then run stress test
python stress_test_vote.py http://localhost:8501 30 5
```

## Option 3: Using Apache Bench (ab)

Simple HTTP load testing:

```bash
# Install ab (usually comes with Apache)
# macOS: brew install httpd
# Linux: apt-get install apache2-utils

# Run 30 concurrent requests, 1000 total requests
ab -n 1000 -c 30 http://localhost:8501/2_Vote
```

## Option 4: Using wrk

High-performance HTTP benchmarking:

```bash
# Install wrk
# macOS: brew install wrk
# Linux: apt-get install wrk

# Run for 30 seconds with 30 connections
wrk -t4 -c30 -d30s http://localhost:8501/2_Vote
```

## Monitoring During Stress Test

### View App Logs

```bash
# Kubernetes
kubectl logs -f deployment/my-chat-app -n default

# Or for all pods
kubectl logs -f -l app.kubernetes.io/name=chat-app -n default
```

### View Redis Logs

```bash
kubectl logs -f statefulset/my-chat-app-redis-master -n default
```

### Check Pod Resources

```bash
kubectl top pods -n default
```

### Check Redis Metrics

```bash
# Connect to Redis
kubectl exec -it my-chat-app-redis-master-0 -n default -- redis-cli

# Check vote counts
GET votes:classic_music
GET votes:rock_music

# Monitor commands
MONITOR
```

## Expected Results

With 30 concurrent users:
- **Response time**: Should be < 500ms for most requests
- **Error rate**: Should be < 1%
- **Vote accuracy**: All votes should be recorded correctly
- **Redis performance**: Should handle concurrent increments without issues

## Troubleshooting

### High Error Rate
- Check if Redis is running: `kubectl get pods -n default | grep redis`
- Check Redis logs for errors
- Verify Redis service is accessible

### Slow Response Times
- Check pod resource usage: `kubectl top pods`
- Consider increasing replica count
- Check network latency

### Votes Not Recording
- Check app logs for Redis connection errors
- Verify Redis service name is correct
- Check Redis is accepting connections

