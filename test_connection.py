#!/usr/bin/env python3
"""
Simple test to verify OpenAI Realtime API connection
"""

import asyncio
import websockets
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def test_connection():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return False
        
    uri = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
    headers = [
        ("Authorization", f"Bearer {api_key}"),
        ("OpenAI-Beta", "realtime=v1")
    ]
    
    try:
        print("🔗 Connecting to OpenAI Realtime API...")
        
        async with websockets.connect(uri, additional_headers=headers) as ws:
            print("✅ Connected successfully!")
            
            # Send session config
            session_config = {
                "type": "session.update",
                "session": {
                    "modalities": ["text"],
                    "instructions": "You are a helpful assistant."
                }
            }
            
            await ws.send(json.dumps(session_config))
            print("📤 Sent session configuration")
            
            # Wait for response
            response = await asyncio.wait_for(ws.recv(), timeout=10.0)
            data = json.loads(response)
            print(f"📥 Received: {data.get('type', 'unknown')}")
            
            # Send a test message
            message = {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "text", "text": "Hello, can you say hi back?"}]
                }
            }
            
            await ws.send(json.dumps(message))
            print("📤 Sent test message")
            
            # Trigger response
            response_trigger = {"type": "response.create"}
            await ws.send(json.dumps(response_trigger))
            print("📤 Triggered response")
            
            # Listen for responses
            for _ in range(5):  # Listen for up to 5 messages
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                    data = json.loads(response)
                    msg_type = data.get('type', 'unknown')
                    print(f"📥 Received: {msg_type}")
                    
                    if msg_type == "response.text.delta":
                        text = data.get('delta', '')
                        print(f"💬 Text: {text}")
                    elif msg_type == "response.done":
                        print("✅ Response completed")
                        break
                        
                except asyncio.TimeoutError:
                    print("⏰ Timeout waiting for response")
                    break
                    
        print("✅ Connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    if success:
        print("\n🎉 OpenAI Realtime API connection works!")
        print("You can now run the cafe service robot.")
    else:
        print("\n💔 Connection test failed.")
        print("Please check your API key and internet connection.")