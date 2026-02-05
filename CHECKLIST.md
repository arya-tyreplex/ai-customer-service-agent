# TyrePlex Setup Checklist

## ✅ Pre-Setup Checklist

- [ ] Python 3.7+ installed (`python --version`)
- [ ] Docker Desktop installed (`docker --version`)
- [ ] Docker Desktop is running (`docker ps`)
- [ ] Git Bash installed (Windows only)
- [ ] CSV file `vehicle_tyre_mapping.csv` in project root

## ✅ Setup Steps

- [ ] Run `./run.sh all` (10-15 minutes)
- [ ] Wait for completion (no errors)
- [ ] Check `models/` folder exists with .pkl files
- [ ] Check `data/processed/` folder exists

## ✅ Verification

- [ ] Run `python test_complete_system.py`
- [ ] All 5 tests pass:
  - [ ] ML Models: PASS
  - [ ] CSV Processing: PASS
  - [ ] Integrated Agent: PASS
  - [ ] REST API: PASS
  - [ ] Docker Services: PASS

## ✅ Demo

- [ ] Run `./run.sh demo`
- [ ] Demo 1: ML Models works
- [ ] Demo 2: CSV Processing works
- [ ] Demo 3: Integrated Agent works
- [ ] Demo 4: REST API info displayed

## ✅ REST API Testing

- [ ] Run `./run.sh run` (starts API)
- [ ] Open new terminal
- [ ] Test: `curl http://localhost:5000/health`
- [ ] Response: `{"status": "healthy", ...}`
- [ ] Test: `curl http://localhost:5000/api/brands`
- [ ] Response: List of brands

## ✅ Docker Services

- [ ] Run `docker-compose ps`
- [ ] MongoDB status: Up
- [ ] Elasticsearch status: Up
- [ ] No errors in logs: `docker-compose logs`

## ✅ Files Generated

- [ ] `venv/` folder (virtual environment)
- [ ] `models/brand_recommender.pkl`
- [ ] `models/price_predictor.pkl`
- [ ] `models/size_predictor.pkl`
- [ ] `models/intent_classifier.pkl`
- [ ] `models/csv_data.pkl`
- [ ] `data/processed/brand_dataset.pkl`
- [ ] `data/processed/price_dataset.pkl`
- [ ] `data/processed/size_dataset.pkl`
- [ ] `data/processed/intent_dataset.pkl`
- [ ] `data/processed/encoders.pkl`
- [ ] `data/processed/scalers.pkl`

## ✅ System Status

- [ ] ML models loaded successfully
- [ ] CSV data processed successfully
- [ ] MongoDB connected
- [ ] Elasticsearch connected
- [ ] REST API running on port 5000

## ✅ Ready for Production

- [ ] All tests pass
- [ ] Demo runs successfully
- [ ] REST API responds correctly
- [ ] Docker services running
- [ ] No errors in logs

## 🎯 Next Steps

Once all checkboxes are checked:

1. **Integrate into your application**
   - Use Python API: `from src.customer_service_agent.integrated_agent import IntegratedTyrePlexAgent`
   - Or use REST API: `http://localhost:5000/api/...`

2. **Test with real data**
   - Try different vehicle makes/models
   - Test brand comparisons
   - Test price predictions

3. **Add voice integration (later)**
   - Sign up for Twilio
   - Add credentials to .env
   - Use voice agent from examples/

## 🐛 If Something Fails

### ML Models fail
```bash
./run.sh train
```

### CSV Processing fails
```bash
./run.sh process
```

### Docker Services fail
```bash
./run.sh stop
./run.sh services
```

### Virtual Environment issues
```bash
./run.sh clean
./run.sh venv
pip install -r requirements.txt
```

### Complete Reset
```bash
./run.sh clean
./run.sh stop
./run.sh all
```

## 📞 Quick Commands

```bash
# Complete setup
./run.sh all

# Test everything
python test_complete_system.py

# Run demo
./run.sh demo

# Start API
./run.sh run

# Start services
./run.sh services

# Stop services
./run.sh stop

# Help
./run.sh help
```

## ✅ Success Criteria

Your setup is successful when:

1. ✅ `python test_complete_system.py` shows 5/5 tests passed
2. ✅ `./run.sh demo` runs without errors
3. ✅ `curl http://localhost:5000/health` returns healthy status
4. ✅ `docker-compose ps` shows MongoDB and Elasticsearch running
5. ✅ No errors in any logs

---

**Once all checkboxes are checked, you're ready to use the system!**
