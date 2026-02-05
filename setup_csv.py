"""
One-command setup for CSV integration
Runs all necessary steps automatically
"""

import sys
import subprocess
from pathlib import Path
from loguru import logger

logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")


def print_banner():
    """Print welcome banner."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "TyrePlex CSV Integration Setup" + " " * 23 + "║")
    print("║" + " " * 20 + "Automated Installation" + " " * 27 + "║")
    print("╚" + "═" * 68 + "╝")
    print("\n")


def check_csv_exists():
    """Check if CSV file exists."""
    logger.info("Step 1: Checking for CSV file...")
    
    csv_path = Path('vehicle_tyre_mapping.csv')
    if not csv_path.exists():
        logger.error("❌ CSV file not found: vehicle_tyre_mapping.csv")
        logger.info("\n📝 Please ensure your CSV file is in the project root:")
        logger.info("   - File name: vehicle_tyre_mapping.csv")
        logger.info("   - Location: Same folder as this script")
        return False
    
    file_size_mb = csv_path.stat().st_size / (1024 * 1024)
    logger.success(f"✅ CSV file found ({file_size_mb:.1f} MB)")
    return True


def check_dependencies():
    """Check if required packages are installed."""
    logger.info("\nStep 2: Checking dependencies...")
    
    required = ['pandas', 'numpy', 'loguru', 'joblib']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            logger.success(f"✅ {package}")
        except ImportError:
            logger.warning(f"⚠️  {package} not found")
            missing.append(package)
    
    if missing:
        logger.info(f"\n📦 Installing missing packages: {', '.join(missing)}")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '--quiet'
            ] + missing)
            logger.success("✅ All dependencies installed")
        except subprocess.CalledProcessError:
            logger.error("❌ Failed to install dependencies")
            logger.info("Please run: pip install pandas numpy loguru joblib")
            return False
    else:
        logger.success("✅ All dependencies installed")
    
    return True


def create_directories():
    """Create necessary directories."""
    logger.info("\nStep 3: Creating directories...")
    
    dirs = ['models', 'call_logs', 'data']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        logger.success(f"✅ {dir_name}/")
    
    return True


def process_csv():
    """Process CSV file."""
    logger.info("\nStep 4: Processing CSV data...")
    logger.info("This may take 2-5 minutes depending on file size...")
    
    try:
        # Import and run processor
        from src.inhouse_ml.csv_processor import CSVProcessor
        
        processor = CSVProcessor('vehicle_tyre_mapping.csv')
        processor.process_csv_chunked(chunk_size=5000)
        
        # Get statistics
        stats = processor.get_statistics()
        logger.success(f"✅ Processed {stats['total_records']:,} records")
        logger.info(f"   Unique vehicles: {stats['unique_vehicles']:,}")
        logger.info(f"   Unique brands: {stats['unique_brands']}")
        logger.info(f"   Unique tyre sizes: {stats['unique_tyre_sizes']}")
        
        # Save
        processor.save_to_disk('models')
        logger.success("✅ Data saved to models/")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error processing CSV: {e}")
        return False


def run_tests():
    """Run integration tests."""
    logger.info("\nStep 5: Running tests...")
    
    try:
        from src.customer_service_agent.csv_tools import CSVTyrePlexTools
        
        tools = CSVTyrePlexTools()
        
        # Test 1: Get brands
        brands = tools.get_all_brands()
        if brands['success']:
            logger.success(f"✅ Test 1: Found {brands['total_brands']} brands")
        else:
            logger.error("❌ Test 1: Failed to get brands")
            return False
        
        # Test 2: Search vehicles
        search = tools.search_vehicles("BMW")
        if not search['success']:
            search = tools.search_vehicles("Maruti")
        
        if search['success'] and search['vehicles']:
            logger.success(f"✅ Test 2: Found {search['total_matches']} vehicles")
            
            # Test 3: Vehicle lookup
            test_vehicle = search['vehicles'][0]
            result = tools.identify_vehicle_tyre_size(
                test_vehicle['make'],
                test_vehicle['model'],
                test_vehicle['variant']
            )
            
            if result['success']:
                logger.success(f"✅ Test 3: Vehicle lookup successful")
                logger.info(f"   {test_vehicle['make']} {test_vehicle['model']}")
                logger.info(f"   Front: {result['front_tyre_size']}")
                logger.info(f"   Rear: {result['rear_tyre_size']}")
                
                # Test 4: Tyre recommendations
                recs = tools.get_tyre_recommendations(
                    result['front_tyre_size'],
                    budget_range='mid'
                )
                
                if recs['success']:
                    logger.success(f"✅ Test 4: Found {recs['total_options']} tyre options")
                else:
                    logger.warning("⚠️  Test 4: No recommendations found")
            else:
                logger.warning("⚠️  Test 3: Vehicle lookup failed")
        else:
            logger.warning("⚠️  Test 2: No vehicles found")
        
        logger.success("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error running tests: {e}")
        return False


def print_summary():
    """Print setup summary."""
    logger.info("\n" + "=" * 70)
    logger.success("🎉 CSV Integration Setup Complete!")
    logger.info("=" * 70)
    
    logger.info("\n📦 What Was Created:")
    logger.info("  ✅ models/csv_data.pkl - Processed data")
    logger.info("  ✅ models/csv_stats.json - Statistics")
    logger.info("  ✅ CSV tools ready to use")
    
    logger.info("\n🧪 Test Commands:")
    logger.info("  python test_csv_integration.py    # Full test suite")
    logger.info("  python examples/tyreplex_csv_demo.py    # Demo conversations")
    
    logger.info("\n📚 Documentation:")
    logger.info("  CSV_INTEGRATION_GUIDE.md    # Complete guide")
    logger.info("  README.md    # Project overview")
    
    logger.info("\n🚀 Next Steps:")
    logger.info("  1. Run demo: python examples/tyreplex_csv_demo.py")
    logger.info("  2. Integrate with voice agent")
    logger.info("  3. Test with phone calls")
    logger.info("  4. Deploy to production")
    
    logger.info("\n💡 Quick Start:")
    logger.info("  from src.customer_service_agent.csv_tools import CSVTyrePlexTools")
    logger.info("  tools = CSVTyrePlexTools()")
    logger.info("  result = tools.identify_vehicle_tyre_size('BMW', 'Z4', 'M40i')")
    
    logger.info("")


def main():
    """Run complete setup."""
    print_banner()
    
    # Step 1: Check CSV
    if not check_csv_exists():
        return 1
    
    # Step 2: Check dependencies
    if not check_dependencies():
        return 1
    
    # Step 3: Create directories
    if not create_directories():
        return 1
    
    # Step 4: Process CSV
    if not process_csv():
        return 1
    
    # Step 5: Run tests
    if not run_tests():
        logger.warning("\n⚠️  Some tests failed, but setup is complete")
        logger.info("You can still use the system")
    
    # Print summary
    print_summary()
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n\n❌ Unexpected error: {e}")
        logger.info("Please check the error and try again")
        sys.exit(1)
