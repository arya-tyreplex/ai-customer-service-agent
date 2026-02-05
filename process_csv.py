"""
Process your vehicle_tyre_mapping.csv file
Run this once to prepare data for the voice agent
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")

from src.inhouse_ml.csv_processor import CSVProcessor


def main():
    """Process CSV and create lookup tables."""
    
    logger.info("=" * 60)
    logger.info("TyrePlex CSV Data Processor")
    logger.info("=" * 60)
    
    # Check if CSV exists
    csv_path = 'vehicle_tyre_mapping.csv'
    if not Path(csv_path).exists():
        logger.error(f"❌ CSV file not found: {csv_path}")
        logger.info("Please ensure vehicle_tyre_mapping.csv is in the project root")
        return
    
    # Get file size
    file_size_mb = Path(csv_path).stat().st_size / (1024 * 1024)
    logger.info(f"📁 CSV file size: {file_size_mb:.1f} MB")
    
    # Initialize processor
    logger.info("\n🚀 Starting CSV processing...")
    processor = CSVProcessor(csv_path)
    
    # Process in chunks (adjust chunk_size based on your RAM)
    chunk_size = 5000 if file_size_mb > 100 else 10000
    logger.info(f"Using chunk size: {chunk_size} rows")
    
    try:
        processor.process_csv_chunked(chunk_size=chunk_size)
    except Exception as e:
        logger.error(f"❌ Error processing CSV: {e}")
        return
    
    # Get statistics
    logger.info("\n📊 Data Statistics:")
    stats = processor.get_statistics()
    logger.info(f"  Total records: {stats['total_records']:,}")
    logger.info(f"  Unique vehicles: {stats['unique_vehicles']:,}")
    logger.info(f"  Unique brands: {stats['unique_brands']}")
    logger.info(f"  Unique tyre sizes: {stats['unique_tyre_sizes']}")
    logger.info(f"  Price range: ₹{stats['price_range']['min']:.0f} - ₹{stats['price_range']['max']:.0f}")
    
    logger.info(f"\n🏷️  Available Brands ({len(stats['brands'])}):")
    for i, brand in enumerate(stats['brands'], 1):
        print(f"    {i:2d}. {brand}")
    
    logger.info(f"\n🚗 Available Makes ({len(stats['makes'])}):")
    for i, make in enumerate(stats['makes'], 1):
        print(f"    {i:2d}. {make.title()}")
    
    # Save to disk
    logger.info("\n💾 Saving processed data...")
    processor.save_to_disk('models')
    
    # Run tests
    logger.info("\n🧪 Running tests...")
    
    # Test 1: Vehicle lookup
    logger.info("\n  Test 1: Vehicle Lookup")
    test_result = processor.get_vehicle_info("BMW", "Z4", "BMW Z4 M40i Petrol AT")
    if test_result:
        logger.success(f"    ✅ Found vehicle!")
        logger.info(f"       Front tyre: {test_result['front_tyre_size']}")
        logger.info(f"       Rear tyre: {test_result['rear_tyre_size']}")
        if test_result['front_tyre']:
            logger.info(f"       Recommended: {test_result['front_tyre']['brand']} {test_result['front_tyre']['model']}")
            logger.info(f"       Price: ₹{test_result['front_tyre']['price']:.0f}")
    else:
        logger.warning("    ⚠️  Vehicle not found (this is OK if you don't have BMW data)")
    
    # Test 2: Tyre recommendations
    logger.info("\n  Test 2: Tyre Recommendations")
    # Get first tyre size from database
    if processor.tyre_database:
        test_size = list(processor.tyre_database.keys())[0]
        tyres = processor.get_tyres_by_size(test_size, budget='mid')
        logger.success(f"    ✅ Found {len(tyres)} tyres for size {test_size}")
        for i, tyre in enumerate(tyres[:3], 1):
            logger.info(f"       {i}. {tyre['brand']} {tyre['model']}: ₹{tyre['price']:.0f}")
    
    # Test 3: Brand search
    logger.info("\n  Test 3: Brand Search")
    if stats['brands']:
        test_brand = stats['brands'][0]
        brand_tyres = processor.get_tyres_by_brand(test_brand)
        logger.success(f"    ✅ Found {len(brand_tyres)} tyres from {test_brand}")
    
    # Test 4: Vehicle search
    logger.info("\n  Test 4: Vehicle Search")
    if stats['makes']:
        test_make = stats['makes'][0]
        vehicles = processor.search_vehicles(test_make)
        logger.success(f"    ✅ Found {len(vehicles)} vehicles matching '{test_make}'")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.success("✅ CSV Processing Complete!")
    logger.info("=" * 60)
    logger.info("\n📦 Generated Files:")
    logger.info("  - models/csv_data.pkl (processed data)")
    logger.info("  - models/csv_stats.json (statistics)")
    
    logger.info("\n🎯 Next Steps:")
    logger.info("  1. Run: python test_csv_integration.py")
    logger.info("  2. Run: python examples/tyreplex_csv_demo.py")
    logger.info("  3. Integrate with voice agent")
    
    logger.info("\n💡 Quick Test:")
    logger.info("  python -c \"from src.customer_service_agent.csv_tools import CSVTyrePlexTools; tools = CSVTyrePlexTools(); print(tools.get_all_brands())\"")
    
    logger.info("")


if __name__ == "__main__":
    main()
