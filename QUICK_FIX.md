# Quick Fix Guide

## Issue: REST API Not Starting

If you see this error:
```
ModuleNotFoundError: No module named 'flask'
```

Or:
```
ModuleNotFoundError: No module named 'src'
```

## Solution

Run these commands in order:

### 1. Create Virtual Environment
```bash
./run.sh venv
```

### 2. Install Dependencies
```bash
# Activate virtual environment first
# Windows Git Bash:
source venv/Scripts/activate

# Then install:
pip install -r requirements.txt
```

### 3. Prepare Data (if not done)
```bash
./run.sh prepare
```

### 4. Train Models (if not done)
```bash
./run.sh train
```

### 5. Start Services
```bash
./run.sh services
```

### 6. Now Run API
```bash
./run.sh run
```

## Or Use Complete Setup

Just run this one command:
```bash
./run.sh all
```

This will do everything automatically!

## Verify Installation

Check if dependencies are installed:
```bash
# Activate venv
source venv/Scripts/activate

# Check Flask
python -c "import flask; print('Flask OK')"

# Check scikit-learn
python -c "import sklearn; print('sklearn OK')"

# Check pandas
python -c "import pandas; print('pandas OK')"
```

## Common Issues

### Issue: Virtual environment not activated
**Solution:**
```bash
source venv/Scripts/activate
```

### Issue: Dependencies not installed
**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Models not trained
**Solution:**
```bash
./run.sh train
```

### Issue: MongoDB not running
**Solution:**
```bash
./run.sh services
```

## Quick Test

After fixing, test with:
```bash
# Test health endpoint
curl http://localhost:5000/health

# Should return:
# {"status": "healthy", "service": "TyrePlex AI System", "version": "1.0.0"}
```

---

**Still having issues? Run: `./run.sh all`**
