"""
Smooth Voice AI Agent with improved audio flow - NO CHUNKY AUDIO
"""

import asyncio
import websockets
import json
import base64
import pyaudio
import threading
import time
from typing import Dict, List, Callable, Any
import os
from dotenv import load_dotenv

load_dotenv()

class VoiceAIAgentSmooth:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.ws = None
        self.audio = pyaudio.PyAudio()
        self.is_recording = False
        self.is_playing = False
        
        # Improved audio settings for smooth playback
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 24000
        self.chunk = 2048  # Larger chunks for smoother audio
        
        # Audio buffer for smooth playback
        self.audio_buffer = bytearray()
        self.buffer_lock = threading.Lock()
        
        # Response tracking to prevent duplicates
        self.active_responses = set()
        
        # Function registry
        self.functions: Dict[str, Callable] = {}
        self.function_schemas: List[Dict] = []
        
    def register_function(self, name: str, func: Callable, schema: Dict):
        """Register a function that can be called by the AI agent"""
        self.functions[name] = func
        self.function_schemas.append({
            "type": "function",
            "name": name,
            "description": schema.get("description", ""),
            "parameters": schema.get("parameters", {})
        })
        
    async def connect(self):
        """Connect to OpenAI Realtime API"""
        uri = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
        headers = [
            ("Authorization", f"Bearer {self.api_key}"),
            ("OpenAI-Beta", "realtime=v1")
        ]
        
        self.ws = await websockets.connect(uri, additional_headers=headers)
        await self.send_session_update()
        
    async def send_session_update(self):
        """Configure the session with tools and settings"""
        session_config = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": """You are an intelligent cafe service robot with voice interaction capabilities. 

CORE CAPABILITIES:
1. CAFE ORDERING: Help customers browse menu, place orders, customize items, process payments
2. ROBOT CONTROL: Move around, control LEDs, take photos, scan environment
3. CUSTOMER SERVICE: Provide recommendations, check order status, handle modifications

CONVERSATION GUIDELINES:
- Always be friendly, helpful, and professional
- For ordering: Guide customers through menu, suggest items, confirm details
- For robot control: Confirm movements for safety, explain actions
- Use appropriate functions based on customer requests
- Ask clarifying questions when needed
- Provide clear status updates

Be conversational and natural - you're both a helpful cafe assistant and a capable service robot!""",
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
                    "silence_duration_ms": 500
                },
                "tools": self.function_schemas
            }
        }
        
        await self.ws.send(json.dumps(session_config))
        
    async def send_audio_chunk(self, audio_data: bytes):
        """Send audio data directly to the API - NO QUEUE"""
        if self.ws and not self.is_playing:
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
            # Add audio to buffer for smooth playback
            audio_data = base64.b64decode(data["delta"])
            with self.buffer_lock:
                self.audio_buffer.extend(audio_data)
            
        elif msg_type == "response.function_call_delta":
            if data.get("delta"):
                await self.handle_function_call(data)
                
        elif msg_type == "response.created":
            response_id = data.get("response", {}).get("id")
            if response_id:
                self.active_responses.add(response_id)
                print("🎤 Processing your request...")
                
        elif msg_type == "response.done":
            response_id = data.get("response", {}).get("id")
            if response_id and response_id in self.active_responses:
                self.active_responses.remove(response_id)
                # Start playing buffered audio
                await self.play_buffered_audio()
                print("✅ Response complete")
            
        elif msg_type == "error":
            print(f"❌ Error: {data}")
            
        elif msg_type == "session.created":
            print("✅ Session created successfully")
            
        elif msg_type == "session.updated":
            print("✅ Session configured")
            
        elif msg_type == "input_audio_buffer.speech_started":
            print("🎤 Listening...")
            
        elif msg_type == "input_audio_buffer.speech_stopped":
            print("🎤 Processing...")
            
    async def handle_function_call(self, data: Dict):
        """Execute function calls from the AI"""
        function_name = data.get("name")
        arguments = data.get("arguments", "{}")
        
        try:
            args = json.loads(arguments)
            if function_name in self.functions:
                print(f"\n🔧 Executing: {function_name}")
                if args:
                    print(f"📋 Parameters: {args}")
                result = await self.functions[function_name](**args)
                print(f"✅ Result: {result}\n")
                
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
            print(f"❌ Function call error: {e}")
            
    def start_recording(self):
        """Start recording audio from microphone with direct async sending"""
        self.is_recording = True
        
        def record():
            stream = None
            try:
                stream = self.audio.open(
                    format=self.format,
                    channels=self.channels,
                    rate=self.rate,
                    input=True,
                    frames_per_buffer=self.chunk
                )
                
                print("🎤 Recording started - speak naturally!")
                
                while self.is_recording:
                    try:
                        data = stream.read(self.chunk, exception_on_overflow=False)
                        # Send audio directly without queue bottleneck
                        if not self.is_playing and self.ws:
                            try:
                                loop = asyncio.get_running_loop()
                                asyncio.run_coroutine_threadsafe(
                                    self.send_audio_chunk(data), 
                                    loop
                                )
                            except RuntimeError:
                                # No event loop, skip this chunk
                                pass
                    except Exception as e:
                        print(f"Recording error: {e}")
                        break
                        
            except Exception as e:
                print(f"Audio setup error: {e}")
            finally:
                if stream:
                    stream.stop_stream()
                    stream.close()
                print("🎤 Recording stopped")
            
        self.record_thread = threading.Thread(target=record, daemon=True)
        self.record_thread.start()
        
    def stop_recording(self):
        """Stop recording audio"""
        self.is_recording = False
        if hasattr(self, 'record_thread'):
            self.record_thread.join(timeout=2.0)
            
    async def play_buffered_audio(self):
        """Play all buffered audio smoothly"""
        if len(self.audio_buffer) == 0:
            return
            
        self.is_playing = True
        
        def play():
            try:
                # Get all buffered audio
                with self.buffer_lock:
                    audio_data = bytes(self.audio_buffer)
                    self.audio_buffer.clear()
                
                if len(audio_data) > 0:
                    stream = self.audio.open(
                        format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        output=True
                    )
                    
                    # Play audio in larger chunks for smoothness
                    chunk_size = 4096
                    for i in range(0, len(audio_data), chunk_size):
                        chunk = audio_data[i:i + chunk_size]
                        stream.write(chunk)
                    
                    stream.stop_stream()
                    stream.close()
                    
            except Exception as e:
                print(f"Audio playback error: {e}")
            finally:
                self.is_playing = False
                # Brief pause before allowing new recording
                time.sleep(0.2)
                
        threading.Thread(target=play, daemon=True).start()
        
    async def run(self):
        """Main loop for the voice agent"""
        try:
            print("🔗 Connecting to OpenAI Realtime API...")
            await self.connect()
            
            # Start recording
            self.start_recording()
            
            print("\n🎉 Smooth Voice AI Cafe Robot is ready!")
            print("🎤 Speak naturally - smooth audio guaranteed!")
            print("💡 Try saying: 'Hello, show me the menu' or 'Move forward 2 meters'")
            print("⏹️  Press Ctrl+C to stop\n")
            
            # Handle messages
            await self.handle_messages()
            
        except websockets.exceptions.ConnectionClosed:
            print("🔌 Connection closed")
        except KeyboardInterrupt:
            print("\n👋 Stopped by user")
        finally:
            self.stop_recording()
            
    def cleanup(self):
        """Clean up resources"""
        self.stop_recording()
        self.audio.terminate()
        if self.ws:
            asyncio.create_task(self.ws.close())