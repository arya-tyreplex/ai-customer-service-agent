"""
Complete ML System Training Pipeline
Runs all steps: Data preparation → Model training → Testing
"""

import sys
import time
from pathlib import Path
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")


def print_banner(text: str):
    """Print section banner."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def check_csv_exists():
    """Check if CSV file exists."""
    csv_path = Path('vehicle_tyre_mapping.csv')
    if not csv_path.exists():
        logger.error("❌ CSV file not found: vehicle_tyre_mapping.csv")
        logger.info("\n📝 Please ensure your CSV file is in the project root")
        return False
    
    file_size_mb = csv_path.stat().st_size / (1024 * 1024)
    logger.success(f"✅ CSV file found ({file_size_mb:.1f} MB)")
    return True


def install_dependencies():
    """Install required packages."""
    logger.info("Checking dependencies...")
    
    required = [
        'pandas', 'numpy', 'scikit-learn', 'joblib', 'loguru'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        logger.info(f"Installing missing packages: {', '.join(missing)}")
        import subprocess
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '--quiet'
            ] + missing)
            logger.success("✅ Dependencies installed")
        except:
            logger.error("❌ Failed to install dependencies")
            logger.info(f"Please run: pip install {' '.join(missing)}")
            return False
    else:
        logger.success("✅ All dependencies installed")
    
    return True


def create_directories():
    """Create necessary directories."""
    logger.info("Creating directories...")
    
    dirs = ['data/processed', 'models', 'logs', 'results']
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    logger.success("✅ Directories created")
    return True


def step1_prepare_datasets():
    """Step 1: Prepare datasets from CSV."""
    print_banner("STEP 1: Dataset Preparation")
    
    try:
        from src.ml_system.dataset_builder import DatasetBuilder
        
        # Initialize builder
        builder = DatasetBuilder('vehicle_tyre_mapping.csv')
        
        # Load and clean data
        builder.load_and_clean_data()
        
        # Get statistics
        stats = builder.get_dataset_statistics()
        logger.info("\n📊 Dataset Statistics:")
        logger.info(f"  Total records: {stats['total_records']:,}")
        logger.info(f"  Unique vehicles: {stats['unique_vehicles']}")
        logger.info(f"  Unique brands: {stats['unique_brands']}")
        logger.info(f"  Unique sizes: {stats['unique_sizes']}")
        logger.info(f"  Price range: ₹{stats['price_stats']['min']:.0f} - ₹{stats['price_stats']['max']:.0f}")
        
        # Create and save datasets
        builder.save_datasets('data/processed')
        
        logger.success("\n✅ Step 1 Complete: Datasets prepared")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in dataset preparation: {e}")
        return False


def step2_train_models():
    """Step 2: Train ML models."""
    print_banner("STEP 2: Model Training")
    
    try:
        from src.ml_system.model_trainer import ModelTrainer
        
        # Initialize trainer
        trainer = ModelTrainer('data/processed')
        
        # Train all models
        trainer.train_all_models()
        
        # Save models
        trainer.save_models('models')
        
        # Get summary
        summary = trainer.get_model_summary()
        
        logger.info("\n📊 Training Summary:")
        logger.info(f"  Models trained: {summary['total_models']}")
        
        for model_name, metrics in summary['metrics'].items():
            logger.info(f"\n  {model_name}:")
            for metric, value in metrics.items():
                if isinstance(value, float):
                    if 'accuracy' in metric:
                        logger.info(f"    {metric}: {value*100:.2f}%")
                    elif metric in ['mae', 'rmse']:
                        logger.info(f"    {metric}: ₹{value:.2f}")
                    else:
                        logger.info(f"    {metric}: {value:.4f}")
                else:
                    logger.info(f"    {metric}: {value}")
        
        logger.success("\n✅ Step 2 Complete: Models trained")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in model training: {e}")
        return False


def step3_test_inference():
    """Step 3: Test inference engine."""
    print_banner("STEP 3: Testing Inference Engine")
    
    try:
        from src.ml_system.ml_inference import MLInferenceEngine
        
        # Initialize engine
        engine = MLInferenceEngine('models', 'data/processed')
        
        # Test brand recommendation
        logger.info("\n🧪 Testing brand recommendation...")
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
            logger.success("✅ Brand recommendation working")
            for i, brand in enumerate(brands, 1):
                logger.info(f"  {i}. {brand['brand']} ({brand['confidence_percent']:.1f}%)")
        
        # Test price prediction
        logger.info("\n🧪 Testing price prediction...")
        price = engine.predict_price(
            vehicle_make="Maruti Suzuki",
            vehicle_model="Swift",
            vehicle_type="Hatchback",
            vehicle_price=700000,
            tyre_brand="MRF",
            tyre_size="185/65 R15"
        )
        
        if 'predicted_price' in price:
            logger.success(f"✅ Price prediction working: {price['formatted_price']}")
        
        # Test intent classification
        logger.info("\n🧪 Testing intent classification...")
        intent = engine.classify_intent("I have a BMW Z4")
        
        if 'intent' in intent:
            logger.success(f"✅ Intent classification working: {intent['intent']} ({intent['confidence_percent']:.1f}%)")
        
        # Test complete recommendation
        logger.info("\n🧪 Testing complete recommendation...")
        complete = engine.get_complete_recommendation(
            vehicle_make="Maruti Suzuki",
            vehicle_model="Swift",
            vehicle_variant="VXI",
            vehicle_type="Hatchback",
            fuel_type="Petrol",
            vehicle_price=700000
        )
        
        if complete.get('tyre_size'):
            logger.success("✅ Complete recommendation working")
            logger.info(f"  Tyre size: {complete['tyre_size']['tyre_size']}")
            if complete.get('brand_prices'):
                logger.info(f"  Top brand: {complete['brand_prices'][0]['brand']} - {complete['brand_prices'][0]['formatted_price']}")
        
        logger.success("\n✅ Step 3 Complete: Inference engine tested")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in inference testing: {e}")
        return False


def step4_process_csv_data():
    """Step 4: Process CSV for fast lookups."""
    print_banner("STEP 4: Processing CSV for Fast Lookups")
    
    try:
        from src.inhouse_ml.csv_processor import CSVProcessor
        
        # Initialize processor
        processor = CSVProcessor('vehicle_tyre_mapping.csv')
        
        # Process CSV
        processor.process_csv_chunked(chunk_size=5000)
        
        # Get statistics
        stats = processor.get_statistics()
        logger.info("\n📊 CSV Processing Statistics:")
        logger.info(f"  Total records: {stats['total_records']:,}")
        logger.info(f"  Unique vehicles: {stats['unique_vehicles']:,}")
        logger.info(f"  Unique brands: {stats['unique_brands']}")
        logger.info(f"  Unique tyre sizes: {stats['unique_tyre_sizes']}")
        
        # Save processed data
        processor.save_to_disk('models')
        
        logger.success("\n✅ Step 4 Complete: CSV data processed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in CSV processing: {e}")
        return False


def generate_summary():
    """Generate final summary."""
    print_banner("TRAINING COMPLETE - SUMMARY")
    
    logger.info("📦 Generated Files:")
    logger.info("\n  Data Files:")
    logger.info("    - data/processed/brand_dataset.pkl")
    logger.info("    - data/processed/price_dataset.pkl")
    logger.info("    - data/processed/size_dataset.pkl")
    logger.info("    - data/processed/intent_dataset.pkl")
    logger.info("    - data/processed/encoders.pkl")
    logger.info("    - data/processed/scalers.pkl")
    
    logger.info("\n  Model Files:")
    logger.info("    - models/brand_recommender.pkl")
    logger.info("    - models/price_predictor.pkl")
    logger.info("    - models/size_predictor.pkl")
    logger.info("    - models/intent_classifier.pkl")
    logger.info("    - models/model_metrics.json")
    
    logger.info("\n  CSV Data:")
    logger.info("    - models/csv_data.pkl")
    logger.info("    - models/csv_stats.json")
    
    logger.info("\n🎯 What You Can Do Now:")
    logger.info("\n  1. Test ML predictions:")
    logger.info("     python src/ml_system/ml_inference.py")
    
    logger.info("\n  2. Test CSV integration:")
    logger.info("     python test_csv_integration.py")
    
    logger.info("\n  3. Run demo:")
    logger.info("     python examples/tyreplex_csv_demo.py")
    
    logger.info("\n  4. Use in your code:")
    logger.info("     from src.ml_system.ml_inference import MLInferenceEngine")
    logger.info("     engine = MLInferenceEngine()")
    logger.info("     result = engine.get_complete_recommendation(...)")
    
    logger.info("\n💡 Integration Options:")
    logger.info("  - ML Models: For predictions and recommendations")
    logger.info("  - CSV Lookups: For exact data from your CSV")
    logger.info("  - Hybrid: Use both for best results")
    
    logger.info("\n📚 Documentation:")
    logger.info("  - ML_SYSTEM_GUIDE.md - Complete ML documentation")
    logger.info("  - CSV_INTEGRATION_GUIDE.md - CSV integration guide")
    logger.info("  - START_HERE.md - Getting started guide")


def main():
    """Run complete training pipeline."""
    start_time = time.time()
    
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "TyrePlex Complete ML System Training" + " " * 22 + "║")
    print("║" + " " * 25 + "End-to-End Pipeline" + " " * 34 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")
    
    # Pre-checks
    logger.info("Running pre-flight checks...")
    
    if not check_csv_exists():
        return 1
    
    if not install_dependencies():
        return 1
    
    if not create_directories():
        return 1
    
    logger.success("✅ Pre-flight checks passed\n")
    
    # Run pipeline
    steps = [
        ("Dataset Preparation", step1_prepare_datasets),
        ("Model Training", step2_train_models),
        ("Inference Testing", step3_test_inference),
        ("CSV Processing", step4_process_csv_data)
    ]
    
    for i, (step_name, step_func) in enumerate(steps, 1):
        logger.info(f"\n{'='*80}")
        logger.info(f"Running Step {i}/{len(steps)}: {step_name}")
        logger.info(f"{'='*80}\n")
        
        if not step_func():
            logger.error(f"\n❌ Pipeline failed at step {i}: {step_name}")
            return 1
        
        time.sleep(1)
    
    # Generate summary
    generate_summary()
    
    # Calculate time
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    
    print("\n" + "=" * 80)
    logger.success(f"🎉 COMPLETE ML SYSTEM TRAINING SUCCESSFUL!")
    print("=" * 80)
    logger.info(f"\n⏱️  Total time: {minutes} minutes {seconds} seconds")
    logger.info("")
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Training interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
