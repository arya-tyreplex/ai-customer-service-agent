"""
Elasticsearch Indexer for TyrePlex System
Syncs data from MongoDB to Elasticsearch for fast search
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from typing import Dict, List
from loguru import logger
import os
from dotenv import load_dotenv
from src.inhouse_ml.mongodb_manager import MongoDBManager

# Load environment variables
load_dotenv()


class ElasticsearchIndexer:
    """
    Elasticsearch indexer for TyrePlex.
    Syncs vehicles and tyres from MongoDB to ES for fast fuzzy search.
    """
    
    def __init__(self, es_host: str = None):
        """
        Initialize Elasticsearch connection.
        
        Args:
            es_host: Elasticsearch host (default: localhost:9200)
        """
        self.es_host = es_host or os.getenv('ELASTICSEARCH_HOST', 'localhost:9200')
        self.es = None
        self.db = MongoDBManager()
        self._connect()
    
    def _connect(self):
        """Connect to Elasticsearch."""
        try:
            # Debug: print the host
            logger.info(f"Attempting to connect to ES at: {self.es_host}")
            
            self.es = Elasticsearch([f'http://{self.es_host}'])
            
            # Test connection with info() instead of ping()
            info = self.es.info()
            if info:
                logger.success(f"✅ Connected to Elasticsearch: {self.es_host}")
                logger.info(f"   Cluster: {info['cluster_name']}, Version: {info['version']['number']}")
            else:
                logger.warning(f"⚠️  Elasticsearch not responding at {self.es_host}")
                self.es = None
        except Exception as e:
            logger.warning(f"⚠️  Elasticsearch connection failed: {e}")
            logger.info("Start Elasticsearch with: ./run.sh services")
            self.es = None
    
    def create_indices(self):
        """Create Elasticsearch indices with mappings."""
        
        # Vehicle index mapping
        vehicle_mapping = {
            "mappings": {
                "properties": {
                    "make": {"type": "text", "analyzer": "standard"},
                    "model": {"type": "text", "analyzer": "standard"},
                    "variant": {"type": "text", "analyzer": "standard"},
                    "vehicle_type": {"type": "keyword"},
                    "fuel_type": {"type": "keyword"},
                    "front_tyre_size": {"type": "keyword"},
                    "rear_tyre_size": {"type": "keyword"},
                    "vehicle_price": {"type": "float"},
                    "created_at": {"type": "date"}
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        }
        
        # Tyre index mapping
        tyre_mapping = {
            "mappings": {
                "properties": {
                    "brand": {"type": "text", "analyzer": "standard"},
                    "model": {"type": "text", "analyzer": "standard"},
                    "size": {"type": "keyword"},
                    "price": {"type": "float"},
                    "mrp": {"type": "float"},
                    "tube_type": {"type": "keyword"},
                    "width": {"type": "integer"},
                    "aspect_ratio": {"type": "integer"},
                    "rim_size": {"type": "integer"},
                    "position": {"type": "keyword"},
                    "created_at": {"type": "date"}
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        }
        
        # Create indices
        for index_name, mapping in [
            ("tyreplex-vehicles", vehicle_mapping),
            ("tyreplex-tyres", tyre_mapping)
        ]:
            if self.es.indices.exists(index=index_name):
                logger.info(f"Index {index_name} already exists")
            else:
                self.es.indices.create(index=index_name, body=mapping)
                logger.success(f"✅ Created index: {index_name}")
    
    def sync_vehicles_from_mongodb(self) -> int:
        """Sync vehicles from MongoDB to Elasticsearch."""
        logger.info("Syncing vehicles from MongoDB to Elasticsearch...")
        
        # Get all vehicles from MongoDB
        vehicles = list(self.db.db.vehicles.find({}))
        
        if not vehicles:
            logger.warning("No vehicles found in MongoDB")
            return 0
        
        # Prepare bulk actions
        actions = []
        for vehicle in vehicles:
            # Convert ObjectId to string
            vehicle['_id'] = str(vehicle['_id'])
            
            action = {
                "_index": "tyreplex-vehicles",
                "_id": vehicle['_id'],
                "_source": {
                    "make": vehicle.get('make'),
                    "model": vehicle.get('model'),
                    "variant": vehicle.get('variant'),
                    "vehicle_type": vehicle.get('vehicle_type'),
                    "fuel_type": vehicle.get('fuel_type'),
                    "front_tyre_size": vehicle.get('front_tyre_size'),
                    "rear_tyre_size": vehicle.get('rear_tyre_size'),
                    "vehicle_price": vehicle.get('vehicle_price', 0),
                    "created_at": vehicle.get('created_at')
                }
            }
            actions.append(action)
        
        # Bulk index
        success, failed = bulk(self.es, actions, raise_on_error=False)
        logger.success(f"✅ Indexed {success} vehicles to Elasticsearch")
        
        if failed:
            logger.warning(f"⚠️  Failed to index {len(failed)} vehicles")
        
        return success
    
    def sync_tyres_from_mongodb(self) -> int:
        """Sync tyres from MongoDB to Elasticsearch."""
        logger.info("Syncing tyres from MongoDB to Elasticsearch...")
        
        # Get all tyres from MongoDB
        tyres = list(self.db.db.tyres.find({}))
        
        if not tyres:
            logger.warning("No tyres found in MongoDB")
            return 0
        
        # Prepare bulk actions
        actions = []
        for tyre in tyres:
            # Convert ObjectId to string
            tyre['_id'] = str(tyre['_id'])
            
            action = {
                "_index": "tyreplex-tyres",
                "_id": tyre['_id'],
                "_source": {
                    "brand": tyre.get('brand'),
                    "model": tyre.get('model'),
                    "size": tyre.get('size'),
                    "price": tyre.get('price', 0),
                    "mrp": tyre.get('mrp', 0),
                    "tube_type": tyre.get('tube_type'),
                    "width": tyre.get('width', 0),
                    "aspect_ratio": tyre.get('aspect_ratio', 0),
                    "rim_size": tyre.get('rim_size', 0),
                    "position": tyre.get('position'),
                    "created_at": tyre.get('created_at')
                }
            }
            actions.append(action)
        
        # Bulk index
        success, failed = bulk(self.es, actions, raise_on_error=False)
        logger.success(f"✅ Indexed {success} tyres to Elasticsearch")
        
        if failed:
            logger.warning(f"⚠️  Failed to index {len(failed)} tyres")
        
        return success
    
    def fuzzy_search_vehicle(self, query: str, size: int = 10) -> List[Dict]:
        """
        Fuzzy search for vehicles.
        Handles typos and partial matches.
        """
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["make^3", "model^2", "variant"],
                    "fuzziness": "AUTO",
                    "prefix_length": 1
                }
            },
            "size": size
        }
        
        result = self.es.search(index="tyreplex-vehicles", body=body)
        return [hit['_source'] for hit in result['hits']['hits']]
    
    def search_tyres_by_size(self, size: str, limit: int = 50) -> List[Dict]:
        """Search tyres by exact size."""
        body = {
            "query": {
                "term": {
                    "size": size
                }
            },
            "size": limit,
            "sort": [{"price": "asc"}]
        }
        
        result = self.es.search(index="tyreplex-tyres", body=body)
        return [hit['_source'] for hit in result['hits']['hits']]
    
    def search_tyres_by_brand(self, brand: str, limit: int = 50) -> List[Dict]:
        """Search tyres by brand with fuzzy matching."""
        body = {
            "query": {
                "match": {
                    "brand": {
                        "query": brand,
                        "fuzziness": "AUTO"
                    }
                }
            },
            "size": limit
        }
        
        result = self.es.search(index="tyreplex-tyres", body=body)
        return [hit['_source'] for hit in result['hits']['hits']]
    
    def search_tyres_by_price_range(
        self,
        size: str,
        min_price: float,
        max_price: float
    ) -> List[Dict]:
        """Search tyres by size and price range."""
        body = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"size": size}},
                        {"range": {"price": {"gte": min_price, "lte": max_price}}}
                    ]
                }
            },
            "sort": [{"price": "asc"}]
        }
        
        result = self.es.search(index="tyreplex-tyres", body=body)
        return [hit['_source'] for hit in result['hits']['hits']]
    
    def get_index_stats(self) -> Dict:
        """Get Elasticsearch index statistics."""
        vehicle_count = self.es.count(index="tyreplex-vehicles")['count']
        tyre_count = self.es.count(index="tyreplex-tyres")['count']
        
        return {
            'vehicles': vehicle_count,
            'tyres': tyre_count,
            'total': vehicle_count + tyre_count
        }
    
    def delete_indices(self):
        """Delete all TyrePlex indices."""
        for index in ["tyreplex-vehicles", "tyreplex-tyres"]:
            if self.es.indices.exists(index=index):
                self.es.indices.delete(index=index)
                logger.info(f"Deleted index: {index}")
    
    def sync_all(self) -> Dict:
        """Sync all data from MongoDB to Elasticsearch."""
        logger.info("Starting full sync from MongoDB to Elasticsearch...")
        
        # Create indices
        self.create_indices()
        
        # Sync vehicles
        vehicles_synced = self.sync_vehicles_from_mongodb()
        
        # Sync tyres
        tyres_synced = self.sync_tyres_from_mongodb()
        
        # Get stats
        stats = self.get_index_stats()
        
        logger.success(f"✅ Sync complete: {vehicles_synced} vehicles, {tyres_synced} tyres")
        
        return {
            'vehicles_synced': vehicles_synced,
            'tyres_synced': tyres_synced,
            'total_in_es': stats
        }


# CLI usage
if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("TyrePlex Elasticsearch Indexer")
    logger.info("=" * 70)
    
    try:
        # Initialize indexer
        indexer = ElasticsearchIndexer()
        
        # Check if ES is available
        if not indexer.es:
            logger.error("\n❌ Elasticsearch is not available!")
            logger.info("\n📝 To start Elasticsearch:")
            logger.info("   1. Run: ./run.sh services")
            logger.info("   2. Wait for services to start (30 seconds)")
            logger.info("   3. Run this script again")
            logger.info("\n💡 Or run complete setup: ./run.sh all")
            exit(1)
        
        # Sync all data
        result = indexer.sync_all()
        
        logger.info("\n📊 Sync Results:")
        logger.info(f"  Vehicles synced: {result['vehicles_synced']}")
        logger.info(f"  Tyres synced: {result['tyres_synced']}")
        logger.info(f"  Total in ES: {result['total_in_es']}")
        
        # Test fuzzy search
        logger.info("\n🧪 Testing fuzzy search...")
        results = indexer.fuzzy_search_vehicle("Maruti Swft")  # Typo
        if results:
            logger.success(f"✅ Found {len(results)} vehicles (with typo correction)")
            for r in results[:3]:
                logger.info(f"  - {r['make']} {r['model']} {r['variant']}")
        
        logger.success("\n✅ Elasticsearch indexing complete!")
        
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Interrupted by user")
    except Exception as e:
        logger.error(f"\n❌ Error: {e}")
        logger.info("\n📝 Troubleshooting:")
        logger.info("   1. Ensure Docker is running")
        logger.info("   2. Start services: ./run.sh services")
        logger.info("   3. Check logs: docker-compose logs elasticsearch")
        exit(1)
