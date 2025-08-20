"""
Voice AI Agent without PyAudio dependency for testing
Uses text-based interaction instead of audio
"""

import asyncio
import websockets
import json
import base64
import threading
from typing import Dict, List, Callable, Any
import os
from dotenv import load_dotenv

load_dotenv()

class VoiceAIAgentNoAudio:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.ws = None
        
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
        
        # Convert headers to the format expected by websockets
        header_list = [(key, value) for key, value in headers.items()]
        self.ws = await websockets.connect(uri, additional_headers=header_list)
        
        # Configure session
        await self.send_session_update()
        
    async def send_session_update(self):
        """Configure the session with tools and settings"""
        session_config = {
            "type": "session.update",
            "session": {
                "modalities": ["text"],  # Text only for now
                "instructions": "You are a helpful AI assistant for human-robot interaction and cafe service. Use the available functions to control robot actions and process cafe orders when requested.",
                "input_audio_transcription": None,
                "turn_detection": None,
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
            
    async def handle_messages(self):
        """Handle incoming messages from the API"""
        async for message in self.ws:
            data = json.loads(message)
            await self.process_message(data)
            
    async def process_message(self, data: Dict):
        """Process different types of messages from the API"""
        msg_type = data.get("type")
        
        if msg_type == "response.text.delta":
            # Print text response
            text = data.get("delta", "")
            print(text, end="", flush=True)
            
        elif msg_type == "response.function_call_delta":
            # Handle function calling
            if data.get("delta"):
                await self.handle_function_call(data)
                
        elif msg_type == "response.done":
            print("\n")  # New line after response
            
        elif msg_type == "error":
            print(f"\nError: {data}")
            
    async def handle_function_call(self, data: Dict):
        """Execute function calls from the AI"""
        function_name = data.get("name")
        arguments = data.get("arguments", "{}")
        
        try:
            args = json.loads(arguments)
            if function_name in self.functions:
                print(f"\n🔧 Executing: {function_name}({args})")
                result = await self.functions[function_name](**args)
                print(f"📋 Result: {result}\n")
                
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
            
    async def text_interaction_loop(self):
        """Text-based interaction loop"""
        print("💬 Text mode active. Type your messages (or 'quit' to exit):")
        
        while True:
            try:
                user_input = input("\n👤 You: ")
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                    
                await self.send_text_message(user_input)
                print("🤖 Assistant: ", end="", flush=True)
                
                # Wait a bit for the response
                await asyncio.sleep(1)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
                
    async def run(self):
        """Main loop for the voice agent"""
        await self.connect()
        
        # Start message handler
        message_task = asyncio.create_task(self.handle_messages())
        
        try:
            await self.text_interaction_loop()
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed")
        finally:
            message_task.cancel()
            
    def cleanup(self):
        """Clean up resources"""
        if self.ws:
            asyncio.create_task(self.ws.close())