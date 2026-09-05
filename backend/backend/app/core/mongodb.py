"""
MongoDB Database Configuration

Uses Beanie ODM for modern async MongoDB operations with Pydantic models.
"""

import os
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from pymongo.server_api import ServerApi
from loguru import logger

from app.core.config import settings


class MongoDB:
    """MongoDB connection manager"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
        
    async def connect(self):
        """Connect to MongoDB database"""
        try:
            # MongoDB connection string
            if hasattr(settings, 'MONGODB_URL') and settings.MONGODB_URL:
                mongodb_url = settings.MONGODB_URL
            else:
                # Fallback to local MongoDB
                mongodb_url = "mongodb://localhost:27017"
            
            # Database name
            db_name = getattr(settings, 'MONGODB_DATABASE', 'voice_clone_platform')
            
            logger.info(f"Connecting to MongoDB: {mongodb_url}")
            
            # Create client with server API version
            self.client = AsyncIOMotorClient(
                mongodb_url,
                server_api=ServerApi('1'),
                maxPoolSize=10,
                minPoolSize=1,
                maxIdleTimeMS=45000,
                connectTimeoutMS=10000,
                serverSelectionTimeoutMS=10000
            )
            
            # Get database
            self.database = self.client[db_name]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB!")
            
            # Initialize Beanie with document models
            await self.init_beanie()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def init_beanie(self):
        """Initialize Beanie ODM with all document models"""
        try:
            # Import all document models here
            from app.models.mongo.user import User
            from app.models.mongo.voice_sample import VoiceSample
            from app.models.mongo.voice_model import VoiceModel
            from app.models.mongo.tts_job import TTSJob
            from app.models.mongo.training_job import TrainingJob
            from app.models.mongo.security_report import SecurityReport
            from app.models.mongo.usage_log import UsageLog
            from app.models.mongo.license import License
            
            # List all document models
            document_models = [
                User,
                VoiceSample,
                VoiceModel, 
                TTSJob,
                TrainingJob,
                SecurityReport,
                UsageLog,
                License
            ]
            
            # Initialize Beanie
            await init_beanie(
                database=self.database,
                document_models=document_models
            )
            
            logger.info(f"Initialized Beanie ODM with {len(document_models)} document models")
            
        except Exception as e:
            logger.error(f"Failed to initialize Beanie ODM: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def get_database_info(self):
        """Get database information"""
        try:
            if not self.database:
                return None
                
            # Get database stats
            stats = await self.database.command("dbStats")
            
            # Get collection names
            collections = await self.database.list_collection_names()
            
            return {
                "database_name": self.database.name,
                "collections": collections,
                "data_size": stats.get("dataSize", 0),
                "storage_size": stats.get("storageSize", 0),
                "objects": stats.get("objects", 0),
                "indexes": stats.get("indexes", 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return None


# Global MongoDB instance
mongodb = MongoDB()


async def get_database():
    """Get MongoDB database instance"""
    if not mongodb.database:
        await mongodb.connect()
    return mongodb.database


async def connect_to_mongo():
    """Connect to MongoDB (used in app startup)"""
    await mongodb.connect()


async def close_mongo_connection():
    """Close MongoDB connection (used in app shutdown)"""
    await mongodb.disconnect()