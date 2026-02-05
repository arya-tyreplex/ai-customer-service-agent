"""
Dataset Builder for TyrePlex ML System
Prepares training data from CSV for ML models
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import pickle
from loguru import logger


class DatasetBuilder:
    """
    Builds ML-ready datasets from TyrePlex CSV.
    Creates features for multiple ML tasks:
    1. Brand recommendation
    2. Price prediction
    3. Tyre size prediction
    4. Customer intent classification
    """
    
    def __init__(self, csv_path: str = 'vehicle_tyre_mapping.csv'):
        self.csv_path = csv_path
        self.df = None
        self.encoders = {}
        self.scalers = {}
        
    def load_and_clean_data(self) -> pd.DataFrame:
        """Load and clean CSV data."""
        logger.info(f"Loading data from {self.csv_path}...")
        
        # Read CSV in chunks for large files
        chunks = []
        chunk_size = 10000
        
        for chunk in pd.read_csv(self.csv_path, chunksize=chunk_size, low_memory=False):
            chunks.append(chunk)
        
        self.df = pd.concat(chunks, ignore_index=True)
        logger.success(f"✅ Loaded {len(self.df)} records")
        
        # Clean data
        logger.info("Cleaning data...")
        
        # Remove rows with missing critical data
        critical_cols = [
            'Vehicle Make', 'Vehicle Model', 'Vehicle Variant',
            'Front Tyre Size (Vehicle Spec)', 'Front Tyre Brand',
            'Front Tyre Price'
        ]
        
        initial_count = len(self.df)
        self.df = self.df.dropna(subset=critical_cols)
        logger.info(f"Removed {initial_count - len(self.df)} rows with missing data")
        
        # Remove rows with zero prices
        self.df = self.df[self.df['Front Tyre Price'] > 0]
        
        # Fill missing values
        self.df['Vehicle Price'] = self.df['Vehicle Price'].fillna(0)
        self.df['Front Tyre MRP'] = self.df['Front Tyre MRP'].fillna(self.df['Front Tyre Price'])
        self.df['Rear Tyre Price'] = self.df['Rear Tyre Price'].fillna(self.df['Front Tyre Price'])
        
        logger.success(f"✅ Cleaned data: {len(self.df)} records remaining")
        
        return self.df
    
    def create_brand_recommendation_dataset(self) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Create dataset for brand recommendation model.
        
        Features: Vehicle make, model, type, fuel type, price range, tyre size
        Target: Tyre brand
        """
        logger.info("\n📊 Creating brand recommendation dataset...")
        
        # Features
        features = pd.DataFrame({
            'vehicle_make': self.df['Vehicle Make'],
            'vehicle_model': self.df['Vehicle Model'],
            'vehicle_type': self.df['Vehicle Type'],
            'fuel_type': self.df['Fuel Type'],
            'vehicle_price': self.df['Vehicle Price'],
            'tyre_size': self.df['Front Tyre Size (Vehicle Spec)'],
            'tyre_width': self.df.get('Front Tyre Width', 0),
            'rim_size': self.df.get('Front Rim Size', 0)
        })
        
        # Target
        target = self.df['Front Tyre Brand']
        
        # Encode categorical features
        for col in ['vehicle_make', 'vehicle_model', 'vehicle_type', 'fuel_type', 'tyre_size']:
            if col not in self.encoders:
                self.encoders[col] = LabelEncoder()
                features[col] = self.encoders[col].fit_transform(features[col].astype(str))
            else:
                features[col] = self.encoders[col].transform(features[col].astype(str))
        
        # Encode target
        if 'brand' not in self.encoders:
            self.encoders['brand'] = LabelEncoder()
            target = self.encoders['brand'].fit_transform(target.astype(str))
        else:
            target = self.encoders['brand'].transform(target.astype(str))
        
        # Scale numerical features
        numerical_cols = ['vehicle_price', 'tyre_width', 'rim_size']
        if 'brand_scaler' not in self.scalers:
            self.scalers['brand_scaler'] = StandardScaler()
            features[numerical_cols] = self.scalers['brand_scaler'].fit_transform(features[numerical_cols])
        else:
            features[numerical_cols] = self.scalers['brand_scaler'].transform(features[numerical_cols])
        
        logger.success(f"✅ Created dataset: {len(features)} samples, {len(features.columns)} features")
        logger.info(f"   Unique brands: {len(np.unique(target))}")
        
        return features, pd.Series(target)
    
    def create_price_prediction_dataset(self) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Create dataset for price prediction model.
        
        Features: Vehicle info, tyre brand, model, size, specifications
        Target: Tyre price
        """
        logger.info("\n📊 Creating price prediction dataset...")
        
        # Features
        features = pd.DataFrame({
            'vehicle_make': self.df['Vehicle Make'],
            'vehicle_model': self.df['Vehicle Model'],
            'vehicle_type': self.df['Vehicle Type'],
            'vehicle_price': self.df['Vehicle Price'],
            'tyre_brand': self.df['Front Tyre Brand'],
            'tyre_size': self.df['Front Tyre Size (Vehicle Spec)'],
            'tyre_width': self.df.get('Front Tyre Width', 0),
            'aspect_ratio': self.df.get('Front Tyre Aspect Ratio', 0),
            'rim_size': self.df.get('Front Rim Size', 0),
            'tube_type': self.df.get('Front Tyre Type', 'Tubeless')
        })
        
        # Target
        target = self.df['Front Tyre Price']
        
        # Encode categorical features
        for col in ['vehicle_make', 'vehicle_model', 'vehicle_type', 'tyre_brand', 'tyre_size', 'tube_type']:
            if f'price_{col}' not in self.encoders:
                self.encoders[f'price_{col}'] = LabelEncoder()
                features[col] = self.encoders[f'price_{col}'].fit_transform(features[col].astype(str))
            else:
                features[col] = self.encoders[f'price_{col}'].transform(features[col].astype(str))
        
        # Scale numerical features
        numerical_cols = ['vehicle_price', 'tyre_width', 'aspect_ratio', 'rim_size']
        if 'price_scaler' not in self.scalers:
            self.scalers['price_scaler'] = StandardScaler()
            features[numerical_cols] = self.scalers['price_scaler'].fit_transform(features[numerical_cols])
        else:
            features[numerical_cols] = self.scalers['price_scaler'].transform(features[numerical_cols])
        
        logger.success(f"✅ Created dataset: {len(features)} samples, {len(features.columns)} features")
        logger.info(f"   Price range: ₹{target.min():.0f} - ₹{target.max():.0f}")
        logger.info(f"   Mean price: ₹{target.mean():.0f}")
        
        return features, target
    
    def create_tyre_size_prediction_dataset(self) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Create dataset for tyre size prediction.
        
        Features: Vehicle make, model, variant, type
        Target: Tyre size
        """
        logger.info("\n📊 Creating tyre size prediction dataset...")
        
        # Features
        features = pd.DataFrame({
            'vehicle_make': self.df['Vehicle Make'],
            'vehicle_model': self.df['Vehicle Model'],
            'vehicle_variant': self.df['Vehicle Variant'],
            'vehicle_type': self.df['Vehicle Type'],
            'fuel_type': self.df['Fuel Type'],
            'vehicle_price': self.df['Vehicle Price']
        })
        
        # Target
        target = self.df['Front Tyre Size (Vehicle Spec)']
        
        # Encode categorical features
        for col in ['vehicle_make', 'vehicle_model', 'vehicle_variant', 'vehicle_type', 'fuel_type']:
            if f'size_{col}' not in self.encoders:
                self.encoders[f'size_{col}'] = LabelEncoder()
                features[col] = self.encoders[f'size_{col}'].fit_transform(features[col].astype(str))
            else:
                features[col] = self.encoders[f'size_{col}'].transform(features[col].astype(str))
        
        # Encode target
        if 'tyre_size' not in self.encoders:
            self.encoders['tyre_size'] = LabelEncoder()
            target = self.encoders['tyre_size'].fit_transform(target.astype(str))
        else:
            target = self.encoders['tyre_size'].transform(target.astype(str))
        
        # Scale numerical features
        if 'size_scaler' not in self.scalers:
            self.scalers['size_scaler'] = StandardScaler()
            features[['vehicle_price']] = self.scalers['size_scaler'].fit_transform(features[['vehicle_price']])
        else:
            features[['vehicle_price']] = self.scalers['size_scaler'].transform(features[['vehicle_price']])
        
        logger.success(f"✅ Created dataset: {len(features)} samples, {len(features.columns)} features")
        logger.info(f"   Unique tyre sizes: {len(np.unique(target))}")
        
        return features, pd.Series(target)
    
    def create_intent_classification_dataset(self) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Create synthetic dataset for customer intent classification.
        
        Intents: 
        - vehicle_inquiry (asking about vehicle)
        - tyre_recommendation (asking for tyre suggestions)
        - price_inquiry (asking about prices)
        - brand_comparison (comparing brands)
        - availability_check (checking stock)
        - booking_request (want to book)
        """
        logger.info("\n📊 Creating intent classification dataset...")
        
        # Synthetic training data
        intents_data = {
            'vehicle_inquiry': [
                'I have a BMW Z4',
                'What size tyres for Maruti Swift',
                'My car is Hyundai Creta',
                'I drive a Honda City',
                'Tell me about tyres for my vehicle',
                'Which tyres fit my car',
                'I need tyres for my bike',
                'What tyres does my vehicle need'
            ],
            'tyre_recommendation': [
                'Suggest good tyres',
                'What are the best tyres',
                'Recommend tyres for city driving',
                'I need budget tyres',
                'Show me premium options',
                'What tyres do you recommend',
                'Best tyres for highway',
                'Good tyres for my budget'
            ],
            'price_inquiry': [
                'How much does it cost',
                'What is the price',
                'How much for MRF tyres',
                'Price of Apollo tyres',
                'What is your rate',
                'How much will it cost',
                'Price range for tyres',
                'Cost of installation'
            ],
            'brand_comparison': [
                'Compare MRF and CEAT',
                'Which is better Michelin or Bridgestone',
                'Difference between Apollo and MRF',
                'MRF vs CEAT which is good',
                'Compare these brands',
                'Which brand is better',
                'Tell me about brand differences',
                'Compare tyre brands'
            ],
            'availability_check': [
                'Is it available',
                'Do you have stock',
                'Available in Mumbai',
                'When can I get it',
                'Is it in stock',
                'Can I get it today',
                'Delivery time',
                'How soon can you deliver'
            ],
            'booking_request': [
                'I want to book',
                'Book an appointment',
                'Schedule installation',
                'I will take it',
                'Book for tomorrow',
                'Make a booking',
                'Reserve for me',
                'I want to buy'
            ]
        }
        
        # Create dataset
        texts = []
        labels = []
        
        for intent, phrases in intents_data.items():
            for phrase in phrases:
                texts.append(phrase)
                labels.append(intent)
        
        # Create features (simple bag of words for now)
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        if 'intent_vectorizer' not in self.encoders:
            self.encoders['intent_vectorizer'] = TfidfVectorizer(max_features=100)
            features = self.encoders['intent_vectorizer'].fit_transform(texts)
        else:
            features = self.encoders['intent_vectorizer'].transform(texts)
        
        features_df = pd.DataFrame(features.toarray())
        
        # Encode labels
        if 'intent' not in self.encoders:
            self.encoders['intent'] = LabelEncoder()
            labels = self.encoders['intent'].fit_transform(labels)
        else:
            labels = self.encoders['intent'].transform(labels)
        
        logger.success(f"✅ Created dataset: {len(features_df)} samples, {len(features_df.columns)} features")
        logger.info(f"   Unique intents: {len(np.unique(labels))}")
        
        return features_df, pd.Series(labels)
    
    def split_dataset(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Tuple:
        """Split dataset into train and test sets."""
        return train_test_split(X, y, test_size=test_size, random_state=random_state)
    
    def save_datasets(self, output_dir: str = 'data/processed'):
        """Save all processed datasets."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"\n💾 Saving datasets to {output_dir}/...")
        
        # Brand recommendation
        X_brand, y_brand = self.create_brand_recommendation_dataset()
        X_brand_train, X_brand_test, y_brand_train, y_brand_test = self.split_dataset(X_brand, y_brand)
        
        pickle.dump((X_brand_train, X_brand_test, y_brand_train, y_brand_test),
                   open(f'{output_dir}/brand_dataset.pkl', 'wb'))
        logger.success(f"✅ Saved brand recommendation dataset")
        
        # Price prediction
        X_price, y_price = self.create_price_prediction_dataset()
        X_price_train, X_price_test, y_price_train, y_price_test = self.split_dataset(X_price, y_price)
        
        pickle.dump((X_price_train, X_price_test, y_price_train, y_price_test),
                   open(f'{output_dir}/price_dataset.pkl', 'wb'))
        logger.success(f"✅ Saved price prediction dataset")
        
        # Tyre size prediction
        X_size, y_size = self.create_tyre_size_prediction_dataset()
        X_size_train, X_size_test, y_size_train, y_size_test = self.split_dataset(X_size, y_size)
        
        pickle.dump((X_size_train, X_size_test, y_size_train, y_size_test),
                   open(f'{output_dir}/size_dataset.pkl', 'wb'))
        logger.success(f"✅ Saved tyre size prediction dataset")
        
        # Intent classification
        X_intent, y_intent = self.create_intent_classification_dataset()
        X_intent_train, X_intent_test, y_intent_train, y_intent_test = self.split_dataset(X_intent, y_intent)
        
        pickle.dump((X_intent_train, X_intent_test, y_intent_train, y_intent_test),
                   open(f'{output_dir}/intent_dataset.pkl', 'wb'))
        logger.success(f"✅ Saved intent classification dataset")
        
        # Save encoders and scalers
        pickle.dump(self.encoders, open(f'{output_dir}/encoders.pkl', 'wb'))
        pickle.dump(self.scalers, open(f'{output_dir}/scalers.pkl', 'wb'))
        logger.success(f"✅ Saved encoders and scalers")
        
        logger.success(f"\n✅ All datasets saved to {output_dir}/")
    
    def get_dataset_statistics(self) -> Dict:
        """Get statistics about the datasets."""
        if self.df is None:
            return {}
        
        return {
            'total_records': len(self.df),
            'unique_vehicles': self.df['Vehicle Make'].nunique(),
            'unique_models': self.df['Vehicle Model'].nunique(),
            'unique_brands': self.df['Front Tyre Brand'].nunique(),
            'unique_sizes': self.df['Front Tyre Size (Vehicle Spec)'].nunique(),
            'price_stats': {
                'min': float(self.df['Front Tyre Price'].min()),
                'max': float(self.df['Front Tyre Price'].max()),
                'mean': float(self.df['Front Tyre Price'].mean()),
                'median': float(self.df['Front Tyre Price'].median())
            },
            'vehicle_types': self.df['Vehicle Type'].value_counts().to_dict(),
            'top_brands': self.df['Front Tyre Brand'].value_counts().head(10).to_dict()
        }


# CLI usage
if __name__ == "__main__":
    import sys
    
    logger.info("=" * 70)
    logger.info("TyrePlex Dataset Builder")
    logger.info("=" * 70)
    
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
    
    # Create and save all datasets
    builder.save_datasets()
    
    logger.success("\n✅ Dataset preparation complete!")
    logger.info("\nNext step: python src/ml_system/model_trainer.py")
