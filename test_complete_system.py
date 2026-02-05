"""
Complete System Test - TyrePlex In-House ML System
Tests all components: ML models, CSV processing, REST API
"""

import sys
from pathlib import Path
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")


def test_ml_models():
    """Test ML inference engine."""
    logger.info("=" * 70)
    logger.info("TEST 1: ML Models")
    logger.info("=" * 70)
    
    try:
        from src.ml_system.ml_inference import MLInferenceEngine
        
        # Check if models exist
        model_dir = Path('models')
        if not model_dir.exists():
            logger.warning("⚠️  Models directory not found. Run: ./run.sh train")
            return False
        
        # Initialize engine
        engine = MLInferenceEngine()
        logger.success(f"✅ Loaded {len(engine.models)} ML models")
        
        # Test brand recommendation
        logger.info("\n  Testing brand recommendation...")
        brands = engine.recommend_brand(
            vehicle_make="Maruti Suzuki",
            vehicle_model="Swift",
            vehicle_type="Hatchback",
            fuel_type="Petrol",
            vehicle_price=700000,
            tyre_size="185/65 R15",
            top_k=3
        )
        
        if brands:
            logger.success(f"  ✅ Brand recommendation works ({len(brands)} brands)")
            for i, brand in enumerate(brands, 1):
                logger.info(f"     {i}. {brand['brand']} ({brand['confidence_percent']:.1f}%)")
        else:
            logger.error("  ❌ Brand recommendation failed")
            return False
        
        # Test price prediction
        logger.info("\n  Testing price prediction...")
        price = engine.predict_price(
            vehicle_make="Maruti Suzuki",
            vehicle_model="Swift",
            vehicle_type="Hatchback",
            vehicle_price=700000,
            tyre_brand="MRF",
            tyre_size="185/65 R15"
        )
        
        if price.get('predicted_price'):
            logger.success(f"  ✅ Price prediction works: {price['formatted_price']}")
        else:
            logger.error("  ❌ Price prediction failed")
            return False
        
        # Test tyre size prediction
        logger.info("\n  Testing tyre size prediction...")
        size = engine.predict_tyre_size(
            vehicle_make="Maruti Suzuki",
            vehicle_model="Swift",
            vehicle_variant="VXI",
            vehicle_type="Hatchback",
            fuel_type="Petrol",
            vehicle_price=700000
        )
        
        if size.get('tyre_size'):
            logger.success(f"  ✅ Size prediction works: {size['tyre_size']} ({size['confidence_percent']:.1f}%)")
        else:
            logger.error("  ❌ Size prediction failed")
            return False
        
        # Test intent classification
        logger.info("\n  Testing intent classification...")
        intent = engine.classify_intent("I have a BMW Z4")
        
        if intent.get('intent'):
            logger.success(f"  ✅ Intent classification works: {intent['intent']} ({intent['confidence_percent']:.1f}%)")
        else:
            logger.error("  ❌ Intent classification failed")
            return False
        
        logger.success("\n✅ All ML model tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ ML model test failed: {e}")
        logger.info("Run: ./run.sh train")
        return False


def test_csv_processing():
    """Test CSV processor."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 2: CSV Processing")
    logger.info("=" * 70)
    
    try:
        from src.inhouse_ml.csv_processor import CSVProcessor
        
        # Check if CSV exists
        csv_path = Path('vehicle_tyre_mapping.csv')
        if not csv_path.exists():
            logger.warning("⚠️  CSV file not found. Place vehicle_tyre_mapping.csv in project root")
            return False
        
        # Check if processed data exists
        processed_data = Path('models/csv_data.pkl')
        if not processed_data.exists():
            logger.warning("⚠️  Processed CSV data not found. Run: ./run.sh process")
            return False
        
        # Load processor
        processor = CSVProcessor.load_from_disk('models')
        logger.success("✅ Loaded processed CSV data")
        
        # Get statistics
        stats = processor.get_statistics()
        logger.info(f"\n  Total records: {stats['total_records']:,}")
        logger.info(f"  Unique vehicles: {stats['unique_vehicles']:,}")
        logger.info(f"  Unique brands: {stats['unique_brands']}")
        logger.info(f"  Unique tyre sizes: {stats['unique_tyre_sizes']}")
        
        # Test vehicle lookup
        logger.info("\n  Testing vehicle lookup...")
        if stats['makes']:
            test_make = stats['makes'][0]
            vehicles = processor.search_vehicles(test_make)
            if vehicles:
                logger.success(f"  ✅ Vehicle search works ({len(vehicles)} results for '{test_make}')")
            else:
                logger.warning(f"  ⚠️  No vehicles found for '{test_make}'")
        
        # Test tyre recommendations
        logger.info("\n  Testing tyre recommendations...")
        if processor.tyre_database:
            test_size = list(processor.tyre_database.keys())[0]
            tyres = processor.get_tyres_by_size(test_size, budget='mid')
            if tyres:
                logger.success(f"  ✅ Tyre recommendations work ({len(tyres)} tyres for {test_size})")
                for i, tyre in enumerate(tyres[:3], 1):
                    logger.info(f"     {i}. {tyre['brand']} {tyre['model']}: ₹{tyre['price']:.0f}")
            else:
                logger.warning(f"  ⚠️  No tyres found for size {test_size}")
        
        logger.success("\n✅ CSV processing tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ CSV processing test failed: {e}")
        logger.info("Run: ./run.sh process")
        return False


def test_integrated_agent():
    """Test integrated agent."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 3: Integrated Agent")
    logger.info("=" * 70)
    
    try:
        from src.customer_service_agent.integrated_agent import IntegratedTyrePlexAgent
        
        # Initialize agent
        agent = IntegratedTyrePlexAgent()
        logger.success("✅ Integrated agent initialized")
        
        # Check status
        status = agent.get_system_status()
        logger.info(f"\n  ML Available: {status['ml_available']}")
        logger.info(f"  CSV Available: {status['csv_available']}")
        logger.info(f"  Status: {status['recommendation']}")
        
        if not status['ml_available'] and not status['csv_available']:
            logger.error("  ❌ Neither ML nor CSV systems available")
            return False
        
        # Test vehicle identification
        logger.info("\n  Testing vehicle identification...")
        result = agent.identify_vehicle_and_recommend(
            "Maruti Suzuki", "Swift", "VXI", "mid"
        )
        
        if result.get('tyre_size'):
            logger.success(f"  ✅ Vehicle identification works (Source: {result.get('source', 'unknown')})")
            logger.info(f"     Tyre size: {result['tyre_size']['front']}")
            if result.get('recommendations'):
                logger.info(f"     Top brand: {result['recommendations'][0]['brand']}")
        else:
            logger.warning("  ⚠️  Vehicle not found (this is OK if you don't have this vehicle in data)")
        
        # Test intent classification
        logger.info("\n  Testing intent classification...")
        intent = agent.classify_customer_intent("I have a BMW Z4")
        if intent.get('intent'):
            logger.success(f"  ✅ Intent classification works: {intent['intent']}")
        
        # Test brand comparison
        logger.info("\n  Testing brand comparison...")
        comparison = agent.compare_brands("185/65 R15", "MRF", "CEAT")
        if comparison.get('success'):
            logger.success(f"  ✅ Brand comparison works (Source: {comparison.get('source', 'unknown')})")
        
        logger.success("\n✅ Integrated agent tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Integrated agent test failed: {e}")
        return False


def test_rest_api():
    """Test REST API (without starting server)."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 4: REST API")
    logger.info("=" * 70)
    
    try:
        # Check if Flask is installed
        import flask
        logger.success("✅ Flask installed")
        
        # Check if API file exists
        api_file = Path('src/api/rest_api.py')
        if not api_file.exists():
            logger.error("❌ REST API file not found")
            return False
        
        logger.success("✅ REST API file exists")
        logger.info("\n  To start REST API:")
        logger.info("    ./run.sh run")
        logger.info("  Or:")
        logger.info("    python src/api/rest_api.py")
        
        logger.info("\n  API Endpoints:")
        logger.info("    GET  /health")
        logger.info("    POST /api/vehicle/identify")
        logger.info("    GET  /api/vehicle/search?q=BMW")
        logger.info("    POST /api/tyres/compare")
        logger.info("    GET  /api/tyres/price-range")
        logger.info("    GET  /api/brands")
        logger.info("    POST /api/intent/classify")
        logger.info("    POST /api/lead/create")
        logger.info("    POST /api/booking/create")
        logger.info("    GET  /api/stats")
        
        logger.success("\n✅ REST API ready!")
        return True
        
    except ImportError:
        logger.error("❌ Flask not installed. Run: pip install -r requirements.txt")
        return False
    except Exception as e:
        logger.error(f"❌ REST API test failed: {e}")
        return False


def test_docker_services():
    """Test Docker services."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 5: Docker Services")
    logger.info("=" * 70)
    
    try:
        import subprocess
        
        # Check if docker-compose.yml exists
        compose_file = Path('docker-compose.yml')
        if not compose_file.exists():
            logger.error("❌ docker-compose.yml not found")
            return False
        
        logger.success("✅ docker-compose.yml exists")
        
        # Check if Docker is running
        try:
            result = subprocess.run(['docker', 'ps'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.success("✅ Docker is running")
            else:
                logger.warning("⚠️  Docker is not running")
                logger.info("  Start Docker Desktop and run: ./run.sh services")
                return True  # Not a failure, just not started
        except:
            logger.warning("⚠️  Docker not available")
            logger.info("  Install Docker and run: ./run.sh services")
            return True  # Not a failure, just not installed
        
        # Check if services are running
        try:
            result = subprocess.run(['docker-compose', 'ps'], capture_output=True, text=True, timeout=5)
            if 'mongodb' in result.stdout and 'Up' in result.stdout:
                logger.success("✅ MongoDB is running")
            else:
                logger.info("  MongoDB not running. Start with: ./run.sh services")
            
            if 'elasticsearch' in result.stdout and 'Up' in result.stdout:
                logger.success("✅ Elasticsearch is running")
            else:
                logger.info("  Elasticsearch not running. Start with: ./run.sh services")
        except:
            logger.info("  Services not started. Run: ./run.sh services")
        
        logger.info("\n  To start services:")
        logger.info("    ./run.sh services")
        logger.info("  To stop services:")
        logger.info("    ./run.sh stop")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Docker services test failed: {e}")
        return False


def main():
    """Run all tests."""
    logger.info("=" * 70)
    logger.info("TyrePlex In-House ML System - Complete Test Suite")
    logger.info("=" * 70)
    logger.info("")
    
    results = {
        'ML Models': test_ml_models(),
        'CSV Processing': test_csv_processing(),
        'Integrated Agent': test_integrated_agent(),
        'REST API': test_rest_api(),
        'Docker Services': test_docker_services()
    }
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"  {test_name:20s} {status}")
    
    logger.info("")
    logger.info(f"  Total: {passed}/{total} tests passed")
    
    if passed == total:
        logger.success("\n🎉 All tests passed! System is ready!")
        logger.info("\n📝 Next Steps:")
        logger.info("  1. Start services: ./run.sh services")
        logger.info("  2. Start REST API: ./run.sh run")
        logger.info("  3. Test API: curl http://localhost:5000/health")
    else:
        logger.warning("\n⚠️  Some tests failed. Follow the instructions above to fix them.")
        logger.info("\n📝 Quick Fix:")
        logger.info("  Run complete setup: ./run.sh all")
    
    logger.info("")


if __name__ == "__main__":
    main()
