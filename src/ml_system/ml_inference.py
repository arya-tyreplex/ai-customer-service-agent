"""
ML Inference Engine for TyrePlex System
Provides predictions using trained models
"""

import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import joblib
from loguru import logger


class MLInferenceEngine:
    """
    Inference engine for TyrePlex ML models.
    Provides predictions for:
    1. Brand recommendations
    2. Price predictions
    3. Tyre size predictions
    4. Intent classification
    """
    
    def __init__(self, model_dir: str = 'models', data_dir: str = 'data/processed'):
        self.model_dir = model_dir
        self.data_dir = data_dir
        self.models = {}
        self.encoders = {}
        self.scalers = {}
        self._load_models()
    
    def _load_models(self):
        """Load all trained models and preprocessors."""
        logger.info("Loading ML models...")
        
        try:
            # Load encoders and scalers
            self.encoders = pickle.load(open(f'{self.data_dir}/encoders.pkl', 'rb'))
            self.scalers = pickle.load(open(f'{self.data_dir}/scalers.pkl', 'rb'))
            
            # Load models
            model_files = {
                'brand_recommender': 'brand_recommender.pkl',
                'price_predictor': 'price_predictor.pkl',
                'size_predictor': 'size_predictor.pkl',
                'intent_classifier': 'intent_classifier.pkl'
            }
            
            for model_name, filename in model_files.items():
                model_path = Path(self.model_dir) / filename
                if model_path.exists():
                    self.models[model_name] = joblib.load(model_path)
                    logger.success(f"✅ Loaded {model_name}")
                else:
                    logger.warning(f"⚠️  Model not found: {filename}")
            
            logger.success(f"✅ Loaded {len(self.models)} models")
            
        except Exception as e:
            logger.error(f"❌ Error loading models: {e}")
            logger.info("Please run: python src/ml_system/model_trainer.py")
            raise
    
    def recommend_brand(
        self,
        vehicle_make: str,
        vehicle_model: str,
        vehicle_type: str,
        fuel_type: str,
        vehicle_price: float,
        tyre_size: str,
        top_k: int = 3
    ) -> List[Dict]:
        """
        Recommend tyre brands based on vehicle information.
        
        Args:
            vehicle_make: Vehicle manufacturer
            vehicle_model: Vehicle model
            vehicle_type: Type (Car, SUV, etc.)
            fuel_type: Fuel type (Petrol, Diesel, etc.)
            vehicle_price: Vehicle price
            tyre_size: Required tyre size
            top_k: Number of recommendations
            
        Returns:
            List of recommended brands with confidence scores
        """
        if 'brand_recommender' not in self.models:
            return []
        
        try:
            # Prepare features
            features = pd.DataFrame({
                'vehicle_make': [vehicle_make],
                'vehicle_model': [vehicle_model],
                'vehicle_type': [vehicle_type],
                'fuel_type': [fuel_type],
                'vehicle_price': [vehicle_price],
                'tyre_size': [tyre_size],
                'tyre_width': [0],  # Default values
                'rim_size': [0]
            })
            
            # Encode categorical features
            for col in ['vehicle_make', 'vehicle_model', 'vehicle_type', 'fuel_type', 'tyre_size']:
                if col in self.encoders:
                    try:
                        features[col] = self.encoders[col].transform(features[col].astype(str))
                    except:
                        features[col] = 0  # Unknown category
            
            # Scale numerical features
            numerical_cols = ['vehicle_price', 'tyre_width', 'rim_size']
            if 'brand_scaler' in self.scalers:
                features[numerical_cols] = self.scalers['brand_scaler'].transform(features[numerical_cols])
            
            # Predict
            model = self.models['brand_recommender']
            probabilities = model.predict_proba(features)[0]
            
            # Get top K predictions
            top_indices = np.argsort(probabilities)[-top_k:][::-1]
            
            recommendations = []
            for idx in top_indices:
                brand = self.encoders['brand'].inverse_transform([idx])[0]
                confidence = probabilities[idx]
                
                recommendations.append({
                    'brand': brand,
                    'confidence': float(confidence),
                    'confidence_percent': float(confidence * 100)
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in brand recommendation: {e}")
            return []
    
    def predict_price(
        self,
        vehicle_make: str,
        vehicle_model: str,
        vehicle_type: str,
        vehicle_price: float,
        tyre_brand: str,
        tyre_size: str
    ) -> Dict:
        """
        Predict tyre price based on vehicle and tyre information.
        
        Returns:
            Dictionary with predicted price and confidence interval
        """
        if 'price_predictor' not in self.models:
            return {'predicted_price': 0, 'error': 'Model not loaded'}
        
        try:
            # Prepare features
            features = pd.DataFrame({
                'vehicle_make': [vehicle_make],
                'vehicle_model': [vehicle_model],
                'vehicle_type': [vehicle_type],
                'vehicle_price': [vehicle_price],
                'tyre_brand': [tyre_brand],
                'tyre_size': [tyre_size],
                'tyre_width': [0],
                'aspect_ratio': [0],
                'rim_size': [0],
                'tube_type': ['Tubeless']
            })
            
            # Encode categorical features
            for col in ['vehicle_make', 'vehicle_model', 'vehicle_type', 'tyre_brand', 'tyre_size', 'tube_type']:
                encoder_key = f'price_{col}'
                if encoder_key in self.encoders:
                    try:
                        features[col] = self.encoders[encoder_key].transform(features[col].astype(str))
                    except:
                        features[col] = 0
            
            # Scale numerical features
            numerical_cols = ['vehicle_price', 'tyre_width', 'aspect_ratio', 'rim_size']
            if 'price_scaler' in self.scalers:
                features[numerical_cols] = self.scalers['price_scaler'].transform(features[numerical_cols])
            
            # Predict
            model = self.models['price_predictor']
            predicted_price = model.predict(features)[0]
            
            # Calculate confidence interval (±10%)
            lower_bound = predicted_price * 0.9
            upper_bound = predicted_price * 1.1
            
            return {
                'predicted_price': float(predicted_price),
                'price_range': {
                    'min': float(lower_bound),
                    'max': float(upper_bound)
                },
                'formatted_price': f"₹{predicted_price:,.0f}"
            }
            
        except Exception as e:
            logger.error(f"Error in price prediction: {e}")
            return {'predicted_price': 0, 'error': str(e)}
    
    def predict_tyre_size(
        self,
        vehicle_make: str,
        vehicle_model: str,
        vehicle_variant: str,
        vehicle_type: str,
        fuel_type: str,
        vehicle_price: float
    ) -> Dict:
        """
        Predict tyre size for a vehicle.
        
        Returns:
            Dictionary with predicted tyre size and confidence
        """
        if 'size_predictor' not in self.models:
            return {'tyre_size': None, 'error': 'Model not loaded'}
        
        try:
            # Prepare features
            features = pd.DataFrame({
                'vehicle_make': [vehicle_make],
                'vehicle_model': [vehicle_model],
                'vehicle_variant': [vehicle_variant],
                'vehicle_type': [vehicle_type],
                'fuel_type': [fuel_type],
                'vehicle_price': [vehicle_price]
            })
            
            # Encode categorical features
            for col in ['vehicle_make', 'vehicle_model', 'vehicle_variant', 'vehicle_type', 'fuel_type']:
                encoder_key = f'size_{col}'
                if encoder_key in self.encoders:
                    try:
                        features[col] = self.encoders[encoder_key].transform(features[col].astype(str))
                    except:
                        features[col] = 0
            
            # Scale numerical features
            if 'size_scaler' in self.scalers:
                features[['vehicle_price']] = self.scalers['size_scaler'].transform(features[['vehicle_price']])
            
            # Predict
            model = self.models['size_predictor']
            prediction = model.predict(features)[0]
            probabilities = model.predict_proba(features)[0]
            
            # Get tyre size
            tyre_size = self.encoders['tyre_size'].inverse_transform([prediction])[0]
            confidence = probabilities[prediction]
            
            return {
                'tyre_size': tyre_size,
                'confidence': float(confidence),
                'confidence_percent': float(confidence * 100)
            }
            
        except Exception as e:
            logger.error(f"Error in size prediction: {e}")
            return {'tyre_size': None, 'error': str(e)}
    
    def classify_intent(self, text: str) -> Dict:
        """
        Classify customer intent from text.
        
        Args:
            text: Customer message
            
        Returns:
            Dictionary with intent and confidence
        """
        if 'intent_classifier' not in self.models:
            return {'intent': 'unknown', 'error': 'Model not loaded'}
        
        try:
            # Vectorize text
            if 'intent_vectorizer' in self.encoders:
                features = self.encoders['intent_vectorizer'].transform([text])
                features_df = pd.DataFrame(features.toarray())
            else:
                return {'intent': 'unknown', 'error': 'Vectorizer not loaded'}
            
            # Predict
            model = self.models['intent_classifier']
            prediction = model.predict(features_df)[0]
            probabilities = model.predict_proba(features_df)[0]
            
            # Get intent
            intent = self.encoders['intent'].inverse_transform([prediction])[0]
            confidence = probabilities[prediction]
            
            # Get top 3 intents
            top_indices = np.argsort(probabilities)[-3:][::-1]
            top_intents = []
            for idx in top_indices:
                intent_name = self.encoders['intent'].inverse_transform([idx])[0]
                top_intents.append({
                    'intent': intent_name,
                    'confidence': float(probabilities[idx]),
                    'confidence_percent': float(probabilities[idx] * 100)
                })
            
            return {
                'intent': intent,
                'confidence': float(confidence),
                'confidence_percent': float(confidence * 100),
                'top_intents': top_intents
            }
            
        except Exception as e:
            logger.error(f"Error in intent classification: {e}")
            return {'intent': 'unknown', 'error': str(e)}
    
    def get_complete_recommendation(
        self,
        vehicle_make: str,
        vehicle_model: str,
        vehicle_variant: str,
        vehicle_type: str,
        fuel_type: str,
        vehicle_price: float
    ) -> Dict:
        """
        Get complete recommendation including size, brands, and prices.
        
        Returns:
            Complete recommendation dictionary
        """
        result = {
            'vehicle': {
                'make': vehicle_make,
                'model': vehicle_model,
                'variant': vehicle_variant,
                'type': vehicle_type,
                'fuel_type': fuel_type
            }
        }
        
        # Predict tyre size
        size_prediction = self.predict_tyre_size(
            vehicle_make, vehicle_model, vehicle_variant,
            vehicle_type, fuel_type, vehicle_price
        )
        result['tyre_size'] = size_prediction
        
        if size_prediction.get('tyre_size'):
            tyre_size = size_prediction['tyre_size']
            
            # Recommend brands
            brand_recommendations = self.recommend_brand(
                vehicle_make, vehicle_model, vehicle_type,
                fuel_type, vehicle_price, tyre_size, top_k=5
            )
            result['recommended_brands'] = brand_recommendations
            
            # Predict prices for each brand
            brand_prices = []
            for brand_rec in brand_recommendations:
                price_pred = self.predict_price(
                    vehicle_make, vehicle_model, vehicle_type,
                    vehicle_price, brand_rec['brand'], tyre_size
                )
                brand_prices.append({
                    'brand': brand_rec['brand'],
                    'confidence': brand_rec['confidence_percent'],
                    'predicted_price': price_pred.get('predicted_price', 0),
                    'price_range': price_pred.get('price_range', {}),
                    'formatted_price': price_pred.get('formatted_price', 'N/A')
                })
            
            result['brand_prices'] = brand_prices
        
        return result


# CLI usage and testing
if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("TyrePlex ML Inference Engine - Testing")
    logger.info("=" * 70)
    
    # Initialize engine
    engine = MLInferenceEngine()
    
    # Test 1: Brand recommendation
    logger.info("\n🧪 Test 1: Brand Recommendation")
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
        logger.success("✅ Brand recommendations:")
        for i, brand in enumerate(brands, 1):
            logger.info(f"  {i}. {brand['brand']} (Confidence: {brand['confidence_percent']:.1f}%)")
    
    # Test 2: Price prediction
    logger.info("\n🧪 Test 2: Price Prediction")
    price = engine.predict_price(
        vehicle_make="Maruti Suzuki",
        vehicle_model="Swift",
        vehicle_type="Hatchback",
        vehicle_price=700000,
        tyre_brand="MRF",
        tyre_size="185/65 R15"
    )
    
    if 'predicted_price' in price:
        logger.success(f"✅ Predicted price: {price['formatted_price']}")
        logger.info(f"   Range: ₹{price['price_range']['min']:,.0f} - ₹{price['price_range']['max']:,.0f}")
    
    # Test 3: Tyre size prediction
    logger.info("\n🧪 Test 3: Tyre Size Prediction")
    size = engine.predict_tyre_size(
        vehicle_make="Maruti Suzuki",
        vehicle_model="Swift",
        vehicle_variant="VXI",
        vehicle_type="Hatchback",
        fuel_type="Petrol",
        vehicle_price=700000
    )
    
    if size.get('tyre_size'):
        logger.success(f"✅ Predicted size: {size['tyre_size']}")
        logger.info(f"   Confidence: {size['confidence_percent']:.1f}%")
    
    # Test 4: Intent classification
    logger.info("\n🧪 Test 4: Intent Classification")
    test_phrases = [
        "I have a BMW Z4",
        "What is the price of MRF tyres",
        "Compare Apollo and CEAT",
        "I want to book an appointment"
    ]
    
    for phrase in test_phrases:
        intent = engine.classify_intent(phrase)
        if 'intent' in intent:
            logger.success(f"✅ '{phrase}'")
            logger.info(f"   Intent: {intent['intent']} ({intent['confidence_percent']:.1f}%)")
    
    # Test 5: Complete recommendation
    logger.info("\n🧪 Test 5: Complete Recommendation")
    complete = engine.get_complete_recommendation(
        vehicle_make="Maruti Suzuki",
        vehicle_model="Swift",
        vehicle_variant="VXI",
        vehicle_type="Hatchback",
        fuel_type="Petrol",
        vehicle_price=700000
    )
    
    logger.success("✅ Complete recommendation generated")
    if complete.get('tyre_size'):
        logger.info(f"   Tyre size: {complete['tyre_size']['tyre_size']}")
    if complete.get('brand_prices'):
        logger.info(f"   Top brands with prices:")
        for bp in complete['brand_prices'][:3]:
            logger.info(f"     - {bp['brand']}: {bp['formatted_price']}")
    
    logger.success("\n✅ All tests complete!")
