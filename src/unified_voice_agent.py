#!/usr/bin/env python3
"""
Unified Voice AI Agent for Cafe Ordering and HRI
Supports both voice and text input for testing
"""

import asyncio
import websockets
import json
import threading
import time
from typing import Dict, List, Callable, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class UnifiedVoiceAgent:
    def __init__(self, audio_enabled: bool = True):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.audio_enabled = audio_enabled
        self.ws = None
        self.running = False
        
        # Function registry for commands
        self.functions: Dict[str, Callable] = {}
        self.function_schemas: List[Dict] = []
        
        # Audio components (loaded conditionally)
        self.audio_in = None
        self.audio_out = None
        
        if self.audio_enabled:
            try:
                import pyaudio
                self._init_audio()
            except ImportError:
                print("⚠️  PyAudio not available, falling back to text mode")
                self.audio_enabled = False
        
    def _init_audio(self):
        """Initialize audio components if available"""
        try:
            import pyaudio
            
            self.pa = pyaudio.PyAudio()
            
            # Audio input stream
            self.audio_in = self.pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=24000,
                input=True,
                frames_per_buffer=1024
            )
            
            # Audio output stream  
            self.audio_out = self.pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=24000,
                output=True,
                frames_per_buffer=1024
            )
            
        except Exception as e:
            print(f"⚠️  Audio initialization failed: {e}")
            self.audio_enabled = False
        
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
        
        header_list = [(key, value) for key, value in headers.items()]
        self.ws = await websockets.connect(uri, additional_headers=header_list)
        
        await self.send_session_update()
        
    async def send_session_update(self):
        """Configure the session with tools and settings"""
        modalities = ["text", "audio"] if self.audio_enabled else ["text"]
        
        session_config = {
            "type": "session.update",
            "session": {
                "modalities": modalities,
                "instructions": """You are an intelligent cafe service robot with conversational AI capabilities.

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

ORDERING FLOW:
1. Greet customer and offer menu/recommendations
2. Help browse menu by category if needed
3. Add items with customizations
4. Confirm order details and total
5. Process payment
6. Provide order status and estimated time

ROBOT ACTIONS:
- Always confirm before moving
- Explain what you're doing
- Report status when asked
- Use LEDs and sounds for better interaction

Be conversational and natural - you're both a helpful cafe assistant and a capable service robot!""",
                "voice": "alloy",
                "input_audio_format": "pcm16" if self.audio_enabled else None,
                "output_audio_format": "pcm16" if self.audio_enabled else None,
                "input_audio_transcription": {
                    "model": "whisper-1"
                } if self.audio_enabled else None,
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 200
                } if self.audio_enabled else None,
                "tools": self.function_schemas
            }
        }
        
        await self.ws.send(json.dumps(session_config))
        
    async def send_text_message(self, text: str):
        """Send text message to the API"""
        if self.ws:
            message = {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "text", "text": text}]
                }
            }
            await self.ws.send(json.dumps(message))
            
            # Trigger response
            response_trigger = {"type": "response.create"}
            await self.ws.send(json.dumps(response_trigger))
            
    async def send_audio_data(self, audio_data: bytes):
        """Send audio data to the API"""
        if self.ws and self.audio_enabled:
            import base64
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
        
        if msg_type == "response.text.delta":
            text = data.get("delta", "")
            print(text, end="", flush=True)
            
        elif msg_type == "response.audio.delta":
            if self.audio_enabled and self.audio_out:
                audio_data = data.get("delta", "")
                if audio_data:
                    import base64
                    audio_bytes = base64.b64decode(audio_data)
                    self.audio_out.write(audio_bytes)
                    
        elif msg_type == "response.function_call_delta":
            if data.get("delta"):
                await self.handle_function_call(data)
                
        elif msg_type == "response.done":
            print()  # New line after response
            
        elif msg_type == "input_audio_buffer.speech_started":
            print("🎤 Listening...")
            
        elif msg_type == "input_audio_buffer.speech_stopped":
            print("🔇 Processing...")
            
        elif msg_type == "error":
            print(f"\n❌ Error: {data}")
            
    async def handle_function_call(self, data: Dict):
        """Execute function calls from the AI"""
        function_name = data.get("name")
        arguments = data.get("arguments", "{}")
        call_id = data.get("call_id")
        
        try:
            args = json.loads(arguments)
            if function_name in self.functions:
                print(f"\n🔧 Executing: {function_name}({args})")
                result = await self.functions[function_name](**args)
                print(f"📋 Result: {result}")
                
                # Send function result back
                response = {
                    "type": "conversation.item.create",
                    "item": {
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": str(result)
                    }
                }
                await self.ws.send(json.dumps(response))
                
        except Exception as e:
            print(f"❌ Function call error: {e}")
            error_response = {
                "type": "conversation.item.create",
                "item": {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": f"Error: {str(e)}"
                }
            }
            await self.ws.send(json.dumps(error_response))
            
    async def audio_input_loop(self):
        """Capture and send audio input"""
        if not self.audio_enabled or not self.audio_in:
            return
            
        print("🎤 Audio input active (speak normally)")
        
        while self.running:
            try:
                # Read audio data
                audio_data = self.audio_in.read(1024, exception_on_overflow=False)
                await self.send_audio_data(audio_data)
                await asyncio.sleep(0.01)  # Small delay
                
            except Exception as e:
                print(f"Audio input error: {e}")
                break
                
    async def text_input_loop(self):
        """Text-based interaction loop"""
        print("💬 Text input active. Type your messages (or 'quit' to exit):")
        
        while self.running:
            try:
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, input, "\n👤 You: "
                )
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    self.running = False
                    break
                    
                await self.send_text_message(user_input)
                print("🤖 Assistant: ", end="", flush=True)
                
            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                print(f"Text input error: {e}")
                
    async def run(self, mode: str = "auto"):
        """Main loop for the unified agent
        
        Args:
            mode: "voice", "text", or "auto" (auto-detect based on audio availability)
        """
        await self.connect()
        
        # Determine input mode
        if mode == "auto":
            input_mode = "voice" if self.audio_enabled else "text"
        else:
            input_mode = mode
            
        if input_mode == "voice" and not self.audio_enabled:
            print("⚠️  Voice mode requested but audio not available, switching to text mode")
            input_mode = "text"
            
        print(f"🚀 Starting in {input_mode.upper()} mode")
        
        # Start message handler
        message_task = asyncio.create_task(self.handle_messages())
        
        # Start appropriate input loop
        self.running = True
        
        try:
            if input_mode == "voice":
                audio_task = asyncio.create_task(self.audio_input_loop())
                await audio_task
            else:
                await self.text_input_loop()
                
        except websockets.exceptions.ConnectionClosed:
            print("🔌 Connection closed")
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
        finally:
            self.running = False
            message_task.cancel()
            
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        
        if self.audio_enabled:
            if self.audio_in:
                self.audio_in.stop_stream()
                self.audio_in.close()
            if self.audio_out:
                self.audio_out.stop_stream()
                self.audio_out.close()
            if hasattr(self, 'pa'):
                self.pa.terminate()
                
        if self.ws:
            asyncio.create_task(self.ws.close())