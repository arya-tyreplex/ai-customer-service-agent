"""
Integrated TyrePlex Agent
Combines ML predictions with CSV lookups for best results
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from typing import Dict, List, Optional
from loguru import logger

# Import ML engine
try:
    from src.ml_system.ml_inference import MLInferenceEngine
    ML_AVAILABLE = True
except:
    ML_AVAILABLE = False
    logger.warning("⚠️  ML models not available")

# Import CSV tools
try:
    from src.customer_service_agent.csv_tools import CSVTyrePlexTools
    CSV_AVAILABLE = True
except:
    CSV_AVAILABLE = False
    logger.warning("⚠️  CSV data not available")


class IntegratedTyrePlexAgent:
    """
    Integrated agent that combines:
    1. ML predictions for recommendations
    2. CSV lookups for exact data
    3. Fallback mechanisms for robustness
    """
    
    def __init__(self):
        """Initialize both ML and CSV systems."""
        self.ml_engine = None
        self.csv_tools = None
        
        # Initialize ML engine
        if ML_AVAILABLE:
            try:
                self.ml_engine = MLInferenceEngine()
                logger.success("✅ ML engine initialized")
            except Exception as e:
                logger.warning(f"⚠️  ML engine not available: {e}")
        
        # Initialize CSV tools
        if CSV_AVAILABLE:
            try:
                self.csv_tools = CSVTyrePlexTools()
                logger.success("✅ CSV tools initialized")
            except Exception as e:
                logger.warning(f"⚠️  CSV tools not available: {e}")
        
        if not self.ml_engine and not self.csv_tools:
            logger.error("❌ Neither ML nor CSV systems available!")
            logger.info("Please run: python train_complete_system.py")
    
    def identify_vehicle_and_recommend(
        self,
        vehicle_make: str,
        vehicle_model: str,
        vehicle_variant: str,
        budget_range: str = "mid"
    ) -> Dict:
        """
        Complete vehicle identification and recommendation.
        Uses CSV for exact lookup, ML for predictions.
        """
        result = {
            'vehicle': {
                'make': vehicle_make,
                'model': vehicle_model,
                'variant': vehicle_variant
            },
            'source': None,
            'tyre_size': None,
            'recommendations': []
        }
        
        # Try CSV first (exact data)
        if self.csv_tools:
            csv_result = self.csv_tools.identify_vehicle_tyre_size(
                vehicle_make, vehicle_model, vehicle_variant
            )
            
            if csv_result.get('success'):
                result['source'] = 'csv'
                result['tyre_size'] = {
                    'front': csv_result['front_tyre_size'],
                    'rear': csv_result['rear_tyre_size'],
                    'same_size': csv_result['same_size']
                }
                result['vehicle_type'] = csv_result.get('vehicle_type')
                result['fuel_type'] = csv_result.get('fuel_type')
                
                # Get tyre recommendations from CSV
                tyres = self.csv_tools.get_tyre_recommendations(
                    csv_result['front_tyre_size'],
                    budget_range=budget_range
                )
                
                if tyres.get('success'):
                    result['recommendations'] = tyres['recommendations']
                    result['total_options'] = tyres['total_options']
                
                return result
        
        # Fallback to ML predictions
        if self.ml_engine:
            logger.info("Using ML predictions (CSV lookup failed)")
            
            # Predict tyre size
            size_pred = self.ml_engine.predict_tyre_size(
                vehicle_make, vehicle_model, vehicle_variant,
                "Car", "Petrol", 1000000  # Default values
            )
            
            if size_pred.get('tyre_size'):
                result['source'] = 'ml'
                result['tyre_size'] = {
                    'front': size_pred['tyre_size'],
                    'rear': size_pred['tyre_size'],
                    'same_size': True,
                    'confidence': size_pred.get('confidence_percent', 0)
                }
                
                # Get brand recommendations from ML
                brands = self.ml_engine.recommend_brand(
                    vehicle_make, vehicle_model, "Car",
                    "Petrol", 1000000, size_pred['tyre_size'],
                    top_k=5
                )
                
                # Get price predictions for each brand
                recommendations = []
                for brand in brands:
                    price_pred = self.ml_engine.predict_price(
                        vehicle_make, vehicle_model, "Car",
                        1000000, brand['brand'], size_pred['tyre_size']
                    )
                    
                    recommendations.append({
                        'brand': brand['brand'],
                        'model': 'Predicted',
                        'price': int(price_pred.get('predicted_price', 0)),
                        'confidence': brand['confidence_percent'],
                        'source': 'ml'
                    })
                
                result['recommendations'] = recommendations
                
                return result
        
        # No data available
        result['error'] = 'Vehicle not found in database'
        return result
    
    def compare_brands(
        self,
        tyre_size: str,
        brand1: str,
        brand2: str
    ) -> Dict:
        """Compare two brands using CSV data or ML predictions."""
        
        # Try CSV first
        if self.csv_tools:
            comparison = self.csv_tools.compare_tyre_brands(
                tyre_size, brand1, brand2
            )
            
            if comparison.get('success'):
                comparison['source'] = 'csv'
                return comparison
        
        # Fallback to ML
        if self.ml_engine:
            logger.info("Using ML for brand comparison")
            
            price1 = self.ml_engine.predict_price(
                "Generic", "Model", "Car", 1000000,
                brand1, tyre_size
            )
            
            price2 = self.ml_engine.predict_price(
                "Generic", "Model", "Car", 1000000,
                brand2, tyre_size
            )
            
            return {
                'success': True,
                'source': 'ml',
                'tyre_size': tyre_size,
                'brand1': {
                    'name': brand1,
                    'price': int(price1.get('predicted_price', 0))
                },
                'brand2': {
                    'name': brand2,
                    'price': int(price2.get('predicted_price', 0))
                },
                'price_difference': abs(
                    int(price1.get('predicted_price', 0)) -
                    int(price2.get('predicted_price', 0))
                ),
                'cheaper_brand': brand1 if price1.get('predicted_price', 0) < price2.get('predicted_price', 0) else brand2
            }
        
        return {'success': False, 'error': 'No data available'}
    
    def classify_customer_intent(self, text: str) -> Dict:
        """Classify customer intent using ML."""
        
        if self.ml_engine:
            return self.ml_engine.classify_intent(text)
        
        # Simple rule-based fallback
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['have', 'my car', 'my vehicle', 'drive']):
            return {'intent': 'vehicle_inquiry', 'confidence': 0.7, 'source': 'rules'}
        elif any(word in text_lower for word in ['price', 'cost', 'how much']):
            return {'intent': 'price_inquiry', 'confidence': 0.7, 'source': 'rules'}
        elif any(word in text_lower for word in ['compare', 'vs', 'difference']):
            return {'intent': 'brand_comparison', 'confidence': 0.7, 'source': 'rules'}
        elif any(word in text_lower for word in ['book', 'appointment', 'schedule']):
            return {'intent': 'booking_request', 'confidence': 0.7, 'source': 'rules'}
        elif any(word in text_lower for word in ['available', 'stock', 'delivery']):
            return {'intent': 'availability_check', 'confidence': 0.7, 'source': 'rules'}
        else:
            return {'intent': 'tyre_recommendation', 'confidence': 0.5, 'source': 'rules'}
    
    def get_price_range_options(
        self,
        tyre_size: str,
        min_price: int,
        max_price: int
    ) -> Dict:
        """Get tyres in price range."""
        
        if self.csv_tools:
            return self.csv_tools.get_price_range_tyres(
                tyre_size, min_price, max_price
            )
        
        return {'success': False, 'error': 'CSV data not available'}
    
    def check_availability(
        self,
        brand: str,
        model: str,
        location: str
    ) -> Dict:
        """Check tyre availability."""
        
        if self.csv_tools:
            return self.csv_tools.check_tyre_availability(
                brand, model, location
            )
        
        # Mock response
        return {
            'success': True,
            'available': True,
            'brand': brand,
            'model': model,
            'location': location,
            'delivery_time': 'Same day',
            'source': 'mock'
        }
    
    def get_all_brands(self) -> List[str]:
        """Get list of all available brands."""
        
        if self.csv_tools:
            result = self.csv_tools.get_all_brands()
            if result.get('success'):
                return result['brands']
        
        # Default brands
        return [
            'MRF', 'CEAT', 'Apollo', 'Bridgestone', 'Michelin',
            'JK Tyre', 'Goodyear', 'Pirelli', 'Continental', 'Yokohama'
        ]
    
    def search_vehicles(self, query: str) -> List[Dict]:
        """Search for vehicles."""
        
        if self.csv_tools:
            result = self.csv_tools.search_vehicles(query)
            if result.get('success'):
                return result['vehicles']
        
        return []
    
    def get_system_status(self) -> Dict:
        """Get status of integrated systems."""
        return {
            'ml_available': self.ml_engine is not None,
            'csv_available': self.csv_tools is not None,
            'ml_models': list(self.ml_engine.models.keys()) if self.ml_engine else [],
            'recommendation': 'Both systems available' if (self.ml_engine and self.csv_tools) else 'Limited functionality'
        }


# Testing
if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("Integrated TyrePlex Agent - Testing")
    logger.info("=" * 70)
    
    # Initialize agent
    agent = IntegratedTyrePlexAgent()
    
    # Check status
    status = agent.get_system_status()
    logger.info("\n📊 System Status:")
    logger.info(f"  ML Available: {status['ml_available']}")
    logger.info(f"  CSV Available: {status['csv_available']}")
    logger.info(f"  Status: {status['recommendation']}")
    
    # Test vehicle identification
    logger.info("\n🧪 Test 1: Vehicle Identification & Recommendation")
    result = agent.identify_vehicle_and_recommend(
        "Maruti Suzuki", "Swift", "VXI", "mid"
    )
    
    if result.get('tyre_size'):
        logger.success(f"✅ Vehicle identified (Source: {result['source']})")
        logger.info(f"   Tyre size: {result['tyre_size']['front']}")
        if result.get('recommendations'):
            logger.info(f"   Top recommendation: {result['recommendations'][0]['brand']}")
    
    # Test intent classification
    logger.info("\n🧪 Test 2: Intent Classification")
    intent = agent.classify_customer_intent("I have a BMW Z4")
    logger.success(f"✅ Intent: {intent['intent']} (Confidence: {intent.get('confidence_percent', intent.get('confidence', 0)*100):.1f}%)")
    
    # Test brand comparison
    logger.info("\n🧪 Test 3: Brand Comparison")
    comparison = agent.compare_brands("185/65 R15", "MRF", "CEAT")
    if comparison.get('success'):
        logger.success(f"✅ Comparison complete (Source: {comparison.get('source', 'unknown')})")
        logger.info(f"   Cheaper: {comparison['cheaper_brand']}")
    
    logger.success("\n✅ All tests complete!")
