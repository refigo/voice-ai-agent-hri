#!/usr/bin/env python3
"""
FINAL SMOOTH Cafe Voice Robot - BEST VERSION
Uses simplified audio handling for smooth playback
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
import signal
import sys
from dotenv import load_dotenv

load_dotenv()

class FinalVoiceAIAgent:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.ws = None
        self.audio = pyaudio.PyAudio()
        self.is_recording = False
        self.is_playing = False
        
        # Optimized audio settings
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 24000
        self.chunk = 4096  # Large chunks for smooth recording
        
        # Audio data storage
        self.recorded_chunks = []
        self.playback_buffer = []
        
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
        """Configure the session"""
        session_config = {
            "type": "session.update", 
            "session": {
                "modalities": ["text", "audio"],
                "instructions": "You are a friendly cafe service robot. Help with orders and robot control.",
                "voice": "alloy",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {"model": "whisper-1"},
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 800  # Longer pause for better detection
                },
                "tools": self.function_schemas
            }
        }
        await self.ws.send(json.dumps(session_config))
        
    def start_recording(self):
        """Start recording with periodic sending"""
        self.is_recording = True
        self.recorded_chunks = []
        
        def record_and_send():
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
                    if not self.is_playing:  # Only record when not playing
                        data = stream.read(self.chunk, exception_on_overflow=False)
                        self.recorded_chunks.append(data)
                        
                        # Send audio every few chunks for smoother streaming
                        if len(self.recorded_chunks) >= 3:
                            combined_audio = b''.join(self.recorded_chunks)
                            self.recorded_chunks = []
                            
                            # Schedule async sending
                            if self.ws:
                                asyncio.run_coroutine_threadsafe(
                                    self.send_audio(combined_audio),
                                    self.event_loop
                                )
                    else:
                        time.sleep(0.1)  # Wait while playing
                        
            except Exception as e:
                print(f"Recording error: {e}")
            finally:
                if stream:
                    stream.stop_stream()
                    stream.close()
                print("🎤 Recording stopped")
        
        self.record_thread = threading.Thread(target=record_and_send, daemon=True)
        self.record_thread.start()
        
    async def send_audio(self, audio_data: bytes):
        """Send audio data to API"""
        if self.ws:
            message = {
                "type": "input_audio_buffer.append",
                "audio": base64.b64encode(audio_data).decode()
            }
            await self.ws.send(json.dumps(message))
            
    async def handle_messages(self):
        """Handle WebSocket messages"""
        async for message in self.ws:
            data = json.loads(message)
            await self.process_message(data)
            
    async def process_message(self, data: Dict):
        """Process messages from OpenAI"""
        msg_type = data.get("type")
        
        if msg_type == "response.audio.delta":
            # Collect audio for smooth playback
            audio_data = base64.b64decode(data["delta"])
            self.playback_buffer.append(audio_data)
            
        elif msg_type == "response.function_call_delta":
            if data.get("delta"):
                await self.handle_function_call(data)
                
        elif msg_type == "response.done":
            # Play all collected audio smoothly
            if self.playback_buffer:
                await self.play_smooth_audio()
            print("✅ Response complete")
            
        elif msg_type == "session.created":
            print("✅ Connected successfully")
            
        elif msg_type == "session.updated":
            print("✅ System ready")
            
        elif msg_type == "input_audio_buffer.speech_started":
            print("👂 Listening...")
            
        elif msg_type == "input_audio_buffer.speech_stopped":
            print("🧠 Thinking...")
            
        elif msg_type == "error":
            print(f"❌ Error: {data}")
            
    async def handle_function_call(self, data: Dict):
        """Execute function calls"""
        function_name = data.get("name")
        arguments = data.get("arguments", "{}")
        
        try:
            args = json.loads(arguments)
            if function_name in self.functions:
                print(f"\n🔧 {function_name}({args})")
                result = await self.functions[function_name](**args)
                print(f"✅ {result}\n")
                
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
            print(f"❌ Function error: {e}")
            
    async def play_smooth_audio(self):
        """Play buffered audio smoothly"""
        if not self.playback_buffer:
            return
            
        self.is_playing = True
        
        def play():
            try:
                # Combine all audio chunks
                audio_data = b''.join(self.playback_buffer)
                self.playback_buffer.clear()
                
                if len(audio_data) > 0:
                    stream = self.audio.open(
                        format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        output=True
                    )
                    
                    # Play in one smooth stream
                    stream.write(audio_data)
                    stream.stop_stream()
                    stream.close()
                    
            except Exception as e:
                print(f"Playback error: {e}")
            finally:
                self.is_playing = False
                time.sleep(0.5)  # Brief pause before allowing recording
                
        threading.Thread(target=play, daemon=True).start()
        
    def stop_recording(self):
        """Stop recording"""
        self.is_recording = False
        
    async def run(self):
        """Main run loop"""
        self.event_loop = asyncio.get_running_loop()
        
        try:
            print("🔗 Connecting to OpenAI...")
            await self.connect()
            
            self.start_recording()
            
            print("\n🎉 SMOOTH Voice AI Ready!")
            print("💬 Speak naturally for smooth responses!")
            print("⏹️  Press Ctrl+C to stop\n")
            
            await self.handle_messages()
            
        except websockets.exceptions.ConnectionClosed:
            print("🔌 Connection closed")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        finally:
            self.stop_recording()
            
    def cleanup(self):
        """Clean up resources"""
        self.stop_recording()
        self.audio.terminate()

# Import the required modules
from hri_functions import RobotController, HRI_FUNCTION_SCHEMAS
from cafe_system import CafeKioskSystem, CAFE_FUNCTION_SCHEMAS

async def main():
    """Main function"""
    print("🤖 ☕ FINAL SMOOTH VOICE AI CAFE ROBOT")
    print("=" * 55)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ No API key found")
        sys.exit(1)
    
    print("✅ API key configured")
    print("\n🎵 SMOOTH AUDIO FEATURES:")
    print("• ✅ No chunky playback")
    print("• ✅ Buffered smooth audio")
    print("• ✅ Large chunk recording")
    print("• ✅ Minimal latency")
    
    # Create systems
    agent = FinalVoiceAIAgent()
    cafe_system = CafeKioskSystem()
    robot = RobotController()
    
    # Register functions
    for schema in CAFE_FUNCTION_SCHEMAS:
        func_name = schema["name"]
        func = getattr(cafe_system, func_name)
        agent.register_function(func_name, func, schema)
        
    for schema in HRI_FUNCTION_SCHEMAS:
        func_name = schema["name"]
        func = getattr(robot, func_name)
        agent.register_function(func_name, func, schema)
    
    print(f"\n✅ {len(CAFE_FUNCTION_SCHEMAS)} cafe + {len(HRI_FUNCTION_SCHEMAS)} robot functions ready")
    
    print("\n💡 VOICE COMMANDS:")
    print("☕ 'Hello, show me the menu'")
    print("🤖 'Move forward 2 meters'")
    print("🔄 'Take my order then scan area'")
    
    print("\n" + "=" * 55)
    print("🚀 Starting Final Smooth Voice AI...")
    print("=" * 55)
    
    # Setup signal handler
    def signal_handler(signum, frame):
        print(f"\n🛑 Stopping...")
        agent.cleanup()
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        await agent.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        agent.cleanup()

if __name__ == "__main__":
    asyncio.run(main())