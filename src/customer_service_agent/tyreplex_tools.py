"""
TyrePlex-specific tools for call center operations.
Handles tyre recommendations, vehicle lookups, lead generation, and location services.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TyrePlexToolRegistry:
    """Registry for TyrePlex-specific tools."""
    
    tools: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tools is None:
            self.tools = {}
    
    def register(self, name: str, function: callable, schema: Dict[str, Any]):
        """Register a tool with its function and schema."""
        self.tools[name] = {"function": function, "schema": schema}
    
    def get_function(self, name: str) -> callable:
        """Get tool function by name."""
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found")
        return self.tools[name]["function"]
    
    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """Get schemas for all tools."""
        return [
            {"type": "function", "function": {**schema, "name": name}}
            for name, tool_info in self.tools.items()
            for schema in [tool_info["schema"]]
        ]


class TyrePlexTools:
    """Implementation of TyrePlex call center tools."""
    
    def __init__(self):
        self.vehicle_database = self._initialize_vehicle_db()
        self.tyre_database = self._initialize_tyre_db()
        self.location_database = self._initialize_location_db()
        self.leads = []
    
    def _initialize_vehicle_db(self) -> Dict[str, Any]:
        """Initialize vehicle database with make/model/variant/tyre size mapping."""
        return {
            "Maruti Suzuki": {
                "Swift": {
                    "LXI": {"tyre_size": "165/80 R14", "year": "2024"},
                    "VXI": {"tyre_size": "185/65 R15", "year": "2024"},
                    "ZXI": {"tyre_size": "185/65 R15", "year": "2024"},
                    "ZXI+": {"tyre_size": "185/65 R15", "year": "2024"}
                },
                "Baleno": {
                    "Sigma": {"tyre_size": "185/65 R15", "year": "2024"},
                    "Delta": {"tyre_size": "185/65 R15", "year": "2024"},
                    "Zeta": {"tyre_size": "195/55 R16", "year": "2024"},
                    "Alpha": {"tyre_size": "195/55 R16", "year": "2024"}
                },
                "Brezza": {
                    "LXI": {"tyre_size": "215/60 R16", "year": "2024"},
                    "VXI": {"tyre_size": "215/60 R16", "year": "2024"},
                    "ZXI": {"tyre_size": "215/60 R16", "year": "2024"},
                    "ZXI+": {"tyre_size": "215/60 R16", "year": "2024"}
                }
            },
            "Hyundai": {
                "Creta": {
                    "E": {"tyre_size": "215/65 R16", "year": "2024"},
                    "EX": {"tyre_size": "215/65 R16", "year": "2024"},
                    "S": {"tyre_size": "215/60 R17", "year": "2024"},
                    "SX": {"tyre_size": "215/60 R17", "year": "2024"}
                },
                "Venue": {
                    "E": {"tyre_size": "195/60 R16", "year": "2024"},
                    "S": {"tyre_size": "195/60 R16", "year": "2024"},
                    "SX": {"tyre_size": "195/60 R16", "year": "2024"}
                },
                "i20": {
                    "Magna": {"tyre_size": "185/65 R15", "year": "2024"},
                    "Sportz": {"tyre_size": "195/55 R16", "year": "2024"},
                    "Asta": {"tyre_size": "195/55 R16", "year": "2024"}
                }
            },
            "Honda": {
                "City": {
                    "V": {"tyre_size": "175/65 R15", "year": "2024"},
                    "VX": {"tyre_size": "185/55 R16", "year": "2024"},
                    "ZX": {"tyre_size": "185/55 R16", "year": "2024"}
                },
                "Amaze": {
                    "E": {"tyre_size": "175/65 R14", "year": "2024"},
                    "S": {"tyre_size": "175/65 R15", "year": "2024"},
                    "VX": {"tyre_size": "175/65 R15", "year": "2024"}
                }
            },
            "Toyota": {
                "Fortuner": {
                    "4x2": {"tyre_size": "265/65 R17", "year": "2024"},
                    "4x4": {"tyre_size": "265/60 R18", "year": "2024"}
                },
                "Innova Crysta": {
                    "GX": {"tyre_size": "205/65 R16", "year": "2024"},
                    "VX": {"tyre_size": "205/65 R16", "year": "2024"},
                    "ZX": {"tyre_size": "215/55 R17", "year": "2024"}
                }
            }
        }
    
    def _initialize_tyre_db(self) -> Dict[str, Any]:
        """Initialize tyre database with brands, models, and specifications."""
        return {
            "185/65 R15": [
                {
                    "brand": "MRF",
                    "model": "ZVTV",
                    "price": 4200,
                    "type": "Tubeless",
                    "speed_rating": "H",
                    "load_index": "88",
                    "features": ["Long tread life", "Fuel efficient", "Low noise"],
                    "best_for": "City driving"
                },
                {
                    "brand": "CEAT",
                    "model": "Milaze",
                    "price": 3800,
                    "type": "Tubeless",
                    "speed_rating": "H",
                    "load_index": "88",
                    "features": ["High mileage", "Comfortable ride", "Budget friendly"],
                    "best_for": "Daily commute"
                },
                {
                    "brand": "Apollo",
                    "model": "Amazer 4G Life",
                    "price": 4500,
                    "type": "Tubeless",
                    "speed_rating": "H",
                    "load_index": "88",
                    "features": ["All-season", "Good wet grip", "Durable"],
                    "best_for": "Mixed conditions"
                },
                {
                    "brand": "Michelin",
                    "model": "Energy XM2+",
                    "price": 6200,
                    "type": "Tubeless",
                    "speed_rating": "H",
                    "load_index": "88",
                    "features": ["Premium quality", "Excellent grip", "Long lasting"],
                    "best_for": "Performance & safety"
                }
            ],
            "215/60 R16": [
                {
                    "brand": "MRF",
                    "model": "Wanderer",
                    "price": 6500,
                    "type": "Tubeless",
                    "speed_rating": "H",
                    "load_index": "95",
                    "features": ["SUV specific", "Highway stable", "Durable"],
                    "best_for": "Highway driving"
                },
                {
                    "brand": "CEAT",
                    "model": "CrossDrive",
                    "price": 5800,
                    "type": "Tubeless",
                    "speed_rating": "H",
                    "load_index": "95",
                    "features": ["All-terrain", "Good off-road", "Comfortable"],
                    "best_for": "Mixed terrain"
                },
                {
                    "brand": "Bridgestone",
                    "model": "Dueler H/T",
                    "price": 7200,
                    "type": "Tubeless",
                    "speed_rating": "H",
                    "load_index": "95",
                    "features": ["Premium SUV tyre", "Quiet ride", "Excellent grip"],
                    "best_for": "Comfort & performance"
                }
            ]
        }
    
    def _initialize_location_db(self) -> Dict[str, Any]:
        """Initialize location database with store information."""
        return {
            "Delhi": {
                "stores": 45,
                "areas": ["Connaught Place", "Karol Bagh", "Lajpat Nagar", "Dwarka", "Rohini"],
                "same_day_delivery": True
            },
            "Mumbai": {
                "stores": 52,
                "areas": ["Andheri", "Bandra", "Thane", "Navi Mumbai", "Borivali"],
                "same_day_delivery": True
            },
            "Bangalore": {
                "stores": 38,
                "areas": ["Koramangala", "Whitefield", "Indiranagar", "JP Nagar", "Electronic City"],
                "same_day_delivery": True
            },
            "Hyderabad": {
                "stores": 28,
                "areas": ["Banjara Hills", "Hitech City", "Secunderabad", "Kukatpally"],
                "same_day_delivery": True
            },
            "Pune": {
                "stores": 22,
                "areas": ["Kothrud", "Hinjewadi", "Wakad", "Viman Nagar"],
                "same_day_delivery": False
            }
        }
    
    def get_tyre_size_for_vehicle(
        self, 
        make: str, 
        model: str, 
        variant: Optional[str] = None
    ) -> str:
        """Get recommended tyre size for a vehicle."""
        logger.info(f"Looking up tyre size for {make} {model} {variant}")
        
        make_data = self.vehicle_database.get(make)
        if not make_data:
            return json.dumps({
                "success": False,
                "message": f"Vehicle make '{make}' not found. Please provide the correct make or tell me your current tyre size.",
                "suggestion": "Popular makes: Maruti Suzuki, Hyundai, Honda, Toyota, Mahindra, Tata, KIA"
            })
        
        model_data = make_data.get(model)
        if not model_data:
            available_models = list(make_data.keys())
            return json.dumps({
                "success": False,
                "message": f"Model '{model}' not found for {make}.",
                "available_models": available_models,
                "suggestion": f"Did you mean one of these: {', '.join(available_models[:5])}?"
            })
        
        if variant:
            variant_data = model_data.get(variant)
            if variant_data:
                return json.dumps({
                    "success": True,
                    "make": make,
                    "model": model,
                    "variant": variant,
                    "tyre_size": variant_data["tyre_size"],
                    "year": variant_data["year"],
                    "message": f"The recommended tyre size for {make} {model} {variant} is {variant_data['tyre_size']}"
                })
        
        # If variant not specified or not found, return all variants
        variants = {v: data["tyre_size"] for v, data in model_data.items()}
        return json.dumps({
            "success": True,
            "make": make,
            "model": model,
            "variants": variants,
            "message": f"Please specify the variant. Available variants: {', '.join(variants.keys())}"
        })
    
    def recommend_tyres(
        self,
        tyre_size: str,
        budget: Optional[str] = "mid",
        usage: Optional[str] = "city"
    ) -> str:
        """Recommend tyres based on size, budget, and usage."""
        logger.info(f"Recommending tyres for size {tyre_size}, budget {budget}, usage {usage}")
        
        tyres = self.tyre_database.get(tyre_size)
        if not tyres:
            return json.dumps({
                "success": False,
                "message": f"No tyres found for size {tyre_size}. Please verify the tyre size.",
                "suggestion": "Common sizes: 185/65 R15, 195/55 R16, 215/60 R16, 205/65 R16"
            })
        
        # Filter by budget
        if budget == "budget":
            filtered_tyres = [t for t in tyres if t["price"] < 5000]
        elif budget == "premium":
            filtered_tyres = [t for t in tyres if t["price"] > 6000]
        else:  # mid
            filtered_tyres = tyres
        
        # Sort by price
        filtered_tyres = sorted(filtered_tyres, key=lambda x: x["price"])
        
        # Get top 3 recommendations
        recommendations = filtered_tyres[:3] if len(filtered_tyres) >= 3 else filtered_tyres
        
        return json.dumps({
            "success": True,
            "tyre_size": tyre_size,
            "budget_category": budget,
            "usage_type": usage,
            "recommendations": recommendations,
            "total_options": len(filtered_tyres),
            "message": f"Found {len(recommendations)} tyre recommendations for {tyre_size}"
        })
    
    def check_availability_location(self, city: str) -> str:
        """Check TyrePlex availability in a location."""
        logger.info(f"Checking availability in {city}")
        
        location_data = self.location_database.get(city)
        if not location_data:
            return json.dumps({
                "success": False,
                "message": f"We're expanding to {city} soon! Currently available in major cities.",
                "available_cities": list(self.location_database.keys()),
                "suggestion": "We can still deliver to your location. Delivery time: 2-3 days."
            })
        
        return json.dumps({
            "success": True,
            "city": city,
            "stores_count": location_data["stores"],
            "areas": location_data["areas"],
            "same_day_delivery": location_data["same_day_delivery"],
            "message": f"Great news! We have {location_data['stores']} partner stores in {city}. " +
                      ("Same-day delivery available!" if location_data["same_day_delivery"] else "Delivery within 24-48 hours.")
        })
    
    def create_lead(
        self,
        customer_name: str,
        phone_number: str,
        vehicle_info: str,
        tyre_size: Optional[str] = None,
        location: Optional[str] = None,
        budget: Optional[str] = None,
        urgency: Optional[str] = "within_week"
    ) -> str:
        """Create a lead for follow-up by sales team."""
        logger.info(f"Creating lead for {customer_name}")
        
        lead_id = f"LEAD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        lead_data = {
            "lead_id": lead_id,
            "customer_name": customer_name,
            "phone_number": phone_number,
            "vehicle_info": vehicle_info,
            "tyre_size": tyre_size,
            "location": location,
            "budget": budget,
            "urgency": urgency,
            "created_at": datetime.now().isoformat(),
            "status": "new",
            "source": "call_center"
        }
        
        self.leads.append(lead_data)
        
        follow_up_time = {
            "immediate": "within 30 minutes",
            "today": "within 2 hours",
            "within_week": "within 24 hours",
            "just_exploring": "within 48 hours"
        }.get(urgency, "within 24 hours")
        
        return json.dumps({
            "success": True,
            "lead_id": lead_id,
            "customer_name": customer_name,
            "follow_up_time": follow_up_time,
            "message": f"Thank you {customer_name}! Your inquiry has been registered with Lead ID: {lead_id}. " +
                      f"Our tyre expert will call you on {phone_number} {follow_up_time} with personalized recommendations and best prices."
        })
    
    def compare_tyres(
        self,
        tyre_size: str,
        brand1: str,
        brand2: str
    ) -> str:
        """Compare two tyre brands."""
        logger.info(f"Comparing {brand1} vs {brand2} for size {tyre_size}")
        
        tyres = self.tyre_database.get(tyre_size, [])
        
        tyre1 = next((t for t in tyres if t["brand"].lower() == brand1.lower()), None)
        tyre2 = next((t for t in tyres if t["brand"].lower() == brand2.lower()), None)
        
        if not tyre1 or not tyre2:
            return json.dumps({
                "success": False,
                "message": "One or both brands not available for this size",
                "available_brands": [t["brand"] for t in tyres]
            })
        
        comparison = {
            "tyre_size": tyre_size,
            "tyre1": tyre1,
            "tyre2": tyre2,
            "price_difference": abs(tyre1["price"] - tyre2["price"]),
            "cheaper_option": tyre1["brand"] if tyre1["price"] < tyre2["price"] else tyre2["brand"]
        }
        
        return json.dumps({
            "success": True,
            "comparison": comparison,
            "message": f"Comparing {brand1} {tyre1['model']} (₹{tyre1['price']}) vs {brand2} {tyre2['model']} (₹{tyre2['price']})"
        })
    
    def get_installation_info(self, service_type: str = "home") -> str:
        """Get information about installation services."""
        logger.info(f"Getting installation info for {service_type}")
        
        if service_type == "home":
            return json.dumps({
                "success": True,
                "service_type": "Home Installation",
                "timeline": "Within 24 hours of order",
                "process": [
                    "Order tyres online or over phone",
                    "Choose convenient time slot",
                    "Expert technician arrives at your location",
                    "Installation, balancing, and alignment done",
                    "Old tyres disposed (if needed)"
                ],
                "charges": "₹200-500 per tyre (included in many offers)",
                "includes": ["Installation", "Wheel balancing", "Valve replacement", "Disposal of old tyres"],
                "message": "We bring the workshop to your doorstep! Installation within 24 hours."
            })
        else:  # store
            return json.dumps({
                "success": True,
                "service_type": "Store Installation",
                "timeline": "Same day or next day",
                "process": [
                    "Order online or visit store",
                    "Book appointment slot",
                    "Visit partner store",
                    "Installation done in 30-45 minutes"
                ],
                "charges": "₹150-400 per tyre",
                "includes": ["Installation", "Wheel balancing", "Wheel alignment", "Free inspection"],
                "stores": "1000+ partner stores across India",
                "message": "Visit any of our 1000+ partner stores for quick installation!"
            })


def create_tyreplex_tool_registry() -> TyrePlexToolRegistry:
    """Create and configure the TyrePlex tool registry."""
    tools = TyrePlexTools()
    registry = TyrePlexToolRegistry()
    
    # Register all tools
    registry.register(
        name="get_tyre_size_for_vehicle",
        function=tools.get_tyre_size_for_vehicle,
        schema={
            "name": "get_tyre_size_for_vehicle",
            "description": "Get the recommended tyre size for a specific vehicle make, model, and variant",
            "parameters": {
                "type": "object",
                "properties": {
                    "make": {
                        "type": "string",
                        "description": "Vehicle make/brand (e.g., Maruti Suzuki, Hyundai, Honda)"
                    },
                    "model": {
                        "type": "string",
                        "description": "Vehicle model (e.g., Swift, Creta, City)"
                    },
                    "variant": {
                        "type": "string",
                        "description": "Vehicle variant (e.g., VXI, SX, ZX) - optional"
                    }
                },
                "required": ["make", "model"]
            }
        }
    )
    
    registry.register(
        name="recommend_tyres",
        function=tools.recommend_tyres,
        schema={
            "name": "recommend_tyres",
            "description": "Recommend tyres based on size, budget, and usage pattern",
            "parameters": {
                "type": "object",
                "properties": {
                    "tyre_size": {
                        "type": "string",
                        "description": "Tyre size (e.g., 185/65 R15, 215/60 R16)"
                    },
                    "budget": {
                        "type": "string",
                        "enum": ["budget", "mid", "premium"],
                        "description": "Budget category"
                    },
                    "usage": {
                        "type": "string",
                        "enum": ["city", "highway", "mixed", "performance"],
                        "description": "Primary usage pattern"
                    }
                },
                "required": ["tyre_size"]
            }
        }
    )
    
    registry.register(
        name="check_availability_location",
        function=tools.check_availability_location,
        schema={
            "name": "check_availability_location",
            "description": "Check TyrePlex availability and services in a specific city/location",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name (e.g., Delhi, Mumbai, Bangalore)"
                    }
                },
                "required": ["city"]
            }
        }
    )
    
    registry.register(
        name="create_lead",
        function=tools.create_lead,
        schema={
            "name": "create_lead",
            "description": "Create a lead for follow-up by sales team with customer details",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "Customer's name"
                    },
                    "phone_number": {
                        "type": "string",
                        "description": "Customer's phone number"
                    },
                    "vehicle_info": {
                        "type": "string",
                        "description": "Vehicle information (make, model, variant)"
                    },
                    "tyre_size": {
                        "type": "string",
                        "description": "Tyre size if known"
                    },
                    "location": {
                        "type": "string",
                        "description": "Customer's city/location"
                    },
                    "budget": {
                        "type": "string",
                        "description": "Budget range or preference"
                    },
                    "urgency": {
                        "type": "string",
                        "enum": ["immediate", "today", "within_week", "just_exploring"],
                        "description": "How urgently customer needs tyres"
                    }
                },
                "required": ["customer_name", "phone_number", "vehicle_info"]
            }
        }
    )
    
    registry.register(
        name="compare_tyres",
        function=tools.compare_tyres,
        schema={
            "name": "compare_tyres",
            "description": "Compare two tyre brands for a specific size",
            "parameters": {
                "type": "object",
                "properties": {
                    "tyre_size": {
                        "type": "string",
                        "description": "Tyre size to compare"
                    },
                    "brand1": {
                        "type": "string",
                        "description": "First brand name (e.g., MRF, CEAT)"
                    },
                    "brand2": {
                        "type": "string",
                        "description": "Second brand name (e.g., Apollo, Michelin)"
                    }
                },
                "required": ["tyre_size", "brand1", "brand2"]
            }
        }
    )
    
    registry.register(
        name="get_installation_info",
        function=tools.get_installation_info,
        schema={
            "name": "get_installation_info",
            "description": "Get information about tyre installation services",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_type": {
                        "type": "string",
                        "enum": ["home", "store"],
                        "description": "Type of installation service"
                    }
                },
                "required": []
            }
        }
    )
    
    return registry
