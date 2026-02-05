"""
CSV-based tools for TyrePlex Voice Agent
Uses your actual vehicle_tyre_mapping.csv data
"""

from typing import Dict, List, Optional
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.inhouse_ml.csv_processor import CSVProcessor
from loguru import logger


class CSVTyrePlexTools:
    """
    Tools for TyrePlex voice agent using your CSV data.
    Provides instant lookups without LLM calls.
    """
    
    def __init__(self, csv_path: str = 'vehicle_tyre_mapping.csv'):
        """
        Initialize with CSV data.
        
        Args:
            csv_path: Path to your CSV file
        """
        self.csv_path = csv_path
        self.processor = None
        self._load_or_process()
    
    def _load_or_process(self):
        """Load processed data or process CSV if not available."""
        try:
            # Try to load pre-processed data
            self.processor = CSVProcessor.load_from_disk('models')
            logger.info("✅ Loaded pre-processed CSV data")
        except FileNotFoundError:
            # Process CSV for first time
            logger.info("Processing CSV for the first time...")
            self.processor = CSVProcessor(self.csv_path)
            self.processor.process_csv_chunked(chunk_size=5000)
            self.processor.save_to_disk('models')
            logger.success("✅ CSV processing complete")
    
    def identify_vehicle_tyre_size(
        self,
        vehicle_make: str,
        vehicle_model: str,
        vehicle_variant: str
    ) -> Dict:
        """
        Identify tyre size for a vehicle.
        
        Args:
            vehicle_make: e.g., "BMW", "Maruti Suzuki"
            vehicle_model: e.g., "Z4", "Swift"
            vehicle_variant: e.g., "BMW Z4 M40i Petrol AT", "VXI"
            
        Returns:
            Dictionary with tyre sizes and vehicle info
        """
        result = self.processor.get_vehicle_info(
            vehicle_make,
            vehicle_model,
            vehicle_variant
        )
        
        if not result:
            return {
                "success": False,
                "message": f"Vehicle not found: {vehicle_make} {vehicle_model} {vehicle_variant}"
            }
        
        return {
            "success": True,
            "vehicle_make": vehicle_make,
            "vehicle_model": vehicle_model,
            "vehicle_variant": vehicle_variant,
            "vehicle_type": result['vehicle_type'],
            "fuel_type": result['fuel_type'],
            "front_tyre_size": result['front_tyre_size'],
            "rear_tyre_size": result['rear_tyre_size'],
            "same_size": result['front_tyre_size'] == result['rear_tyre_size']
        }
    
    def get_tyre_recommendations(
        self,
        tyre_size: str,
        budget_range: str = "mid",
        usage_type: str = "city"
    ) -> Dict:
        """
        Get tyre recommendations for a size.
        
        Args:
            tyre_size: e.g., "255-35-19" or "255/35 R19"
            budget_range: "budget", "mid", or "premium"
            usage_type: "city", "highway", "mixed" (for filtering)
            
        Returns:
            Dictionary with tyre recommendations
        """
        tyres = self.processor.get_tyres_by_size(tyre_size, budget=budget_range)
        
        if not tyres:
            return {
                "success": False,
                "message": f"No tyres found for size: {tyre_size}"
            }
        
        # Format recommendations
        recommendations = []
        for tyre in tyres[:5]:  # Top 5 recommendations
            discount = 0
            if tyre['mrp'] > tyre['price']:
                discount = int(((tyre['mrp'] - tyre['price']) / tyre['mrp']) * 100)
            
            recommendations.append({
                "brand": tyre['brand'],
                "model": tyre['model'],
                "variant": tyre['variant'],
                "price": int(tyre['price']),
                "mrp": int(tyre['mrp']),
                "discount_percent": discount,
                "tube_type": tyre['tube_type'],
                "position": tyre['position'],
                "full_name": f"{tyre['brand']} {tyre['model']} {tyre['variant']}".strip()
            })
        
        return {
            "success": True,
            "tyre_size": tyre_size,
            "budget_range": budget_range,
            "total_options": len(tyres),
            "recommendations": recommendations
        }
    
    def compare_tyre_brands(
        self,
        tyre_size: str,
        brand1: str,
        brand2: str
    ) -> Dict:
        """
        Compare two tyre brands for a specific size.
        
        Args:
            tyre_size: Tyre size
            brand1: First brand name
            brand2: Second brand name
            
        Returns:
            Comparison dictionary
        """
        all_tyres = self.processor.get_tyres_by_size(tyre_size, budget='all')
        
        brand1_tyres = [t for t in all_tyres if t['brand'].lower() == brand1.lower()]
        brand2_tyres = [t for t in all_tyres if t['brand'].lower() == brand2.lower()]
        
        if not brand1_tyres or not brand2_tyres:
            return {
                "success": False,
                "message": f"Could not find both brands for size {tyre_size}"
            }
        
        # Get cheapest from each brand
        brand1_best = min(brand1_tyres, key=lambda x: x['price'])
        brand2_best = min(brand2_tyres, key=lambda x: x['price'])
        
        return {
            "success": True,
            "tyre_size": tyre_size,
            "brand1": {
                "name": brand1_best['brand'],
                "model": brand1_best['model'],
                "price": int(brand1_best['price']),
                "mrp": int(brand1_best['mrp'])
            },
            "brand2": {
                "name": brand2_best['brand'],
                "model": brand2_best['model'],
                "price": int(brand2_best['price']),
                "mrp": int(brand2_best['mrp'])
            },
            "price_difference": abs(int(brand1_best['price'] - brand2_best['price'])),
            "cheaper_brand": brand1 if brand1_best['price'] < brand2_best['price'] else brand2
        }
    
    def check_tyre_availability(
        self,
        tyre_brand: str,
        tyre_model: str,
        location: str
    ) -> Dict:
        """
        Check tyre availability (mock for now, can integrate with inventory).
        
        Args:
            tyre_brand: Brand name
            tyre_model: Model name
            location: Customer location
            
        Returns:
            Availability info
        """
        # For now, return mock data
        # TODO: Integrate with actual inventory system
        return {
            "success": True,
            "brand": tyre_brand,
            "model": tyre_model,
            "location": location,
            "available": True,
            "stock_count": "4+",
            "delivery_time": "Same day",
            "installation_available": True,
            "nearest_store": f"TyrePlex {location}",
            "store_distance": "2.5 km"
        }
    
    def search_vehicles(self, query: str) -> Dict:
        """
        Search for vehicles by make or model.
        
        Args:
            query: Search query
            
        Returns:
            List of matching vehicles
        """
        matches = self.processor.search_vehicles(query)
        
        if not matches:
            return {
                "success": False,
                "message": f"No vehicles found matching: {query}"
            }
        
        # Parse vehicle keys back to readable format
        vehicles = []
        for match in matches[:10]:
            parts = match.split('|')
            if len(parts) >= 3:
                vehicles.append({
                    "make": parts[0].title(),
                    "model": parts[1].title(),
                    "variant": parts[2].title()
                })
        
        return {
            "success": True,
            "query": query,
            "total_matches": len(matches),
            "vehicles": vehicles
        }
    
    def get_all_brands(self) -> Dict:
        """Get list of all available tyre brands."""
        stats = self.processor.get_statistics()
        
        return {
            "success": True,
            "total_brands": len(stats['brands']),
            "brands": stats['brands']
        }
    
    def get_price_range_tyres(
        self,
        tyre_size: str,
        min_price: int,
        max_price: int
    ) -> Dict:
        """
        Get tyres within a price range.
        
        Args:
            tyre_size: Tyre size
            min_price: Minimum price
            max_price: Maximum price
            
        Returns:
            Filtered tyres
        """
        all_tyres = self.processor.get_tyres_by_size(tyre_size, budget='all')
        
        filtered = [
            t for t in all_tyres
            if min_price <= t['price'] <= max_price
        ]
        
        if not filtered:
            return {
                "success": False,
                "message": f"No tyres found in price range ₹{min_price}-₹{max_price}"
            }
        
        recommendations = []
        for tyre in filtered[:10]:
            recommendations.append({
                "brand": tyre['brand'],
                "model": tyre['model'],
                "price": int(tyre['price']),
                "mrp": int(tyre['mrp'])
            })
        
        return {
            "success": True,
            "tyre_size": tyre_size,
            "price_range": f"₹{min_price}-₹{max_price}",
            "total_options": len(filtered),
            "recommendations": recommendations
        }


# Function definitions for OpenAI function calling
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "identify_vehicle_tyre_size",
            "description": "Identify the correct tyre size for a vehicle based on make, model, and variant",
            "parameters": {
                "type": "object",
                "properties": {
                    "vehicle_make": {
                        "type": "string",
                        "description": "Vehicle make (e.g., 'BMW', 'Maruti Suzuki', 'Hyundai')"
                    },
                    "vehicle_model": {
                        "type": "string",
                        "description": "Vehicle model (e.g., 'Z4', 'Swift', 'Creta')"
                    },
                    "vehicle_variant": {
                        "type": "string",
                        "description": "Vehicle variant (e.g., 'VXI', 'ZXI', 'M40i Petrol AT')"
                    }
                },
                "required": ["vehicle_make", "vehicle_model", "vehicle_variant"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_tyre_recommendations",
            "description": "Get tyre recommendations for a specific size and budget",
            "parameters": {
                "type": "object",
                "properties": {
                    "tyre_size": {
                        "type": "string",
                        "description": "Tyre size (e.g., '255-35-19', '185/65 R15')"
                    },
                    "budget_range": {
                        "type": "string",
                        "enum": ["budget", "mid", "premium"],
                        "description": "Budget category"
                    },
                    "usage_type": {
                        "type": "string",
                        "enum": ["city", "highway", "mixed"],
                        "description": "Primary usage type"
                    }
                },
                "required": ["tyre_size"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_tyre_brands",
            "description": "Compare two tyre brands for a specific size",
            "parameters": {
                "type": "object",
                "properties": {
                    "tyre_size": {
                        "type": "string",
                        "description": "Tyre size"
                    },
                    "brand1": {
                        "type": "string",
                        "description": "First brand name"
                    },
                    "brand2": {
                        "type": "string",
                        "description": "Second brand name"
                    }
                },
                "required": ["tyre_size", "brand1", "brand2"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_tyre_availability",
            "description": "Check if a specific tyre is available in customer's location",
            "parameters": {
                "type": "object",
                "properties": {
                    "tyre_brand": {
                        "type": "string",
                        "description": "Tyre brand"
                    },
                    "tyre_model": {
                        "type": "string",
                        "description": "Tyre model"
                    },
                    "location": {
                        "type": "string",
                        "description": "Customer location (city)"
                    }
                },
                "required": ["tyre_brand", "tyre_model", "location"]
            }
        }
    }
]


# Example usage
if __name__ == "__main__":
    # Initialize tools
    tools = CSVTyrePlexTools()
    
    # Test vehicle lookup
    print("\n🧪 Test 1: Vehicle Lookup")
    result = tools.identify_vehicle_tyre_size("BMW", "Z4", "BMW Z4 M40i Petrol AT")
    print(f"Result: {result}")
    
    # Test tyre recommendations
    if result['success']:
        print("\n🧪 Test 2: Tyre Recommendations")
        tyres = tools.get_tyre_recommendations(
            result['front_tyre_size'],
            budget_range="mid"
        )
        print(f"Found {tyres.get('total_options', 0)} options")
        if tyres['success']:
            for rec in tyres['recommendations'][:3]:
                print(f"  - {rec['brand']} {rec['model']}: ₹{rec['price']}")
    
    # Test brand comparison
    print("\n🧪 Test 3: Brand Comparison")
    comparison = tools.compare_tyre_brands("255-35-19", "Pirelli", "Bridgestone")
    print(f"Result: {comparison}")
    
    # Test search
    print("\n🧪 Test 4: Vehicle Search")
    search = tools.search_vehicles("BMW")
    print(f"Found {search.get('total_matches', 0)} vehicles")
    
    print("\n✅ All tests complete!")
