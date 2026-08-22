"""
Voice Model Registry

Central registry for all voice cloning and TTS models available in the platform.
Supports multiple model types and providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import os
from loguru import logger


class ModelType(Enum):
    """Types of voice models supported"""
    COQUI_TTS = "coqui_tts"
    XTTS = "xtts"
    BARK = "bark"
    ELEVENLABS = "elevenlabs"
    AZURE_SPEECH = "azure_speech"
    GOOGLE_CLOUD_TTS = "google_cloud_tts"
    OPENAI_TTS = "openai_tts"
    TORTOISE_TTS = "tortoise_tts"
    VALL_E = "vall_e"
    CUSTOM = "custom"


class ModelTier(Enum):
    """Quality tiers for models"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


@dataclass
class ModelCapabilities:
    """Capabilities of a voice model"""
    voice_cloning: bool = False
    emotion_control: bool = False
    speed_control: bool = True
    pitch_control: bool = True
    style_transfer: bool = False
    real_time: bool = False
    streaming: bool = False
    multi_speaker: bool = False
    cross_lingual: bool = False
    fine_tuning: bool = False
    commercial_use: bool = False


@dataclass
class ModelSpecifications:
    """Technical specifications of a model"""
    max_text_length: int = 1000
    supported_sample_rates: List[int] = None
    supported_formats: List[str] = None
    min_training_samples: int = 10
    max_training_samples: int = 100
    training_duration_hours: float = 2.0
    inference_time_per_second: float = 0.5  # seconds of processing per second of audio
    model_size_mb: float = 100.0
    gpu_memory_required_gb: float = 4.0
    cpu_cores_recommended: int = 4
    
    def __post_init__(self):
        if self.supported_sample_rates is None:
            self.supported_sample_rates = [16000, 22050, 44100]
        if self.supported_formats is None:
            self.supported_formats = ["wav", "mp3", "flac"]


class BaseVoiceModel(ABC):
    """Base class for all voice models"""
    
    def __init__(self, model_id: str, config: Dict[str, Any]):
        self.model_id = model_id
        self.config = config
        self.is_loaded = False
    
    @abstractmethod
    async def load_model(self) -> bool:
        """Load the model into memory"""
        pass
    
    @abstractmethod
    async def unload_model(self):
        """Unload the model from memory"""
        pass
    
    @abstractmethod
    async def synthesize_speech(self, text: str, voice_id: str, **kwargs) -> bytes:
        """Synthesize speech from text"""
        pass
    
    @abstractmethod
    async def clone_voice(self, audio_samples: List[bytes], voice_name: str) -> str:
        """Clone a voice from audio samples, returns voice_id"""
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes"""
        pass
    
    @abstractmethod
    def validate_audio_sample(self, audio: bytes) -> Dict[str, Any]:
        """Validate audio sample for voice cloning"""
        pass


class ModelRegistry:
    """Central registry for voice models"""
    
    def __init__(self):
        self.models: Dict[str, Dict[str, Any]] = {}
        self.loaded_models: Dict[str, BaseVoiceModel] = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize the model registry with available models"""
        
        # Coqui TTS (Open Source, High Quality)
        self.register_model(
            model_id="coqui_tts_v1",
            model_type=ModelType.COQUI_TTS,
            tier=ModelTier.FREE,
            name="Coqui TTS v1",
            description="Open-source neural TTS with voice cloning capabilities",
            capabilities=ModelCapabilities(
                voice_cloning=True,
                emotion_control=False,
                speed_control=True,
                pitch_control=True,
                style_transfer=False,
                real_time=True,
                streaming=False,
                multi_speaker=True,
                cross_lingual=False,
                fine_tuning=True,
                commercial_use=True
            ),
            specs=ModelSpecifications(
                max_text_length=500,
                supported_sample_rates=[22050],
                min_training_samples=20,
                max_training_samples=100,
                training_duration_hours=4.0,
                inference_time_per_second=0.8,
                model_size_mb=150.0,
                gpu_memory_required_gb=6.0
            ),
            cost_per_second=0.0,  # Free
            setup_required=True
        )
        
        # XTTS (Coqui's Advanced Model)
        self.register_model(
            model_id="xtts_v2",
            model_type=ModelType.XTTS,
            tier=ModelTier.PREMIUM,
            name="XTTS v2",
            description="Advanced cross-lingual TTS with few-shot voice cloning",
            capabilities=ModelCapabilities(
                voice_cloning=True,
                emotion_control=True,
                speed_control=True,
                pitch_control=True,
                style_transfer=True,
                real_time=True,
                streaming=True,
                multi_speaker=True,
                cross_lingual=True,
                fine_tuning=True,
                commercial_use=True
            ),
            specs=ModelSpecifications(
                max_text_length=1000,
                supported_sample_rates=[22050, 24000],
                min_training_samples=1,  # Few-shot learning
                max_training_samples=50,
                training_duration_hours=1.0,
                inference_time_per_second=0.3,
                model_size_mb=300.0,
                gpu_memory_required_gb=8.0
            ),
            cost_per_second=0.002,
            setup_required=True
        )
        
        # Bark (Suno AI's Model)
        self.register_model(
            model_id="bark_v1",
            model_type=ModelType.BARK,
            tier=ModelTier.BASIC,
            name="Bark",
            description="Generative audio model with speaker prompts",
            capabilities=ModelCapabilities(
                voice_cloning=True,
                emotion_control=True,
                speed_control=False,
                pitch_control=False,
                style_transfer=True,
                real_time=False,
                streaming=False,
                multi_speaker=True,
                cross_lingual=True,
                fine_tuning=False,
                commercial_use=False  # Check license
            ),
            specs=ModelSpecifications(
                max_text_length=300,
                supported_sample_rates=[24000],
                min_training_samples=5,
                max_training_samples=20,
                training_duration_hours=0.5,
                inference_time_per_second=2.0,  # Slower
                model_size_mb=400.0,
                gpu_memory_required_gb=10.0
            ),
            cost_per_second=0.0,
            setup_required=True
        )
        
        # ElevenLabs API (Commercial)
        self.register_model(
            model_id="elevenlabs_multilingual",
            model_type=ModelType.ELEVENLABS,
            tier=ModelTier.PREMIUM,
            name="ElevenLabs Multilingual",
            description="Premium commercial TTS with voice cloning",
            capabilities=ModelCapabilities(
                voice_cloning=True,
                emotion_control=True,
                speed_control=True,
                pitch_control=False,
                style_transfer=True,
                real_time=True,
                streaming=True,
                multi_speaker=True,
                cross_lingual=True,
                fine_tuning=True,
                commercial_use=True
            ),
            specs=ModelSpecifications(
                max_text_length=5000,
                supported_sample_rates=[22050, 44100],
                min_training_samples=1,
                max_training_samples=25,
                training_duration_hours=0.25,
                inference_time_per_second=0.1,  # Very fast API
                model_size_mb=0,  # API-based
                gpu_memory_required_gb=0
            ),
            cost_per_second=0.018,  # Premium pricing
            setup_required=False,
            requires_api_key=True
        )
        
        # Azure Speech Services
        self.register_model(
            model_id="azure_neural_tts",
            model_type=ModelType.AZURE_SPEECH,
            tier=ModelTier.BASIC,
            name="Azure Neural TTS",
            description="Microsoft's neural TTS service",
            capabilities=ModelCapabilities(
                voice_cloning=False,  # Custom Neural Voice requires approval
                emotion_control=True,
                speed_control=True,
                pitch_control=True,
                style_transfer=True,
                real_time=True,
                streaming=True,
                multi_speaker=True,
                cross_lingual=True,
                fine_tuning=False,
                commercial_use=True
            ),
            specs=ModelSpecifications(
                max_text_length=10000,
                supported_sample_rates=[16000, 22050, 24000, 48000],
                inference_time_per_second=0.05,
                model_size_mb=0,
                gpu_memory_required_gb=0
            ),
            cost_per_second=0.004,
            setup_required=False,
            requires_api_key=True
        )
        
        # OpenAI TTS
        self.register_model(
            model_id="openai_tts_1",
            model_type=ModelType.OPENAI_TTS,
            tier=ModelTier.PREMIUM,
            name="OpenAI TTS",
            description="OpenAI's text-to-speech model",
            capabilities=ModelCapabilities(
                voice_cloning=False,
                emotion_control=False,
                speed_control=True,
                pitch_control=False,
                style_transfer=False,
                real_time=True,
                streaming=True,
                multi_speaker=True,
                cross_lingual=True,
                fine_tuning=False,
                commercial_use=True
            ),
            specs=ModelSpecifications(
                max_text_length=4096,
                supported_sample_rates=[22050, 24000, 44100],
                inference_time_per_second=0.1,
                model_size_mb=0,
                gpu_memory_required_gb=0
            ),
            cost_per_second=0.015,
            setup_required=False,
            requires_api_key=True
        )
    
    def register_model(
        self, 
        model_id: str,
        model_type: ModelType,
        tier: ModelTier,
        name: str,
        description: str,
        capabilities: ModelCapabilities,
        specs: ModelSpecifications,
        cost_per_second: float = 0.0,
        setup_required: bool = False,
        requires_api_key: bool = False,
        **kwargs
    ):
        """Register a new model in the registry"""
        self.models[model_id] = {
            "model_id": model_id,
            "model_type": model_type,
            "tier": tier,
            "name": name,
            "description": description,
            "capabilities": capabilities,
            "specs": specs,
            "cost_per_second": cost_per_second,
            "setup_required": setup_required,
            "requires_api_key": requires_api_key,
            "is_available": self._check_availability(model_type, requires_api_key),
            **kwargs
        }
    
    def _check_availability(self, model_type: ModelType, requires_api_key: bool) -> bool:
        """Check if a model is available based on configuration"""
        if requires_api_key:
            # Check if API keys are configured
            api_key_map = {
                ModelType.ELEVENLABS: "ELEVENLABS_API_KEY",
                ModelType.AZURE_SPEECH: "AZURE_SPEECH_KEY",
                ModelType.OPENAI_TTS: "OPENAI_API_KEY",
                ModelType.GOOGLE_CLOUD_TTS: "GOOGLE_CLOUD_KEY",
            }
            env_var = api_key_map.get(model_type)
            return env_var and bool(os.getenv(env_var))
        
        return True  # Local models are always "available" (can be downloaded/installed)
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model"""
        return self.models.get(model_id)
    
    def list_available_models(
        self, 
        tier: Optional[ModelTier] = None,
        capabilities: Optional[List[str]] = None,
        voice_cloning_only: bool = False
    ) -> List[Dict[str, Any]]:
        """List available models with optional filtering"""
        models = []
        
        for model_info in self.models.values():
            if not model_info["is_available"]:
                continue
                
            if tier and model_info["tier"] != tier:
                continue
                
            if voice_cloning_only and not model_info["capabilities"].voice_cloning:
                continue
                
            if capabilities:
                model_caps = model_info["capabilities"]
                if not all(hasattr(model_caps, cap) and getattr(model_caps, cap) for cap in capabilities):
                    continue
            
            models.append(model_info)
        
        return sorted(models, key=lambda x: (x["tier"].value, x["cost_per_second"]))
    
    def get_recommended_model(
        self, 
        use_case: str = "general",
        budget_tier: ModelTier = ModelTier.BASIC,
        voice_cloning: bool = False
    ) -> Optional[str]:
        """Get recommended model ID based on use case and requirements"""
        
        # Filter models by requirements
        suitable_models = []
        
        for model_id, model_info in self.models.items():
            if not model_info["is_available"]:
                continue
                
            # Check tier constraint
            tier_priority = {
                ModelTier.FREE: 0,
                ModelTier.BASIC: 1,
                ModelTier.PREMIUM: 2,
                ModelTier.ENTERPRISE: 3
            }
            
            if tier_priority[model_info["tier"]] > tier_priority[budget_tier]:
                continue
            
            # Check voice cloning requirement
            if voice_cloning and not model_info["capabilities"].voice_cloning:
                continue
            
            suitable_models.append((model_id, model_info))
        
        if not suitable_models:
            return None
        
        # Use case specific recommendations
        if use_case == "real_time":
            # Prioritize speed
            suitable_models.sort(key=lambda x: x[1]["specs"].inference_time_per_second)
        elif use_case == "high_quality":
            # Prioritize premium models
            suitable_models.sort(key=lambda x: -tier_priority[x[1]["tier"]])
        elif use_case == "cost_effective":
            # Prioritize free/low cost
            suitable_models.sort(key=lambda x: x[1]["cost_per_second"])
        else:
            # General use - balance of quality and cost
            suitable_models.sort(key=lambda x: (
                x[1]["cost_per_second"],
                x[1]["specs"].inference_time_per_second
            ))
        
        return suitable_models[0][0]
    
    async def load_model(self, model_id: str) -> Optional[BaseVoiceModel]:
        """Load a model instance"""
        if model_id in self.loaded_models:
            return self.loaded_models[model_id]
        
        model_info = self.get_model_info(model_id)
        if not model_info:
            logger.error(f"Model {model_id} not found in registry")
            return None
        
        try:
            # Dynamic model loading based on type
            model_class = self._get_model_class(model_info["model_type"])
            if not model_class:
                logger.error(f"No implementation for model type {model_info['model_type']}")
                return None
            
            model_instance = model_class(model_id, model_info)
            success = await model_instance.load_model()
            
            if success:
                self.loaded_models[model_id] = model_instance
                logger.info(f"Successfully loaded model {model_id}")
                return model_instance
            else:
                logger.error(f"Failed to load model {model_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error loading model {model_id}: {e}")
            return None
    
    def _get_model_class(self, model_type: ModelType) -> Optional[type]:
        """Get the implementation class for a model type"""
        # Import model implementations
        try:
            if model_type == ModelType.COQUI_TTS:
                from .implementations.coqui_tts import CoquiTTSModel
                return CoquiTTSModel
            elif model_type == ModelType.XTTS:
                from .implementations.xtts import XTTSModel
                return XTTSModel
            elif model_type == ModelType.ELEVENLABS:
                from .implementations.elevenlabs import ElevenLabsModel
                return ElevenLabsModel
            elif model_type == ModelType.BARK:
                from .implementations.bark import BarkModel
                return BarkModel
            # Add more implementations as needed
        except ImportError as e:
            logger.warning(f"Model implementation not available for {model_type}: {e}")
            return None
        
        return None


# Global model registry instance
model_registry = ModelRegistry()