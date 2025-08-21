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
import queue
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
        
        # Voice interruption management
        self.is_speaking = False
        self.current_response_id = None
        self.audio_queue = asyncio.Queue() if audio_enabled else None
        self.interruption_enabled = True
        self.message_queue = queue.Queue()
        
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
        
    def enable_interruption(self):
        """Enable voice interruption capability"""
        self.interruption_enabled = True
        print("✅ Voice interruption enabled")
        
    def disable_interruption(self):
        """Disable voice interruption capability"""
        self.interruption_enabled = False
        print("⚠️  Voice interruption disabled")
        
    def connect(self):
        """Connect to OpenAI Realtime API"""
        from websocket import WebSocketApp
        
        uri = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
        headers = [
            f"Authorization: Bearer {self.api_key}",
            "OpenAI-Beta: realtime=v1"
        ]
        
        def on_open(ws):
            print("✅ Connected to OpenAI Realtime API")
            # Queue session update message
            self.message_queue.put({"type": "session_update"})
        
        def on_message(ws, message):
            data = json.loads(message)
            print("Received message:", data)
            # Queue the message for processing
            self.message_queue.put(data)
        
        def on_error(ws, error):
            print(f"❌ WebSocket error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            print("🔌 Connection closed")
        
        self.ws = WebSocketApp(
            uri,
            header=headers,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        
        # Start connection in a separate thread
        import threading
        self.ws_thread = threading.Thread(target=self.ws.run_forever, daemon=True)
        self.ws_thread.start()
        
    async def send_session_update(self):
        """Configure the session with tools and settings"""
        modalities = ["text", "audio"] if self.audio_enabled else ["text"]
        
        # Build session config conditionally
        session_data = {
            "modalities": modalities,
            "instructions": """You are an intelligent cafe service robot with conversational AI capabilities, voice interruption support, and kiosk UI control.

CORE CAPABILITIES:
1. CAFE ORDERING: Help customers browse menu, place orders, customize items, process payments
2. ROBOT CONTROL: Move around, control LEDs, take photos, scan environment  
3. KIOSK UI CONTROL: Display menus, highlight items, navigate screens, show cart contents
- Always be friendly, helpful, and professional
- Support natural conversation flow with voice interruptions
- Keep responses concise to allow for interruptions
- For ordering: Guide customers through menu, suggest items, confirm details
- For robot control: Confirm movements for safety, explain actions
- Use appropriate functions based on customer requests
- Ask clarifying questions when needed
- Provide clear status updates

VOICE INTERACTION:
- Customers can interrupt you at any time by speaking
- Gracefully handle interruptions and respond to new input
- Keep responses natural and conversational
- Pause appropriately to allow customer input

ORDERING FLOW:
1. Greet customer and offer menu/recommendations
2. Take order with customizations
3. Confirm order details and total
4. Process payment
5. Provide order status and pickup info

ROBOT ACTIONS:
- Move safely and announce movements
- Use LEDs and sounds for better interaction

KIOSK UI ACTIONS:
- Display appropriate screens based on customer needs
- Highlight menu items when mentioned
- Show cart contents when discussing orders
- Navigate between screens smoothly
- Use visual feedback to enhance conversation

Be conversational and natural - you're both a helpful cafe assistant and a capable service robot that supports dynamic voice interaction with visual kiosk displays!""",
            "tools": self.function_schemas
        }
        
        # Add audio-specific settings only if audio is enabled
        if self.audio_enabled:
            session_data.update({
                "voice": "alloy",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {"model": "whisper-1"},
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.3,
                    "prefix_padding_ms": 200,
                    "silence_duration_ms": 150
                }
            })
        
        session_config = {
            "type": "session.update",
            "session": session_data
        }
        
        if self.ws:
            self.ws.send(json.dumps(session_config))
        
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
            self.ws.send(json.dumps(message))
            
            # Trigger response
            response_trigger = {"type": "response.create"}
            self.ws.send(json.dumps(response_trigger))
            
    async def send_audio_data(self, audio_data: bytes):
        """Send audio data to the API"""
        if self.ws and self.audio_enabled:
            import base64
            audio_message = {
                "type": "input_audio_buffer.append",
                "audio": base64.b64encode(audio_data).decode()
            }
            self.ws.send(json.dumps(audio_message))
            
    async def cancel_response(self):
        """Cancel current AI response for interruption"""
        if self.ws and self.current_response_id:
            cancel_message = {
                "type": "response.cancel"
            }
            self.ws.send(json.dumps(cancel_message))
            print("\n⏸️  Response cancelled due to interruption")
            
    async def clear_audio_output_buffer(self):
        """Clear the audio output buffer to stop current speech"""
        if self.audio_out:
            # Stop current audio output
            self.audio_out.stop_stream()
            self.audio_out.close()
            
            # Reinitialize audio output
            import pyaudio
            self.audio_out = self.pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=24000,
                output=True,
                frames_per_buffer=1024
            )
            
    async def commit_audio_buffer(self):
        """Commit the current audio buffer when user starts speaking"""
        if self.ws:
            commit_message = {
                "type": "input_audio_buffer.commit"
            }
            self.ws.send(json.dumps(commit_message))
            
    async def handle_messages(self):
        """Handle incoming messages from the API"""
        while self.running:
            try:
                # Process messages from the queue
                try:
                    message = self.message_queue.get_nowait()
                    if message.get("type") == "session_update":
                        await self.send_session_update()
                    else:
                        await self.process_message(message)
                    self.message_queue.task_done()
                except queue.Empty:
                    await asyncio.sleep(0.1)
            except Exception as e:
                print(f"Message handling error: {e}")
                break
                
    async def process_message(self, data: Dict):
        """Process different types of messages from the API"""
        msg_type = data.get("type")
        
        if msg_type == "response.created":
            # Track current response for interruption handling
            self.current_response_id = data.get("response", {}).get("id")
            self.is_speaking = True
            
        elif msg_type == "response.text.delta":
            text = data.get("delta", "")
            print(text, end="", flush=True)
            
        elif msg_type == "response.audio.delta":
            if self.audio_enabled and self.audio_out and self.is_speaking:
                audio_data = data.get("delta", "")
                if audio_data:
                    import base64
                    audio_bytes = base64.b64decode(audio_data)
                    try:
                        self.audio_out.write(audio_bytes)
                    except Exception as e:
                        # Audio output might be interrupted, continue silently
                        pass
                    
        elif msg_type == "response.function_call_delta":
            if data.get("delta"):
                await self.handle_function_call(data)
                
        elif msg_type == "response.function_call_arguments.delta":
            # Handle function call arguments delta
            print("🔧 Function call in progress...", end="", flush=True)
            
        elif msg_type == "response.function_call_arguments.done":
            # Function call arguments completed
            if data.get("name") and data.get("arguments"):
                await self.handle_function_call_complete(data)
                
        elif msg_type == "response.output_item.added":
            # New output item added to response
            item = data.get("item", {})
            if item.get("type") == "function_call":
                print(f"\n🔧 Function call: {item.get('name', 'unknown')}")
                
        elif msg_type == "response.output_item.done":
            # Output item completed
            item = data.get("item", {})
            if item.get("type") == "function_call":
                print("✅ Function call completed")
                
        elif msg_type == "response.done":
            self.is_speaking = False
            self.current_response_id = None
            print()  # New line after response
            
        elif msg_type == "response.cancelled":
            self.is_speaking = False
            self.current_response_id = None
            print("\n🚫 Response interrupted")
            
        elif msg_type == "input_audio_buffer.speech_started":
            print("🎤 You're speaking...")
            
            # Handle interruption if AI is currently speaking
            if self.is_speaking and self.interruption_enabled:
                print("⚡ Interruption detected - stopping AI response")
                await self.cancel_response()
                await self.clear_audio_output_buffer()
                await self.commit_audio_buffer()
            
        elif msg_type == "input_audio_buffer.speech_stopped":
            print("🔇 Processing your message...")
            
        elif msg_type == "input_audio_buffer.committed":
            # Buffer committed, trigger new response
            if self.ws:
                response_trigger = {"type": "response.create"}
                self.ws.send(json.dumps(response_trigger))
            
        elif msg_type == "conversation.item.created":
            # New conversation item created (user speech transcribed)
            if data.get("item", {}).get("type") == "message":
                content = data.get("item", {}).get("content", [])
                if content and content[0].get("type") == "input_text":
                    transcript = content[0].get("text", "")
                    print(f"👤 You said: {transcript}")
                    
        elif msg_type == "conversation.item.input_audio_transcription.delta":
            # Real-time transcription delta
            delta = data.get("delta", "")
            if delta:
                print(delta, end="", flush=True)
                
        elif msg_type == "conversation.item.input_audio_transcription.completed":
            # Transcription completed
            transcript = data.get("transcript", "")
            if transcript:
                print(f"\n👤 You said: {transcript}")
            
        elif msg_type == "error":
            print(f"\n❌ Error: {data}")
            
        elif msg_type == "session.updated":
            print("✅ Session configured for voice interruption")
            
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
                self.ws.send(json.dumps(response))
                
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
            self.ws.send(json.dumps(error_response))
            
    async def handle_function_call_complete(self, data: Dict):
        """Handle completed function call with arguments"""
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
                self.ws.send(json.dumps(response))
                
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
            self.ws.send(json.dumps(error_response))
            
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
        self.connect()
        
        # Determine input mode
        if mode == "auto":
            input_mode = "voice" if self.audio_enabled else "text"
        else:
            input_mode = mode
            
        if input_mode == "voice" and not self.audio_enabled:
            print("⚠️  Voice mode requested but audio not available, switching to text mode")
            input_mode = "text"
            
        print(f"🚀 Starting in {input_mode.upper()} mode")
        
        if input_mode == "voice":
            print("⚡ Voice interruption enabled - you can interrupt the AI at any time")
            print("🎤 Speak naturally and interrupt freely for dynamic conversation")
        
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
        self.ws = None
        self.ws_thread = None
        self.message_queue = queue.Queue()
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