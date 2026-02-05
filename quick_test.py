"""
Quick test script to verify system is working
"""

from loguru import logger
import sys

def test_mongodb():
    """Test MongoDB connection."""
    try:
        from src.inhouse_ml.mongodb_manager import MongoDBManager
        db = MongoDBManager()
        stats = db.get_statistics()
        logger.success(f"✅ MongoDB: {stats}")
        db.close()
        return True
    except Exception as e:
        logger.error(f"❌ MongoDB failed: {e}")
        return False

def test_elasticsearch():
    """Test Elasticsearch connection."""
    try:
        from src.inhouse_ml.elasticsearch_indexer import ElasticsearchIndexer
        es = ElasticsearchIndexer()
        stats = es.get_index_stats()
        logger.success(f"✅ Elasticsearch: {stats}")
        return True
    except Exception as e:
        logger.error(f"❌ Elasticsearch failed: {e}")
        return False

def test_ml_models():
    """Test ML models."""
    try:
        from src.ml_system.ml_inference import MLInferenceEngine
        engine = MLInferenceEngine()
        logger.success(f"✅ ML Models loaded: {list(engine.models.keys())}")
        return True
    except Exception as e:
        logger.error(f"❌ ML Models failed: {e}")
        return False

def test_csv_tools():
    """Test CSV tools."""
    try:
        from src.customer_service_agent.csv_tools import CSVTyrePlexTools
        tools = CSVTyrePlexTools()
        brands = tools.get_all_brands()
        logger.success(f"✅ CSV Tools: {brands['total_brands']} brands loaded")
        return True
    except Exception as e:
        logger.error(f"❌ CSV Tools failed: {e}")
        return False

def test_integrated_agent():
    """Test integrated agent."""
    try:
        from src.customer_service_agent.integrated_agent import IntegratedTyrePlexAgent
        agent = IntegratedTyrePlexAgent()
        status = agent.get_system_status()
        logger.success(f"✅ Integrated Agent: {status}")
        return True
    except Exception as e:
        logger.error(f"❌ Integrated Agent failed: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("=" * 70)
    logger.info("TyrePlex System - Quick Test")
    logger.info("=" * 70)
    
    tests = [
        ("MongoDB", test_mongodb),
        ("Elasticsearch", test_elasticsearch),
        ("ML Models", test_ml_models),
        ("CSV Tools", test_csv_tools),
        ("Integrated Agent", test_integrated_agent)
    ]
    
    results = []
    for name, test_func in tests:
        logger.info(f"\nTesting {name}...")
        result = test_func()
        results.append((name, result))
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("Test Summary")
    logger.info("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {name}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.success("\n🎉 All tests passed!")
        return 0
    else:
        logger.error(f"\n❌ {total - passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
