"""
CSV Data Processor for TyrePlex Vehicle-Tyre Mapping
Handles your actual CSV with 35 columns and large dataset (50MB+)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path
import pickle
from collections import defaultdict
from loguru import logger


class CSVProcessor:
    """
    Processes your vehicle_tyre_mapping.csv file.
    Optimized for large files (50MB+) with chunked processing.
    """
    
    def __init__(self, csv_path: str = 'vehicle_tyre_mapping.csv'):
        self.csv_path = csv_path
        self.vehicle_lookup = defaultdict(list)
        self.tyre_database = defaultdict(list)
        self.brand_index = defaultdict(list)
        self.make_model_index = defaultdict(set)
        self.stats = {
            'total_records': 0,
            'unique_vehicles': set(),
            'unique_brands': set(),
            'price_range': {'min': float('inf'), 'max': 0}
        }
        
    def process_csv_chunked(self, chunk_size: int = 10000):
        """
        Process large CSV in chunks to avoid memory issues.
        
        Args:
            chunk_size: Number of rows per chunk
        """
        logger.info(f"Processing CSV: {self.csv_path}")
        logger.info(f"Chunk size: {chunk_size} rows")
        
        chunk_num = 0
        
        try:
            for chunk in pd.read_csv(self.csv_path, chunksize=chunk_size, low_memory=False):
                chunk_num += 1
                logger.info(f"Processing chunk {chunk_num} ({len(chunk)} rows)...")
                
                self._process_chunk(chunk)
                
                if chunk_num % 10 == 0:
                    logger.info(f"Processed {self.stats['total_records']} records so far...")
                    
        except Exception as e:
            logger.error(f"Error processing CSV: {e}")
            raise
        
        logger.success(f"✅ Processed {self.stats['total_records']} total records")
        logger.success(f"✅ Unique vehicles: {len(self.stats['unique_vehicles'])}")
        logger.success(f"✅ Unique brands: {len(self.stats['unique_brands'])}")
        
    def _process_chunk(self, chunk: pd.DataFrame):
        """Process a single chunk of data."""
        for idx, row in chunk.iterrows():
            try:
                self._process_row(row)
                self.stats['total_records'] += 1
            except Exception as e:
                logger.warning(f"Error processing row {idx}: {e}")
                continue
    
    def _process_row(self, row: pd.Series):
        """Process a single row from CSV."""
        # Extract vehicle info
        make = str(row['Vehicle Make']).strip()
        model = str(row['Vehicle Model']).strip()
        variant = str(row['Vehicle Variant']).strip()
        
        vehicle_key = self._create_key(make, model, variant)
        self.stats['unique_vehicles'].add(vehicle_key)
        
        # Index by make and model for fuzzy search
        self.make_model_index[make.lower()].add(model)
        
        # Extract tyre sizes
        front_size = str(row['Front Tyre Size (Vehicle Spec)']).strip()
        rear_size = str(row['Rear Tyre Size (Vehicle Spec)']).strip()
        
        # Process front tyre
        front_tyre = self._extract_tyre_info(row, 'Front')
        if front_tyre:
            self.stats['unique_brands'].add(front_tyre['brand'])
            self._update_price_range(front_tyre['price'])
            
            # Add to vehicle lookup
            self.vehicle_lookup[vehicle_key].append({
                'vehicle_type': str(row.get('Vehicle Type', '')),
                'fuel_type': str(row.get('Fuel Type', '')),
                'vehicle_price': self._safe_float(row.get('Vehicle Price', 0)),
                'front_tyre_size': front_size,
                'rear_tyre_size': rear_size,
                'front_tyre': front_tyre,
                'rear_tyre': None  # Will be added below
            })
            
            # Add to tyre database
            self.tyre_database[front_size].append(front_tyre)
            
            # Index by brand
            self.brand_index[front_tyre['brand'].lower()].append(front_tyre)
        
        # Process rear tyre
        rear_tyre = self._extract_tyre_info(row, 'Rear')
        if rear_tyre:
            self.stats['unique_brands'].add(rear_tyre['brand'])
            self._update_price_range(rear_tyre['price'])
            
            # Update vehicle lookup with rear tyre
            if self.vehicle_lookup[vehicle_key]:
                self.vehicle_lookup[vehicle_key][-1]['rear_tyre'] = rear_tyre
            
            # Add to tyre database
            self.tyre_database[rear_size].append(rear_tyre)
            
            # Index by brand
            self.brand_index[rear_tyre['brand'].lower()].append(rear_tyre)
    
    def _extract_tyre_info(self, row: pd.Series, position: str) -> Optional[Dict]:
        """Extract tyre information from row."""
        try:
            brand = str(row[f'{position} Tyre Brand']).strip()
            if not brand or brand == 'nan':
                return None
            
            price = self._safe_float(row[f'{position} Tyre Price'])
            if price == 0:
                return None
            
            return {
                'brand': brand,
                'model': str(row.get(f'{position} Tyre Model', '')).strip(),
                'variant': str(row.get(f'{position} Tyre Variant', '')).strip(),
                'width': str(row.get(f'{position} Tyre Width', '')).strip(),
                'aspect_ratio': str(row.get(f'{position} Tyre Aspect Ratio', '')).strip(),
                'rim_size': str(row.get(f'{position} Rim Size', '')).strip(),
                'tube_type': str(row.get(f'{position} Tyre Type', 'Tubeless')).strip(),
                'price': price,
                'mrp': self._safe_float(row.get(f'{position} Tyre MRP', price)),
                'position': position.lower(),
                'brand_id': str(row.get(f'{position} Tyre Brand ID', '')),
                'model_id': str(row.get(f'{position} Tyre Model ID', '')),
                'variant_id': str(row.get(f'{position} Tyre Variant ID', ''))
            }
        except Exception as e:
            logger.debug(f"Error extracting {position} tyre: {e}")
            return None
    
    def _create_key(self, *parts) -> str:
        """Create normalized lookup key."""
        return '|'.join(str(p).lower().strip() for p in parts)
    
    def _safe_float(self, value) -> float:
        """Safely convert to float."""
        try:
            return float(value) if value and str(value) != 'nan' else 0.0
        except:
            return 0.0
    
    def _update_price_range(self, price: float):
        """Update price statistics."""
        if price > 0:
            self.stats['price_range']['min'] = min(self.stats['price_range']['min'], price)
            self.stats['price_range']['max'] = max(self.stats['price_range']['max'], price)
    
    def get_vehicle_info(self, make: str, model: str, variant: str) -> Optional[Dict]:
        """
        Get vehicle and tyre information.
        
        Args:
            make: Vehicle make (e.g., "BMW")
            model: Vehicle model (e.g., "Z4")
            variant: Vehicle variant (e.g., "BMW Z4 M40i Petrol AT")
            
        Returns:
            Dictionary with vehicle and tyre info, or None if not found
        """
        key = self._create_key(make, model, variant)
        results = self.vehicle_lookup.get(key, [])
        
        if results:
            return results[0]  # Return first match
        return None
    
    def get_all_vehicle_options(self, make: str, model: str, variant: str) -> List[Dict]:
        """Get all tyre options for a vehicle."""
        key = self._create_key(make, model, variant)
        return self.vehicle_lookup.get(key, [])
    
    def get_tyres_by_size(self, tyre_size: str, budget: str = 'all') -> List[Dict]:
        """
        Get tyres by size with optional budget filter.
        
        Args:
            tyre_size: Tyre size (e.g., "255-35-19" or "255/35 R19")
            budget: 'budget', 'mid', 'premium', or 'all'
            
        Returns:
            List of tyres sorted by price
        """
        # Normalize tyre size (handle both formats)
        normalized_size = tyre_size.replace('/', '-').replace(' R', '-').replace('R', '-')
        
        tyres = self.tyre_database.get(tyre_size, [])
        if not tyres:
            # Try normalized format
            tyres = self.tyre_database.get(normalized_size, [])
        
        if not tyres:
            return []
        
        # Remove duplicates based on brand + model + variant
        unique_tyres = []
        seen = set()
        for tyre in tyres:
            key = f"{tyre['brand']}|{tyre['model']}|{tyre['variant']}"
            if key not in seen:
                seen.add(key)
                unique_tyres.append(tyre)
        
        # Sort by price
        sorted_tyres = sorted(unique_tyres, key=lambda x: x['price'])
        
        # Filter by budget
        if budget == 'budget':
            cutoff = max(3, int(len(sorted_tyres) * 0.3))
            return sorted_tyres[:cutoff]
        elif budget == 'premium':
            cutoff = int(len(sorted_tyres) * 0.7)
            return sorted_tyres[cutoff:]
        elif budget == 'mid':
            start = int(len(sorted_tyres) * 0.3)
            end = int(len(sorted_tyres) * 0.7)
            return sorted_tyres[start:end] if end > start else sorted_tyres[:5]
        else:
            return sorted_tyres
    
    def get_tyres_by_brand(self, brand: str) -> List[Dict]:
        """Get all tyres from a specific brand."""
        return self.brand_index.get(brand.lower(), [])
    
    def search_vehicles(self, query: str) -> List[str]:
        """
        Search for vehicles by make or model.
        
        Args:
            query: Search query (e.g., "BMW", "Swift")
            
        Returns:
            List of matching vehicle keys
        """
        query_lower = query.lower()
        matches = []
        
        for vehicle_key in self.vehicle_lookup.keys():
            if query_lower in vehicle_key:
                matches.append(vehicle_key)
        
        return matches[:20]  # Limit results
    
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics."""
        return {
            'total_records': self.stats['total_records'],
            'unique_vehicles': len(self.stats['unique_vehicles']),
            'unique_brands': len(self.stats['unique_brands']),
            'unique_tyre_sizes': len(self.tyre_database),
            'price_range': {
                'min': self.stats['price_range']['min'],
                'max': self.stats['price_range']['max']
            },
            'brands': sorted(list(self.stats['unique_brands'])),
            'makes': sorted(list(self.make_model_index.keys()))
        }
    
    def save_to_disk(self, output_dir: str = 'models'):
        """Save processed data to disk."""
        Path(output_dir).mkdir(exist_ok=True)
        
        logger.info(f"Saving processed data to {output_dir}/...")
        
        # Convert defaultdicts to regular dicts for pickling
        data = {
            'vehicle_lookup': dict(self.vehicle_lookup),
            'tyre_database': dict(self.tyre_database),
            'brand_index': dict(self.brand_index),
            'make_model_index': {k: list(v) for k, v in self.make_model_index.items()},
            'stats': self.stats
        }
        
        with open(f'{output_dir}/csv_data.pkl', 'wb') as f:
            pickle.dump(data, f)
        
        # Also save as JSON for inspection
        json_data = {
            'stats': {
                'total_records': self.stats['total_records'],
                'unique_vehicles': len(self.stats['unique_vehicles']),
                'unique_brands': len(self.stats['unique_brands']),
                'unique_tyre_sizes': len(self.tyre_database),
                'price_range': self.stats['price_range']
            },
            'brands': sorted(list(self.stats['unique_brands'])),
            'makes': sorted(list(self.make_model_index.keys()))
        }
        
        with open(f'{output_dir}/csv_stats.json', 'w') as f:
            json.dump(json_data, f, indent=2)
        
        logger.success(f"✅ Saved to {output_dir}/csv_data.pkl")
        logger.success(f"✅ Saved stats to {output_dir}/csv_stats.json")
    
    @classmethod
    def load_from_disk(cls, input_dir: str = 'models') -> 'CSVProcessor':
        """Load processed data from disk."""
        processor = cls()
        
        with open(f'{input_dir}/csv_data.pkl', 'rb') as f:
            data = pickle.load(f)
        
        processor.vehicle_lookup = defaultdict(list, data['vehicle_lookup'])
        processor.tyre_database = defaultdict(list, data['tyre_database'])
        processor.brand_index = defaultdict(list, data['brand_index'])
        processor.make_model_index = defaultdict(set, {
            k: set(v) for k, v in data['make_model_index'].items()
        })
        processor.stats = data['stats']
        
        logger.success(f"✅ Loaded processed data from {input_dir}/")
        return processor


# CLI usage
if __name__ == "__main__":
    import sys
    
    # Initialize processor
    processor = CSVProcessor('vehicle_tyre_mapping.csv')
    
    # Process CSV
    logger.info("Starting CSV processing...")
    processor.process_csv_chunked(chunk_size=5000)
    
    # Print statistics
    stats = processor.get_statistics()
    logger.info("\n📊 Data Statistics:")
    logger.info(f"  Total records: {stats['total_records']}")
    logger.info(f"  Unique vehicles: {stats['unique_vehicles']}")
    logger.info(f"  Unique brands: {stats['unique_brands']}")
    logger.info(f"  Unique tyre sizes: {stats['unique_tyre_sizes']}")
    logger.info(f"  Price range: ₹{stats['price_range']['min']:.0f} - ₹{stats['price_range']['max']:.0f}")
    logger.info(f"  Brands: {', '.join(stats['brands'][:10])}...")
    
    # Save to disk
    processor.save_to_disk()
    
    # Test lookup
    logger.info("\n🧪 Testing lookups...")
    test_result = processor.get_vehicle_info("BMW", "Z4", "BMW Z4 M40i Petrol AT")
    if test_result:
        logger.success(f"✅ Test lookup successful!")
        logger.info(f"  Front tyre: {test_result['front_tyre_size']}")
        logger.info(f"  Rear tyre: {test_result['rear_tyre_size']}")
        if test_result['front_tyre']:
            logger.info(f"  Recommended: {test_result['front_tyre']['brand']} {test_result['front_tyre']['model']}")
    
    logger.success("\n✅ Processing complete!")
