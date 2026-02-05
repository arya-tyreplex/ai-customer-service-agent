"""
Data processor for TyrePlex CSV data.
Handles vehicle and tyre data processing for ML models.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import joblib
from pathlib import Path


class TyrePlexDataProcessor:
    """Process TyrePlex CSV data for ML models."""
    
    def __init__(self, csv_path: str):
        """
        Initialize data processor.
        
        Args:
            csv_path: Path to your CSV file
        """
        self.csv_path = csv_path
        self.df = None
        self.vehicle_lookup = {}
        self.tyre_lookup = {}
        
    def load_data(self) -> pd.DataFrame:
        """Load and validate CSV data."""
        print("Loading CSV data...")
        
        self.df = pd.read_csv(self.csv_path)
        
        # Validate required columns
        required_cols = [
            'Vehicle Make', 'Vehicle Model', 'Vehicle Variant',
            'Front Tyre Size (Vehicle Spec)', 'Rear Tyre Size (Vehicle Spec)',
            'Front Tyre Brand', 'Front Tyre Model', 'Front Tyre Price',
            'Rear Tyre Brand', 'Rear Tyre Model', 'Rear Tyre Price',
            'Vehicle Type', 'Fuel Type'
        ]
        
        missing = [col for col in required_cols if col not in self.df.columns]
        if missing:
            raise ValueError(f"Missing columns: {missing}")
        
        print(f"✅ Loaded {len(self.df)} records")
        print(f"✅ Unique vehicles: {self.df['Vehicle Make'].nunique()}")
        print(f"✅ Unique tyre brands: {self.df['Front Tyre Brand'].nunique()}")
        
        return self.df
    
    def create_vehicle_lookup(self) -> Dict:
        """
        Create fast vehicle lookup dictionary.
        
        Returns:
            Dictionary: {vehicle_key: tyre_info}
        """
        print("\nCreating vehicle lookup table...")
        
        for _, row in self.df.iterrows():
            # Create unique key
            key = self._create_vehicle_key(
                row['Vehicle Make'],
                row['Vehicle Model'],
                row['Vehicle Variant']
            )
            
            # Store tyre information
            self.vehicle_lookup[key] = {
                'front_tyre_size': row['Front Tyre Size (Vehicle Spec)'],
                'rear_tyre_size': row['Rear Tyre Size (Vehicle Spec)'],
                'vehicle_type': row['Vehicle Type'],
                'fuel_type': row['Fuel Type'],
                'vehicle_price': row.get('Vehicle Price', 0),
                
                # Front tyre recommendations
                'front_tyre_brand': row['Front Tyre Brand'],
                'front_tyre_model': row['Front Tyre Model'],
                'front_tyre_variant': row.get('Front Tyre Variant', ''),
                'front_tyre_price': row['Front Tyre Price'],
                'front_tyre_mrp': row.get('Front Tyre MRP', row['Front Tyre Price']),
                
                # Rear tyre recommendations
                'rear_tyre_brand': row['Rear Tyre Brand'],
                'rear_tyre_model': row['Rear Tyre Model'],
                'rear_tyre_variant': row.get('Rear Tyre Variant', ''),
                'rear_tyre_price': row['Rear Tyre Price'],
                'rear_tyre_mrp': row.get('Rear Tyre MRP', row['Rear Tyre Price']),
                
                # Tube type
                'tube_type': row.get('Tube type', 'Tubeless')
            }
        
        print(f"✅ Created lookup for {len(self.vehicle_lookup)} vehicle variants")
        return self.vehicle_lookup
    
    def create_tyre_database(self) -> Dict:
        """
        Create tyre database grouped by size.
        
        Returns:
            Dictionary: {tyre_size: [list of tyres]}
        """
        print("\nCreating tyre database...")
        
        # Process front tyres
        for _, row in self.df.iterrows():
            size = row['Front Tyre Size (Vehicle Spec)']
            
            if size not in self.tyre_lookup:
                self.tyre_lookup[size] = []
            
            tyre_info = {
                'brand': row['Front Tyre Brand'],
                'model': row['Front Tyre Model'],
                'variant': row.get('Front Tyre Variant', ''),
                'width': row.get('Front Tyre Width', ''),
                'aspect_ratio': row.get('Front Tyre Aspect Ratio', ''),
                'rim_size': row.get('Front Rim Size', ''),
                'price': row['Front Tyre Price'],
                'mrp': row.get('Front Tyre MRP', row['Front Tyre Price']),
                'tube_type': row.get('Tube type', 'Tubeless'),
                'position': 'front'
            }
            
            # Avoid duplicates
            if tyre_info not in self.tyre_lookup[size]:
                self.tyre_lookup[size].append(tyre_info)
        
        # Process rear tyres (if different from front)
        for _, row in self.df.iterrows():
            size = row['Rear Tyre Size (Vehicle Spec)']
            
            if size not in self.tyre_lookup:
                self.tyre_lookup[size] = []
            
            tyre_info = {
                'brand': row['Rear Tyre Brand'],
                'model': row['Rear Tyre Model'],
                'variant': row.get('Rear Tyre Variant', ''),
                'width': row.get('Rear Tyre Width', ''),
                'aspect_ratio': row.get('Rear Tyre Aspect Ratio', ''),
                'rim_size': row.get('Rear Rim Size', ''),
                'price': row['Rear Tyre Price'],
                'mrp': row.get('Rear Tyre MRP', row['Rear Tyre Price']),
                'tube_type': row.get('Tube type', 'Tubeless'),
                'position': 'rear'
            }
            
            if tyre_info not in self.tyre_lookup[size]:
                self.tyre_lookup[size].append(tyre_info)
        
        print(f"✅ Created database for {len(self.tyre_lookup)} tyre sizes")
        return self.tyre_lookup
    
    def _create_vehicle_key(self, make: str, model: str, variant: str) -> str:
        """Create normalized vehicle key."""
        return f"{make}|{model}|{variant}".lower().strip()
    
    def get_tyre_size(self, make: str, model: str, variant: str) -> Dict:
        """
        Get tyre size for a vehicle.
        
        Args:
            make: Vehicle make (e.g., "Maruti Suzuki")
            model: Vehicle model (e.g., "Swift")
            variant: Vehicle variant (e.g., "VXI")
            
        Returns:
            Dictionary with front and rear tyre sizes
        """
        key = self._create_vehicle_key(make, model, variant)
        
        if key in self.vehicle_lookup:
            return {
                'front_size': self.vehicle_lookup[key]['front_tyre_size'],
                'rear_size': self.vehicle_lookup[key]['rear_tyre_size'],
                'vehicle_type': self.vehicle_lookup[key]['vehicle_type']
            }
        
        return None
    
    def get_tyre_recommendations(
        self,
        tyre_size: str,
        budget: str = 'mid',
        position: str = 'front'
    ) -> List[Dict]:
        """
        Get tyre recommendations for a size.
        
        Args:
            tyre_size: Tyre size (e.g., "185/65 R15")
            budget: 'budget', 'mid', or 'premium'
            position: 'front' or 'rear'
            
        Returns:
            List of recommended tyres
        """
        if tyre_size not in self.tyre_lookup:
            return []
        
        tyres = self.tyre_lookup[tyre_size]
        
        # Filter by position if specified
        if position:
            tyres = [t for t in tyres if t['position'] == position or t['position'] == 'both']
        
        # Sort by price
        tyres_sorted = sorted(tyres, key=lambda x: x['price'])
        
        # Filter by budget
        if budget == 'budget':
            # Bottom 30%
            cutoff = int(len(tyres_sorted) * 0.3)
            return tyres_sorted[:max(cutoff, 3)]
        elif budget == 'premium':
            # Top 30%
            cutoff = int(len(tyres_sorted) * 0.7)
            return tyres_sorted[cutoff:]
        else:  # mid
            # Middle 40%
            start = int(len(tyres_sorted) * 0.3)
            end = int(len(tyres_sorted) * 0.7)
            return tyres_sorted[start:end] if end > start else tyres_sorted
    
    def prepare_ml_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Prepare data for ML model training.
        
        Returns:
            Tuple of (features_df, targets_df)
        """
        print("\nPreparing ML training data...")
        
        # Create features
        features = []
        targets = []
        
        for _, row in self.df.iterrows():
            # Features
            feature_dict = {
                'vehicle_make': row['Vehicle Make'],
                'vehicle_model': row['Vehicle Model'],
                'vehicle_type': row['Vehicle Type'],
                'fuel_type': row['Fuel Type'],
                'vehicle_price': row.get('Vehicle Price', 0),
                'front_tyre_size': row['Front Tyre Size (Vehicle Spec)'],
            }
            
            # Target (tyre brand to recommend)
            target_dict = {
                'front_tyre_brand': row['Front Tyre Brand'],
                'front_tyre_model': row['Front Tyre Model'],
                'front_tyre_price': row['Front Tyre Price'],
            }
            
            features.append(feature_dict)
            targets.append(target_dict)
        
        features_df = pd.DataFrame(features)
        targets_df = pd.DataFrame(targets)
        
        print(f"✅ Prepared {len(features_df)} training samples")
        
        return features_df, targets_df
    
    def save_lookups(self, output_dir: str = 'models'):
        """Save lookup tables for fast inference."""
        Path(output_dir).mkdir(exist_ok=True)
        
        joblib.dump(self.vehicle_lookup, f'{output_dir}/vehicle_lookup.pkl')
        joblib.dump(self.tyre_lookup, f'{output_dir}/tyre_lookup.pkl')
        
        print(f"\n✅ Saved lookup tables to {output_dir}/")
    
    def get_statistics(self) -> Dict:
        """Get data statistics."""
        if self.df is None:
            return {}
        
        return {
            'total_records': len(self.df),
            'unique_makes': self.df['Vehicle Make'].nunique(),
            'unique_models': self.df['Vehicle Model'].nunique(),
            'unique_variants': self.df['Vehicle Variant'].nunique(),
            'unique_tyre_brands': self.df['Front Tyre Brand'].nunique(),
            'unique_tyre_sizes': self.df['Front Tyre Size (Vehicle Spec)'].nunique(),
            'price_range': {
                'min': self.df['Front Tyre Price'].min(),
                'max': self.df['Front Tyre Price'].max(),
                'mean': self.df['Front Tyre Price'].mean()
            },
            'vehicle_types': self.df['Vehicle Type'].value_counts().to_dict()
        }


# Example usage
if __name__ == "__main__":
    # Initialize processor
    processor = TyrePlexDataProcessor('data/tyreplex_data.csv')
    
    # Load data
    df = processor.load_data()
    
    # Create lookups
    vehicle_lookup = processor.create_vehicle_lookup()
    tyre_lookup = processor.create_tyre_database()
    
    # Test vehicle lookup
    result = processor.get_tyre_size("Maruti Suzuki", "Swift", "VXI")
    print(f"\nTest lookup: {result}")
    
    # Test tyre recommendations
    if result:
        recommendations = processor.get_tyre_recommendations(
            result['front_size'],
            budget='mid'
        )
        print(f"\nRecommendations: {len(recommendations)} tyres found")
        for tyre in recommendations[:3]:
            print(f"  - {tyre['brand']} {tyre['model']}: ₹{tyre['price']}")
    
    # Save lookups
    processor.save_lookups()
    
    # Print statistics
    stats = processor.get_statistics()
    print(f"\n📊 Data Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
