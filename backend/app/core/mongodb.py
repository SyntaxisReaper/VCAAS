"""
MongoDB Configuration and Connection Management

Handles MongoDB connection, Beanie ODM initialization, and database setup.
"""

import asyncio
from typing import List
from loguru import logger
import os

try:
    from motor.motor_asyncio import AsyncIOMotorClient
    from beanie import init_beanie
    HAS_MONGO = True
except ImportError:
    AsyncIOMotorClient = None
    init_beanie = None
    HAS_MONGO = False
    logger.warning("MongoDB drivers (motor, beanie) not installed. Running in no-Mongo mode.")

# Import models only if Mongo is available to avoid errors
if HAS_MONGO:
    from app.models.mongo.user import User
    from app.models.mongo.voice_sample import VoiceSample
    from app.models.mongo.voice_model import VoiceModel
    from app.models.mongo.tts_job import TTSJob
else:
    User = None
    VoiceSample = None
    VoiceModel = None
    TTSJob = None


class MongoDB:
    """MongoDB connection and management class"""
    
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.database = None
        self.is_connected = False
        
        # Get MongoDB URL from environment or use default
        self.mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017/voice_platform")
        self.database_name = os.getenv("MONGODB_DATABASE", "voice_platform")
    
    async def connect(self):
        """Connect to MongoDB and initialize Beanie ODM"""
        if not HAS_MONGO:
            logger.info("MongoDB disabled (drivers not found)")
            return False

        try:
            logger.info(f"Connecting to MongoDB: {self.mongodb_url}")
            
            # Create MongoDB client
            self.client = AsyncIOMotorClient(self.mongodb_url)
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("MongoDB connection successful")
            
            # Get database
            self.database = self.client[self.database_name]
            
            # Initialize Beanie ODM with document models
            await init_beanie(
                database=self.database,
                document_models=[User, VoiceSample, VoiceModel, TTSJob]
            )
            
            self.is_connected = True
            logger.info("Beanie ODM initialized successfully")
            
            # Create indexes
            await self._create_indexes()
            
            return True
            
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            self.is_connected = False
            logger.info("Disconnected from MongoDB")
    
    async def _create_indexes(self):
        """Create additional database indexes for performance"""
        try:
            # User indexes
            await self.database.users.create_index("email", unique=True)
            await self.database.users.create_index("username", unique=True)
            await self.database.users.create_index("subscription_tier")
            
            # Voice Sample indexes
            await self.database.voice_samples.create_index([("user_id", 1), ("created_at", -1)])
            await self.database.voice_samples.create_index("status")
            await self.database.voice_samples.create_index("is_suitable_for_training")
            
            # Voice Model indexes
            await self.database.voice_models.create_index([("user_id", 1), ("created_at", -1)])
            await self.database.voice_models.create_index("is_public")
            await self.database.voice_models.create_index("status")
            await self.database.voice_models.create_index("deployment_status")
            
            # TTS Job indexes
            await self.database.tts_jobs.create_index([("user_id", 1), ("created_at", -1)])
            await self.database.tts_jobs.create_index("status")
            await self.database.tts_jobs.create_index([("status", 1), ("priority", 1)])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Index creation failed (may already exist): {e}")
    
    async def health_check(self) -> dict:
        """Check MongoDB connection health"""
        try:
            if not self.is_connected:
                return {"status": "disconnected", "error": "Not connected to MongoDB"}
            
            # Test connection
            await self.client.admin.command('ping')
            
            # Get database stats
            stats = await self.database.command("dbStats")
            
            return {
                "status": "healthy",
                "database": self.database_name,
                "collections": stats.get("collections", 0),
                "objects": stats.get("objects", 0),
                "dataSize": stats.get("dataSize", 0),
                "storageSize": stats.get("storageSize", 0)
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def create_test_data(self):
        """Create test data for development"""
        try:
            logger.info("Creating test data...")
            
            # Create test user
            test_user = User(
                email="test@example.com",
                username="testuser",
                full_name="Test User",
                password_hash="hashed_password"  # In real app, hash this properly
            )
            
            # Check if test user already exists
            existing_user = await User.find_one(User.email == "test@example.com")
            if not existing_user:
                await test_user.save()
                logger.info("Created test user: test@example.com")
            else:
                test_user = existing_user
                logger.info("Test user already exists")
            
            # Create test voice sample
            existing_sample = await VoiceSample.find_one(VoiceSample.user_id == str(test_user.id))
            if not existing_sample:
                test_sample = VoiceSample(
                    user_id=str(test_user.id),
                    filename="test_sample.wav",
                    file_path="/storage/samples/test_sample.wav",
                    transcription="This is a test voice sample for the platform.",
                    duration_seconds=10.5,
                    quality_score=0.85,
                    is_suitable_for_training=True,
                    status="processed"
                )
                await test_sample.save()
                logger.info("Created test voice sample")
            
            # Create test voice model
            existing_model = await VoiceModel.find_one(VoiceModel.user_id == str(test_user.id))
            if not existing_model:
                test_model = VoiceModel(
                    name="Test Voice Model",
                    description="A test voice model for development",
                    user_id=str(test_user.id),
                    is_public=True,
                    model_type="xtts_v2",
                    status="completed",
                    deployment_status="deployed",
                    quality_score=0.9,
                    similarity_score=0.85,
                    naturalness_score=0.88,
                    supported_languages=["en"]
                )
                await test_model.save()
                logger.info("Created test voice model")
            
            logger.info("Test data creation completed")
            
        except Exception as e:
            logger.error(f"Test data creation failed: {e}")


# Global MongoDB instance
mongodb = MongoDB()


async def init_database():
    """Initialize database connection"""
    return await mongodb.connect()


async def close_database():
    """Close database connection"""
    await mongodb.disconnect()


async def get_database():
    """Get database instance (for dependency injection)"""
    if not mongodb.is_connected:
        raise Exception("Database not connected")
    return mongodb.database