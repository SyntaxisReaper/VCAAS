"""
ElevenLabs Implementation

Commercial TTS API with voice cloning capabilities.
"""

import os
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from loguru import logger
import json
import io

from ..model_registry import BaseVoiceModel


class ElevenLabsModel(BaseVoiceModel):
    """ElevenLabs API implementation"""
    
    def __init__(self, model_id: str, config: Dict[str, Any]):
        super().__init__(model_id, config)
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1"
        self.session: Optional[aiohttp.ClientSession] = None
        
        if not self.api_key:
            logger.warning("ElevenLabs API key not found in environment variables")
    
    async def load_model(self) -> bool:
        """Initialize the ElevenLabs client"""
        try:
            if not self.api_key:
                logger.error("ElevenLabs API key is required")
                return False
            
            # Create aiohttp session with headers
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            self.session = aiohttp.ClientSession(headers=headers)
            
            # Test API connection
            await self._test_connection()
            
            self.is_loaded = True
            logger.info("ElevenLabs model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load ElevenLabs model: {e}")
            return False
    
    async def unload_model(self):
        """Close the API session"""
        if self.session:
            await self.session.close()
            self.session = None
        self.is_loaded = False
        logger.info("ElevenLabs model unloaded")
    
    async def _test_connection(self):
        """Test API connection"""
        if not self.session:
            raise ValueError("Session not initialized")
        
        async with self.session.get(f"{self.base_url}/user") as response:
            if response.status != 200:
                text = await response.text()
                raise ValueError(f"API connection failed: {response.status} - {text}")
    
    async def synthesize_speech(
        self, 
        text: str, 
        voice_id: str, 
        **kwargs
    ) -> bytes:
        """Synthesize speech using ElevenLabs API"""
        if not self.is_loaded or not self.session:
            raise ValueError("Model not loaded")
        
        # ElevenLabs API parameters
        voice_settings = {
            "stability": kwargs.get("stability", 0.5),
            "similarity_boost": kwargs.get("similarity_boost", 0.75),
            "style": kwargs.get("style", 0.0),
            "use_speaker_boost": kwargs.get("use_speaker_boost", True)
        }
        
        # Adjust for custom parameters
        if "speed" in kwargs:
            # ElevenLabs doesn't have direct speed control, adjust style
            speed = kwargs["speed"]
            if speed < 1.0:
                voice_settings["style"] = min(1.0, voice_settings["style"] + (1.0 - speed) * 0.3)
            elif speed > 1.0:
                voice_settings["style"] = max(0.0, voice_settings["style"] - (speed - 1.0) * 0.3)
        
        payload = {
            "text": text,
            "model_id": kwargs.get("model_id", "eleven_multilingual_v2"),
            "voice_settings": voice_settings
        }
        
        try:
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    audio_data = await response.read()
                    logger.info(f"Successfully synthesized {len(audio_data)} bytes of audio")
                    return audio_data
                else:
                    error_text = await response.text()
                    raise ValueError(f"TTS failed: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            raise
    
    async def clone_voice(
        self, 
        audio_samples: List[bytes], 
        voice_name: str,
        description: Optional[str] = None
    ) -> str:
        """Clone a voice using ElevenLabs API"""
        if not self.is_loaded or not self.session:
            raise ValueError("Model not loaded")
        
        if len(audio_samples) == 0:
            raise ValueError("At least one audio sample is required")
        
        if len(audio_samples) > 25:
            logger.warning(f"Too many samples ({len(audio_samples)}), using first 25")
            audio_samples = audio_samples[:25]
        
        try:
            # Prepare multipart form data
            data = aiohttp.FormData()
            data.add_field('name', voice_name)
            
            if description:
                data.add_field('description', description)
            
            # Add audio files
            for i, audio_data in enumerate(audio_samples):
                data.add_field(
                    'files',
                    io.BytesIO(audio_data),
                    filename=f'sample_{i}.wav',
                    content_type='audio/wav'
                )
            
            # Clone the voice
            url = f"{self.base_url}/voices/add"
            
            # Update headers for multipart upload
            headers = {"xi-api-key": self.api_key}
            
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.post(url, data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        voice_id = result.get("voice_id")
                        logger.info(f"Successfully cloned voice: {voice_id}")
                        return voice_id
                    else:
                        error_text = await response.text()
                        raise ValueError(f"Voice cloning failed: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Error cloning voice: {e}")
            raise
    
    async def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get list of available voices"""
        if not self.is_loaded or not self.session:
            raise ValueError("Model not loaded")
        
        try:
            async with self.session.get(f"{self.base_url}/voices") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("voices", [])
                else:
                    error_text = await response.text()
                    raise ValueError(f"Failed to get voices: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"Error getting available voices: {e}")
            raise
    
    async def delete_voice(self, voice_id: str) -> bool:
        """Delete a cloned voice"""
        if not self.is_loaded or not self.session:
            raise ValueError("Model not loaded")
        
        try:
            async with self.session.delete(f"{self.base_url}/voices/{voice_id}") as response:
                if response.status == 200:
                    logger.info(f"Successfully deleted voice: {voice_id}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to delete voice {voice_id}: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error deleting voice: {e}")
            return False
    
    def get_supported_languages(self) -> List[str]:
        """Get supported language codes"""
        return [
            "en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", 
            "cs", "ar", "zh", "ja", "hu", "ko", "hi", "fi", "sv", "bg",
            "hr", "ro", "uk", "el", "sk", "da", "ta", "id", "th", "ms"
        ]
    
    def validate_audio_sample(self, audio: bytes) -> Dict[str, Any]:
        """Validate audio sample for voice cloning"""
        # Basic validation
        if len(audio) < 1000:  # Less than 1KB
            return {
                "valid": False,
                "reason": "Audio file too small",
                "recommendations": ["Upload a larger audio file (at least a few seconds)"]
            }
        
        if len(audio) > 10 * 1024 * 1024:  # Larger than 10MB
            return {
                "valid": False,
                "reason": "Audio file too large",
                "recommendations": ["Compress audio file to under 10MB"]
            }
        
        # ElevenLabs accepts most common formats
        return {
            "valid": True,
            "reason": "Audio sample appears valid",
            "recommendations": [
                "For best results, use clear, high-quality recordings",
                "Recommended: 22kHz sample rate, WAV format",
                "Include 1-5 minutes of clean speech per sample"
            ]
        }
    
    async def get_voice_info(self, voice_id: str) -> Dict[str, Any]:
        """Get information about a specific voice"""
        if not self.is_loaded or not self.session:
            raise ValueError("Model not loaded")
        
        try:
            async with self.session.get(f"{self.base_url}/voices/{voice_id}") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise ValueError(f"Failed to get voice info: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"Error getting voice info: {e}")
            raise
    
    async def get_user_info(self) -> Dict[str, Any]:
        """Get user account information and usage"""
        if not self.is_loaded or not self.session:
            raise ValueError("Model not loaded")
        
        try:
            async with self.session.get(f"{self.base_url}/user") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise ValueError(f"Failed to get user info: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            raise
    
    def estimate_cost(self, text: str) -> Dict[str, float]:
        """Estimate cost for TTS generation"""
        # ElevenLabs pricing (as of 2024)
        characters = len(text)
        
        # Pricing tiers (characters per month)
        if characters <= 10000:  # Free tier
            cost = 0.0
        else:
            # Paid tier: ~$0.18 per 1000 characters
            cost = (characters / 1000) * 0.18
        
        return {
            "characters": characters,
            "estimated_cost_usd": cost,
            "tier": "free" if characters <= 10000 else "paid"
        }