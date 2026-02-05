# Elasticsearch Setup Guide

## What is Elasticsearch?

Elasticsearch is a search engine that provides:
- Fast fuzzy search (handles typos)
- Full-text search
- Real-time indexing

**Note:** Elasticsearch is **optional** for the TyrePlex system. The core ML + CSV functionality works without it.

---

## When Do You Need Elasticsearch?

### ✅ You NEED Elasticsearch if:
- You want fuzzy search (typo correction)
- You want full-text search across all data
- You want real-time search updates

### ❌ You DON'T NEED Elasticsearch if:
- You only use ML models (brand, price, size, intent)
- You only use CSV lookups (exact matches)
- You're just testing the system

---

## How to Start Elasticsearch

### Option 1: Complete Setup (Recommended)
```bash
./run.sh all
```
This starts everything including Elasticsearch.

### Option 2: Manual Start
```bash
# Start Docker services
./run.sh services

# Wait 30 seconds for services to start
sleep 30

# Sync data to Elasticsearch
./run.sh sync
```

### Option 3: Check if Running
```bash
# Check Docker services
docker-compose ps

# Should show:
# elasticsearch   Up   0.0.0.0:9200->9200/tcp
# mongodb         Up   0.0.0.0:27017->27017/tcp
```

---

## Troubleshooting

### Issue: Elasticsearch connection failed

**Error:**
```
❌ Elasticsearch connection failed: Elasticsearch ping failed
```

**Solution 1: Start Services**
```bash
./run.sh services
```

**Solution 2: Check Docker**
```bash
# Is Docker running?
docker ps

# Are services running?
docker-compose ps

# Check logs
docker-compose logs elasticsearch
```

**Solution 3: Restart Services**
```bash
./run.sh stop
./run.sh services
```

### Issue: Elasticsearch not responding

**Check if port is available:**
```bash
# Windows
netstat -ano | findstr :9200

# If port is in use, stop the process or change port
```

**Change Elasticsearch port (if needed):**

Edit `docker-compose.yml`:
```yaml
elasticsearch:
  ports:
    - "9201:9200"  # Change 9200 to 9201
```

Then update `.env`:
```bash
ELASTICSEARCH_HOST=localhost:9201
```

### Issue: Elasticsearch takes too long to start

**Wait longer:**
```bash
# Start services
./run.sh services

# Wait 60 seconds (ES needs time to start)
sleep 60

# Then sync
./run.sh sync
```

**Check if ready:**
```bash
# Test connection
curl http://localhost:9200

# Should return JSON with cluster info
```

---

## Using the System WITHOUT Elasticsearch

The system works perfectly fine without Elasticsearch!

### What Works Without ES:
- ✅ ML models (brand, price, size, intent)
- ✅ CSV lookups (exact matches)
- ✅ REST API (all endpoints except search)
- ✅ Integrated agent
- ✅ All core functionality

### What Doesn't Work Without ES:
- ❌ Fuzzy search (typo correction)
- ❌ Full-text search
- ❌ Search endpoints in REST API

### To Use Without ES:

**1. Skip Elasticsearch in setup:**
```bash
# Don't run sync
./run.sh venv
./run.sh prepare
./run.sh train
# Skip: ./run.sh services
# Skip: ./run.sh sync
./run.sh run
```

**2. Or start only MongoDB:**
```bash
# Edit docker-compose.yml and comment out elasticsearch
docker-compose up -d mongodb
```

---

## Elasticsearch Commands

### Start Elasticsearch
```bash
./run.sh services
```

### Stop Elasticsearch
```bash
./run.sh stop
```

### Sync Data to Elasticsearch
```bash
./run.sh sync
```

### Check Elasticsearch Status
```bash
# Health check
curl http://localhost:9200/_cluster/health

# Check indices
curl http://localhost:9200/_cat/indices

# Count documents
curl http://localhost:9200/tyreplex-vehicles/_count
curl http://localhost:9200/tyreplex-tyres/_count
```

### View Elasticsearch Logs
```bash
docker-compose logs -f elasticsearch
```

### Restart Elasticsearch
```bash
docker-compose restart elasticsearch
```

---

## Elasticsearch Configuration

### Default Settings
- Host: `localhost`
- Port: `9200`
- Indices: `tyreplex-vehicles`, `tyreplex-tyres`

### Change Settings

Edit `.env`:
```bash
ELASTICSEARCH_HOST=localhost:9200
```

Or set environment variable:
```bash
export ELASTICSEARCH_HOST=localhost:9200
```

---

## Performance

### Elasticsearch Stats
- Index time: ~30 seconds (for 10K records)
- Search time: <50ms
- Memory usage: ~500MB
- Disk usage: ~100MB

### When to Use
- ✅ Large datasets (>10K records)
- ✅ Need fuzzy search
- ✅ Need full-text search
- ✅ Production deployment

### When to Skip
- ❌ Small datasets (<1K records)
- ❌ Only exact matches needed
- ❌ Testing/development
- ❌ Limited resources

---

## Summary

### Elasticsearch is Optional
- Core system works without it
- Only needed for advanced search features
- Can be added later

### To Use With Elasticsearch
```bash
./run.sh all
```

### To Use Without Elasticsearch
```bash
./run.sh venv
./run.sh prepare
./run.sh train
# Skip services and sync
./run.sh run
```

### Quick Test
```bash
# With ES:
curl http://localhost:9200

# Without ES:
# Just skip the sync step
```

---

**Elasticsearch is a nice-to-have, not a must-have! 🎯**
