import asyncio
import websockets
import json
import base64
import pyaudio
import threading
from typing import Dict, List, Callable, Any
import os
from dotenv import load_dotenv

load_dotenv()

class VoiceAIAgent:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.ws = None
        self.audio = pyaudio.PyAudio()
        self.is_recording = False
        self.is_playing = False
        
        # Audio settings
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 24000
        self.chunk = 1024
        
        # Function registry for HRI commands
        self.functions: Dict[str, Callable] = {}
        self.function_schemas: List[Dict] = []
        
    def register_function(self, name: str, func: Callable, schema: Dict):
        """Register a function that can be called by the AI agent"""
        self.functions[name] = func
        self.function_schemas.append({
            "name": name,
            "description": schema.get("description", ""),
            "parameters": schema.get("parameters", {})
        })
        
    async def connect(self):
        """Connect to OpenAI Realtime API"""
        uri = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "OpenAI-Beta": "realtime=v1"
        }
        
        self.ws = await websockets.connect(uri, extra_headers=headers)
        
        # Configure session
        await self.send_session_update()
        
    async def send_session_update(self):
        """Configure the session with tools and settings"""
        session_config = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": "You are a helpful AI assistant for human-robot interaction. Use the available functions to control robot actions when requested.",
                "voice": "alloy",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {
                    "model": "whisper-1"
                },
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 200
                },
                "tools": self.function_schemas
            }
        }
        
        await self.ws.send(json.dumps(session_config))
        
    async def send_audio_chunk(self, audio_data: bytes):
        """Send audio data to the API"""
        if self.ws:
            audio_message = {
                "type": "input_audio_buffer.append",
                "audio": base64.b64encode(audio_data).decode()
            }
            await self.ws.send(json.dumps(audio_message))
            
    async def handle_messages(self):
        """Handle incoming messages from the API"""
        async for message in self.ws:
            data = json.loads(message)
            await self.process_message(data)
            
    async def process_message(self, data: Dict):
        """Process different types of messages from the API"""
        msg_type = data.get("type")
        
        if msg_type == "response.audio.delta":
            # Play audio response
            audio_data = base64.b64decode(data["delta"])
            await self.play_audio(audio_data)
            
        elif msg_type == "response.function_call_delta":
            # Handle function calling
            if data.get("delta"):
                await self.handle_function_call(data)
                
        elif msg_type == "response.done":
            print("Response completed")
            
        elif msg_type == "error":
            print(f"Error: {data}")
            
    async def handle_function_call(self, data: Dict):
        """Execute function calls from the AI"""
        function_name = data.get("name")
        arguments = data.get("arguments", "{}")
        
        try:
            args = json.loads(arguments)
            if function_name in self.functions:
                result = await self.functions[function_name](**args)
                
                # Send function result back
                response = {
                    "type": "conversation.item.create",
                    "item": {
                        "type": "function_call_output",
                        "call_id": data.get("call_id"),
                        "output": str(result)
                    }
                }
                await self.ws.send(json.dumps(response))
                
        except Exception as e:
            print(f"Function call error: {e}")
            
    def start_recording(self):
        """Start recording audio from microphone"""
        self.is_recording = True
        
        def record():
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            while self.is_recording:
                data = stream.read(self.chunk)
                if self.ws:
                    asyncio.create_task(self.send_audio_chunk(data))
                    
            stream.stop_stream()
            stream.close()
            
        self.record_thread = threading.Thread(target=record)
        self.record_thread.start()
        
    def stop_recording(self):
        """Stop recording audio"""
        self.is_recording = False
        if hasattr(self, 'record_thread'):
            self.record_thread.join()
            
    async def play_audio(self, audio_data: bytes):
        """Play audio data through speakers"""
        def play():
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                output=True
            )
            
            stream.write(audio_data)
            stream.stop_stream()
            stream.close()
            
        threading.Thread(target=play).start()
        
    async def run(self):
        """Main loop for the voice agent"""
        await self.connect()
        
        # Start recording
        self.start_recording()
        
        try:
            await self.handle_messages()
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed")
        finally:
            self.stop_recording()
            
    def cleanup(self):
        """Clean up resources"""
        self.stop_recording()
        self.audio.terminate()
        if self.ws:
            asyncio.create_task(self.ws.close())