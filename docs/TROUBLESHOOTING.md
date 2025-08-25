# MemoryLink Troubleshooting Guide
*Comprehensive Problem Resolution and Debugging Guide*

## 🚨 Quick Problem Resolution

### ⚡ Emergency Checklist

If MemoryLink is not working, try these steps in order:

```bash
# 1. Check service status
make health

# 2. View recent logs
make logs | tail -50

# 3. Restart services
make restart

# 4. Verify configuration
echo $ENCRYPTION_KEY | wc -c  # Should be 32+ characters

# 5. Check disk space
df -h /data

# 6. Test basic functionality
curl http://localhost:8080/health
```

### 🔍 Quick Diagnostic Commands

```bash
# System status overview
make status

# Container health
docker ps --filter name=memorylink

# Resource usage
docker stats memorylink --no-stream

# Network connectivity
curl -I http://localhost:8080/health

# Database status
sqlite3 data/metadata/memorylink.db "SELECT COUNT(*) FROM memories;"
```

## 📊 Common Issues and Solutions

### 🚀 Startup Issues

#### Issue: Container Won't Start

**Symptoms:**
- `docker-compose up` fails
- Container exits immediately
- "Port already in use" errors

**Diagnosis:**
```bash
# Check what's using the port
netstat -tulpn | grep :8080

# Check Docker logs
docker-compose logs memorylink

# Check container status
docker ps -a --filter name=memorylink
```

**Solutions:**

1. **Port Conflict:**
```bash
# Option 1: Change port
export API_PORT=8081
make restart

# Option 2: Kill conflicting process
sudo lsof -ti:8080 | xargs sudo kill -9
make start
```

2. **Permission Issues:**
```bash
# Fix data directory permissions
sudo chown -R $(id -u):$(id -g) data/
sudo chmod -R 755 data/
```

3. **Missing Environment Variables:**
```bash
# Check required variables
echo "Encryption key length: $(echo -n $ENCRYPTION_KEY | wc -c)"

# Generate if missing
if [ -z "$ENCRYPTION_KEY" ]; then
    echo "ENCRYPTION_KEY=$(openssl rand -base64 32)" >> .env
fi
```

4. **Docker Issues:**
```bash
# Clean and rebuild
make clean
make build
make start

# Or reset everything
make reset
```

#### Issue: Slow Startup

**Symptoms:**
- Container starts but takes 2+ minutes
- Health checks fail initially
- API becomes available late

**Diagnosis:**
```bash
# Monitor startup logs
docker-compose logs -f memorylink

# Check resource usage during startup
docker stats memorylink
```

**Solutions:**

1. **Increase Resources:**
```yaml
# docker-compose.yml
services:
  memorylink:
    deploy:
      resources:
        limits:
          memory: 2G  # Increase from 1G
          cpus: '1.0'  # Increase from 0.5
```

2. **Pre-download Models:**
```bash
# Download embedding model ahead of time
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

3. **Optimize Startup:**
```bash
# Set faster startup mode
export EMBEDDING_MODEL_CACHE=true
export SKIP_MODEL_VALIDATION=true
make restart
```

### 🔍 API Issues

#### Issue: 500 Internal Server Error

**Symptoms:**
- API requests return 500 errors
- No specific error message
- Random failures

**Diagnosis:**
```bash
# Check detailed logs
docker-compose logs memorylink | grep ERROR

# Test specific endpoint
curl -v -X POST http://localhost:8080/memories/ \
  -H "Content-Type: application/json" \
  -d '{"content":"test"}'

# Check database connectivity
docker exec memorylink sqlite3 /data/metadata/memorylink.db "SELECT 1;"
```

**Solutions:**

1. **Database Corruption:**
```bash
# Check database integrity
sqlite3 data/metadata/memorylink.db "PRAGMA integrity_check;"

# Backup and repair if needed
cp data/metadata/memorylink.db data/metadata/memorylink.db.backup
sqlite3 data/metadata/memorylink.db "VACUUM;"
```

2. **Encryption Issues:**
```bash
# Test encryption service
docker exec memorylink python -c "
from src.utils.encryption import EncryptionService
enc = EncryptionService()
test = enc.encrypt('hello')
print('Encryption working:', enc.decrypt(test) == 'hello')
"
```

3. **Memory Issues:**
```bash
# Check memory usage
docker stats memorylink --no-stream

# Increase memory limit
docker-compose down
# Edit docker-compose.yml to increase memory
docker-compose up -d
```

#### Issue: Slow API Responses

**Symptoms:**
- Requests take > 5 seconds
- Timeouts on large operations
- Search is very slow

**Diagnosis:**
```bash
# Measure response times
time curl -X POST http://localhost:8080/search/ \
  -H "Content-Type: application/json" \
  -d '{"query":"test search"}'

# Check system resources
top -p $(docker inspect --format '{{.State.Pid}}' memorylink)

# Profile database performance
sqlite3 data/metadata/memorylink.db ".timer on" "SELECT COUNT(*) FROM memories;"
```

**Solutions:**

1. **Enable Caching:**
```bash
# Add to .env
echo "EMBEDDING_CACHE_SIZE=1000" >> .env
echo "SEARCH_CACHE_SIZE=2000" >> .env
make restart
```

2. **Optimize Database:**
```bash
# Run database optimization
sqlite3 data/metadata/memorylink.db "
PRAGMA optimize;
VACUUM;
ANALYZE;
"
```

3. **Increase Workers:**
```bash
# Add more workers
echo "WORKERS=4" >> .env
make restart
```

### 🔍 Search Issues

#### Issue: No Search Results

**Symptoms:**
- Search returns empty results
- Even exact text matches fail
- Previously working searches break

**Diagnosis:**
```bash
# Check if memories exist
curl http://localhost:8080/memories/ | jq 'length'

# Test with very low threshold
curl -X POST http://localhost:8080/search/ \
  -H "Content-Type: application/json" \
  -d '{"query":"test", "threshold":0.1}'

# Check embedding service
docker logs memorylink 2>&1 | grep -i embedding
```

**Solutions:**

1. **Vector Database Issues:**
```bash
# Check vector database
ls -la data/vector/

# Reset vector database
make stop
rm -rf data/vector/*
make start
# Re-add memories to rebuild index
```

2. **Embedding Model Problems:**
```bash
# Test embedding generation
docker exec memorylink python -c "
from src.services.embedding_service import EmbeddingService
embed = EmbeddingService()
result = embed.generate_sync('test text')
print('Embedding dimensions:', len(result))
"
```

3. **Threshold Too High:**
```bash
# Use lower similarity threshold
curl -X POST http://localhost:8080/search/ \
  -H "Content-Type: application/json" \
  -d '{"query":"your search", "threshold":0.2}'
```

#### Issue: Poor Search Quality

**Symptoms:**
- Irrelevant results returned
- Relevant memories not found
- Search ranking seems wrong

**Diagnosis:**
```bash
# Test search with debug info
curl -X POST http://localhost:8080/search/ \
  -H "Content-Type: application/json" \
  -d '{"query":"machine learning", "limit":10}' | jq '.[] | {similarity, content: .memory.content[:50]}'
```

**Solutions:**

1. **Improve Content Quality:**
```python
# When adding memories, include more context
{
    "content": "Machine learning algorithms like neural networks...",
    "metadata": {
        "tags": ["machine-learning", "neural-networks", "algorithms"],
        "category": "technology",
        "keywords": "ML, AI, deep learning"
    }
}
```

2. **Adjust Search Parameters:**
```bash
# Use different similarity thresholds
# Strict: 0.7-0.9, Medium: 0.5-0.7, Loose: 0.2-0.5
curl -X POST http://localhost:8080/search/ \
  -d '{"query":"search terms", "threshold":0.6, "limit":20}'
```

3. **Use Better Embedding Model:**
```bash
# Switch to more powerful model (requires restart)
echo "EMBEDDING_MODEL=all-mpnet-base-v2" >> .env
make restart
```

### 🔒 Security Issues

#### Issue: Encryption Errors

**Symptoms:**
- "Decryption failed" errors
- Stored memories unreadable
- Key-related exceptions

**Diagnosis:**
```bash
# Check encryption key
echo "Key length: $(echo -n $ENCRYPTION_KEY | wc -c)"

# Test encryption/decryption
docker exec memorylink python -c "
try:
    from src.utils.encryption import EncryptionService
    enc = EncryptionService()
    encrypted = enc.encrypt('test')
    decrypted = enc.decrypt(encrypted)
    print('Encryption test:', 'PASSED' if decrypted == 'test' else 'FAILED')
except Exception as e:
    print('Encryption error:', str(e))
"
```

**Solutions:**

1. **Regenerate Encryption Key:**
```bash
# ⚠️  WARNING: This makes existing data unreadable
make backup  # Backup first!

# Generate new key
EXPORT ENCRYPTION_KEY=$(openssl rand -base64 32)
echo "ENCRYPTION_KEY=$ENCRYPTION_KEY" > .env.new

# Clean start with new key
make stop
mv .env .env.old
mv .env.new .env
rm -rf data/
make start
```

2. **Key Format Issues:**
```bash
# Ensure proper key format
key=$(openssl rand -base64 32)
echo "Generated key length: ${#key}"

# Update .env with proper key
sed -i "s/ENCRYPTION_KEY=.*/ENCRYPTION_KEY=${key}/" .env
```

3. **Restore from Backup:**
```bash
# If you have a backup with the correct key
make stop
rm -rf data/
make restore BACKUP_PATH=/path/to/backup.tar.gz
```

### 💾 Data Issues

#### Issue: Data Loss or Corruption

**Symptoms:**
- Memories disappeared
- Database errors
- Inconsistent data

**Diagnosis:**
```bash
# Check database integrity
sqlite3 data/metadata/memorylink.db "PRAGMA integrity_check;"

# Count memories in database vs API
db_count=$(sqlite3 data/metadata/memorylink.db "SELECT COUNT(*) FROM memories;")
api_count=$(curl -s http://localhost:8080/memories/ | jq 'length')
echo "DB: $db_count, API: $api_count"

# Check disk space
df -h data/
```

**Solutions:**

1. **Restore from Backup:**
```bash
# List available backups
ls -la data/backups/

# Restore most recent
make restore BACKUP_PATH=data/backups/memorylink_backup_$(date +%Y%m%d).tar.gz
```

2. **Database Repair:**
```bash
# Stop services
make stop

# Attempt repair
sqlite3 data/metadata/memorylink.db "
.backup backup.db
.exit
"
mv data/metadata/memorylink.db data/metadata/memorylink.db.corrupt
mv backup.db data/metadata/memorylink.db

make start
```

3. **Rebuild Vector Index:**
```bash
# If vector data is corrupted
make stop
rm -rf data/vector/*
make start

# Re-index all memories
curl -X POST http://localhost:8080/admin/reindex
```

### 📊 Performance Issues

#### Issue: High Memory Usage

**Symptoms:**
- Container using > 2GB RAM
- System becomes slow
- Out of memory errors

**Diagnosis:**
```bash
# Monitor memory usage
docker stats memorylink --no-stream

# Check memory breakdown
docker exec memorylink cat /proc/meminfo

# Check cache sizes
curl http://localhost:8080/metrics | grep cache
```

**Solutions:**

1. **Reduce Cache Sizes:**
```bash
# Reduce caching in .env
echo "EMBEDDING_CACHE_SIZE=500" >> .env
echo "SEARCH_CACHE_SIZE=1000" >> .env
make restart
```

2. **Optimize Embedding Model:**
```bash
# Use smaller model
echo "EMBEDDING_MODEL=all-MiniLM-L6-v2" >> .env  # 80MB vs 420MB
make restart
```

3. **Increase Container Limits:**
```yaml
# docker-compose.yml
services:
  memorylink:
    deploy:
      resources:
        limits:
          memory: 4G  # Increase limit
```

#### Issue: High CPU Usage

**Symptoms:**
- CPU constantly at 100%
- Slow response times
- System overheating

**Diagnosis:**
```bash
# Monitor CPU usage
top -p $(docker inspect --format '{{.State.Pid}}' memorylink)

# Check what's using CPU
docker exec memorylink ps aux

# Monitor API requests
curl http://localhost:8080/metrics | grep requests_total
```

**Solutions:**

1. **Limit Workers:**
```bash
# Reduce number of workers
echo "WORKERS=2" >> .env
make restart
```

2. **Optimize Operations:**
```bash
# Enable request rate limiting
echo "RATE_LIMIT_ENABLED=true" >> .env
echo "RATE_LIMIT_PER_MINUTE=60" >> .env
make restart
```

3. **Use CPU Limits:**
```yaml
# docker-compose.yml
services:
  memorylink:
    deploy:
      resources:
        limits:
          cpus: '1.0'  # Limit CPU usage
```

## 🔧 Advanced Troubleshooting

### Debug Mode Setup

```bash
# Enable comprehensive debugging
cat >> .env << EOF
DEBUG=true
LOG_LEVEL=DEBUG
SQL_DEBUG=true
EMBEDDING_DEBUG=true
EOF

make restart

# Watch debug logs
make logs | grep DEBUG
```

### Performance Profiling

```bash
# Profile API performance
curl -w "@curl-format.txt" -s -o /dev/null http://localhost:8080/health

# Create curl-format.txt
cat > curl-format.txt << 'EOF'
     time_namelookup:  %{time_namelookup}s
        time_connect:  %{time_connect}s
     time_appconnect:  %{time_appconnect}s
    time_pretransfer:  %{time_pretransfer}s
       time_redirect:  %{time_redirect}s
  time_starttransfer:  %{time_starttransfer}s
                     ----------
          time_total:  %{time_total}s
EOF
```

### Database Deep Dive

```bash
# Analyze database performance
sqlite3 data/metadata/memorylink.db << 'EOF'
.timer on
.schema
SELECT COUNT(*) as total_memories FROM memories;
SELECT 
    datetime(created_at) as date,
    COUNT(*) as count 
FROM memories 
GROUP BY date(created_at) 
ORDER BY date DESC 
LIMIT 10;
EOF
```

### Container Debugging

```bash
# Enter container for debugging
docker exec -it memorylink /bin/bash

# Check internal processes
ps aux
netstat -tulpn
df -h
free -h

# Test internal connectivity
curl http://localhost:8080/health

# Check Python environment
python -c "import sys; print(sys.path)"
pip list | grep -E "(fastapi|chromadb|sentence)"
```

## 💡 Prevention Strategies

### Monitoring Setup

```bash
# Create monitoring script
cat > monitor_memorylink.sh << 'EOF'
#!/bin/bash
set -e

# Check health
if ! curl -sf http://localhost:8080/health > /dev/null; then
    echo "[$(date)] ALERT: MemoryLink health check failed" >> monitor.log
    # Optional: restart service
    # make restart
fi

# Check disk space
USED=$(df /data | awk 'END{print $(NF-1)}' | sed 's/%//')
if [ $USED -gt 85 ]; then
    echo "[$(date)] WARNING: Disk usage at ${USED}%" >> monitor.log
fi

# Check memory usage
MEM_USAGE=$(docker stats memorylink --no-stream --format "{{.MemPerc}}" | sed 's/%//')
if (( $(echo "$MEM_USAGE > 80" | bc -l) )); then
    echo "[$(date)] WARNING: Memory usage at ${MEM_USAGE}%" >> monitor.log
fi

echo "[$(date)] Health check passed" >> monitor.log
EOF

chmod +x monitor_memorylink.sh

# Add to crontab (run every 5 minutes)
echo "*/5 * * * * /path/to/monitor_memorylink.sh" | crontab -
```

### Automated Backups

```bash
# Create backup script
cat > backup_memorylink.sh << 'EOF'
#!/bin/bash
set -e

BACKUP_DIR="./data/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="memorylink_backup_${TIMESTAMP}.tar.gz"

# Create backup
echo "[$(date)] Starting backup: $BACKUP_NAME"
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}" \
    data/metadata/ \
    data/vector/ \
    .env

# Verify backup
if tar -tzf "${BACKUP_DIR}/${BACKUP_NAME}" > /dev/null 2>&1; then
    echo "[$(date)] Backup successful: $BACKUP_NAME"
else
    echo "[$(date)] Backup verification failed: $BACKUP_NAME"
    exit 1
fi

# Cleanup old backups (keep 7 days)
find "$BACKUP_DIR" -name "memorylink_backup_*.tar.gz" -mtime +7 -delete

echo "[$(date)] Backup completed: $BACKUP_NAME"
EOF

chmod +x backup_memorylink.sh

# Schedule daily backups at 2 AM
echo "0 2 * * * /path/to/backup_memorylink.sh >> /var/log/memorylink_backup.log 2>&1" | crontab -
```

### Health Checks

```bash
# Comprehensive health check script
cat > health_check.sh << 'EOF'
#!/bin/bash

echo "=== MemoryLink Health Check ==="
echo "Timestamp: $(date)"

# 1. Container status
echo "\n1. Container Status:"
docker ps --filter name=memorylink --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 2. API health
echo "\n2. API Health:"
if curl -sf http://localhost:8080/health > /dev/null; then
    echo "✅ API responding"
    curl -s http://localhost:8080/health | jq '.
 else
    echo "❌ API not responding"
fi

# 3. Database connectivity
echo "\n3. Database Status:"
if sqlite3 data/metadata/memorylink.db "SELECT COUNT(*) FROM memories;" > /dev/null 2>&1; then
    echo "✅ Database accessible"
    echo "Memories count: $(sqlite3 data/metadata/memorylink.db "SELECT COUNT(*) FROM memories;")"
else
    echo "❌ Database not accessible"
fi

# 4. Disk space
echo "\n4. Storage Status:"
echo "Data directory usage:"
du -sh data/
echo "Available space:"
df -h data/

# 5. Memory usage
echo "\n5. Resource Usage:"
docker stats memorylink --no-stream --format "Memory: {{.MemUsage}} ({{.MemPerc}})"
docker stats memorylink --no-stream --format "CPU: {{.CPUPerc}}"

# 6. Recent errors
echo "\n6. Recent Errors (last 10):"
docker logs memorylink --since 1h 2>&1 | grep -i error | tail -10 || echo "No recent errors"

echo "\n=== Health Check Complete ==="
EOF

chmod +x health_check.sh
```

## 📞 Getting Help

### Self-Help Resources

1. **Documentation**
   - [User Guide](./USER_GUIDE.md)
   - [Technical Documentation](./TECHNICAL_DOCUMENTATION.md)
   - [FAQ](./FAQ.md)

2. **Logs and Diagnostics**
   ```bash
   # Collect diagnostic information
   ./health_check.sh > diagnostic_report.txt
   make logs > app_logs.txt
   docker system info > system_info.txt
   ```

3. **Community Support**
   - GitHub Issues: Report bugs and request features
   - Community Forums: Get help from other users
   - Documentation Updates: Improve guides based on your experience

### Creating Bug Reports

When reporting issues, include:

1. **System Information**
   - Operating system and version
   - Docker and Docker Compose versions
   - MemoryLink version

2. **Problem Description**
   - What you expected to happen
   - What actually happened
   - Steps to reproduce

3. **Diagnostic Information**
   ```bash
   # Collect this information
   make health > health_status.txt
   make logs | tail -100 > recent_logs.txt
   docker system info > docker_info.txt
   cat .env | grep -v ENCRYPTION_KEY > config.txt  # Don't share encryption key!
   ```

4. **Error Messages**
   - Complete error messages
   - Stack traces if available
   - Browser console errors (if applicable)

### Issue Template

```markdown
## Bug Report

**Describe the Bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
 - OS: [e.g. Ubuntu 22.04]
 - Docker Version: [e.g. 24.0.7]
 - MemoryLink Version: [e.g. 1.0.0]
 - Browser: [e.g. Chrome 91] (if applicable)

**Additional Context**
Add any other context about the problem.

**Diagnostic Information**
```
# Paste health check output here
```

**Logs**
```
# Paste relevant log entries here
```
```

---

## 🏆 Troubleshooting Success

### Resolution Verification

After fixing any issue:

```bash
# 1. Verify basic functionality
curl http://localhost:8080/health

# 2. Test core operations
curl -X POST http://localhost:8080/memories/ \
  -H "Content-Type: application/json" \
  -d '{"content":"Test memory after fix"}'

# 3. Test search
curl -X POST http://localhost:8080/search/ \
  -H "Content-Type: application/json" \
  -d '{"query":"test"}'

# 4. Run full health check
./health_check.sh

# 5. Create backup of working state
make backup
```

### Prevention Measures

1. **Set up monitoring** to catch issues early
2. **Schedule regular backups** to prevent data loss
3. **Keep logs** for troubleshooting future issues
4. **Document any custom configurations** for reference
5. **Test updates** in a separate environment first

---

**Most issues can be resolved quickly with systematic troubleshooting. When in doubt, check the logs, verify your configuration, and don't hesitate to ask for help in the community.**