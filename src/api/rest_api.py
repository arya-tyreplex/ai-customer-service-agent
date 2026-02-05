"""
REST API for TyrePlex System
No external API dependencies - all in-house
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from flask import Flask, request, jsonify
from flask_cors import CORS
from src.customer_service_agent.integrated_agent import IntegratedTyrePlexAgent
from src.inhouse_ml.mongodb_manager import MongoDBManager
from loguru import logger
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize agent
try:
    agent = IntegratedTyrePlexAgent()
    logger.success("✅ Agent initialized")
except Exception as e:
    logger.error(f"❌ Agent initialization failed: {e}")
    agent = None

# Initialize database (optional - only if MongoDB is running)
try:
    db = MongoDBManager()
    logger.success("✅ Database connected")
except Exception as e:
    logger.warning(f"⚠️  Database not available: {e}")
    db = None

logger.success("✅ REST API initialized")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'TyrePlex AI System',
        'version': '1.0.0'
    })


@app.route('/api/vehicle/identify', methods=['POST'])
def identify_vehicle():
    """
    Identify vehicle and get tyre recommendations.
    
    Request:
    {
        "make": "Maruti Suzuki",
        "model": "Swift",
        "variant": "VXI",
        "budget_range": "mid"
    }
    """
    try:
        if not agent:
            return jsonify({
                'success': False,
                'error': 'Agent not initialized. Run: ./run.sh prepare && ./run.sh train'
            }), 503
        
        data = request.json
        
        result = agent.identify_vehicle_and_recommend(
            data['make'],
            data['model'],
            data['variant'],
            data.get('budget_range', 'mid')
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/vehicle/search', methods=['GET'])
def search_vehicles():
    """
    Search vehicles by query.
    
    Query params: ?q=BMW
    """
    try:
        if not agent:
            return jsonify({
                'success': False,
                'error': 'Agent not initialized'
            }), 503
        
        query = request.args.get('q', '')
        vehicles = agent.search_vehicles(query)
        
        return jsonify({
            'success': True,
            'data': vehicles
        })
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/tyres/compare', methods=['POST'])
def compare_brands():
    """
    Compare two tyre brands.
    
    Request:
    {
        "tyre_size": "185/65 R15",
        "brand1": "MRF",
        "brand2": "CEAT"
    }
    """
    try:
        if not agent:
            return jsonify({
                'success': False,
                'error': 'Agent not initialized'
            }), 503
        
        data = request.json
        
        result = agent.compare_brands(
            data['tyre_size'],
            data['brand1'],
            data['brand2']
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/tyres/price-range', methods=['GET'])
def get_price_range():
    """
    Get tyres in price range.
    
    Query params: ?size=185/65 R15&min=3000&max=5000
    """
    try:
        if not agent:
            return jsonify({
                'success': False,
                'error': 'Agent not initialized'
            }), 503
        
        size = request.args.get('size')
        min_price = int(request.args.get('min', 0))
        max_price = int(request.args.get('max', 100000))
        
        result = agent.get_price_range_options(size, min_price, max_price)
        
        return jsonify({
            'success': True,
            'data': result
        })
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/brands', methods=['GET'])
def get_brands():
    """Get all available brands."""
    try:
        if not agent:
            return jsonify({
                'success': False,
                'error': 'Agent not initialized'
            }), 503
        
        brands = agent.get_all_brands()
        
        return jsonify({
            'success': True,
            'data': brands
        })
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/intent/classify', methods=['POST'])
def classify_intent():
    """
    Classify customer intent using in-house ML.
    
    Request:
    {
        "text": "I have a BMW Z4"
    }
    """
    try:
        if not agent:
            return jsonify({
                'success': False,
                'error': 'Agent not initialized'
            }), 503
        
        data = request.json
        result = agent.classify_customer_intent(data['text'])
        
        return jsonify({
            'success': True,
            'data': result
        })
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/lead/create', methods=['POST'])
def create_lead():
    """
    Create a new lead.
    
    Request:
    {
        "name": "Rahul Sharma",
        "phone": "9876543210",
        "vehicle_make": "Maruti Suzuki",
        "vehicle_model": "Swift",
        "tyre_size": "185/65 R15"
    }
    """
    try:
        if not db:
            return jsonify({
                'success': False,
                'error': 'Database not available. Start services: ./run.sh services'
            }), 503
        
        data = request.json
        lead_id = db.create_lead(data)
        
        return jsonify({
            'success': True,
            'lead_id': lead_id
        })
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/booking/create', methods=['POST'])
def create_booking():
    """
    Create a new booking.
    
    Request:
    {
        "lead_id": "...",
        "booking_date": "2024-01-15",
        "tyre_brand": "MRF",
        "quantity": 4
    }
    """
    try:
        if not db:
            return jsonify({
                'success': False,
                'error': 'Database not available. Start services: ./run.sh services'
            }), 503
        
        data = request.json
        booking_id = db.create_booking(data)
        
        return jsonify({
            'success': True,
            'booking_id': booking_id
        })
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """Get system statistics."""
    try:
        stats = {}
        
        if db:
            stats['database'] = db.get_statistics()
        else:
            stats['database'] = {'status': 'not_available'}
        
        if agent:
            stats['agent'] = agent.get_system_status()
        else:
            stats['agent'] = {'status': 'not_available'}
        
        return jsonify({
            'success': True,
            'data': stats
        })
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


# Run server
if __name__ == '__main__':
    port = int(os.getenv('APP_PORT', 5000))
    debug = os.getenv('DEBUG', 'True') == 'True'
    
    logger.info(f"🚀 Starting REST API on port {port}")
    logger.info(f"📝 API Documentation: http://localhost:{port}/health")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
