#!/usr/bin/env python3
"""
Simple voice test to debug issues
"""

import asyncio
import pyaudio
import sys
import os
from dotenv import load_dotenv

load_dotenv()

def test_audio():
    """Test audio setup"""
    print("🔊 Testing audio setup...")
    
    try:
        audio = pyaudio.PyAudio()
        print(f"✅ PyAudio initialized")
        print(f"📊 Available devices: {audio.get_device_count()}")
        
        # Test input device
        for i in range(audio.get_device_count()):
            device_info = audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                print(f"🎤 Input device {i}: {device_info['name']}")
                break
        
        # Test output device  
        for i in range(audio.get_device_count()):
            device_info = audio.get_device_info_by_index(i)
            if device_info['maxOutputChannels'] > 0:
                print(f"🔊 Output device {i}: {device_info['name']}")
                break
                
        audio.terminate()
        return True
        
    except Exception as e:
        print(f"❌ Audio test failed: {e}")
        return False

def test_api_key():
    """Test API key"""
    print("🔑 Testing API key...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return False
    
    if api_key.startswith("sk-"):
        print("✅ API key format looks correct")
        return True
    else:
        print("⚠️  API key format may be incorrect")
        return False

async def test_connection():
    """Test WebSocket connection"""
    print("🔗 Testing WebSocket connection...")
    
    try:
        import websockets
        import json
        
        api_key = os.getenv("OPENAI_API_KEY")
        uri = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
        headers = [
            ("Authorization", f"Bearer {api_key}"),
            ("OpenAI-Beta", "realtime=v1")
        ]
        
        async with websockets.connect(uri, additional_headers=headers) as ws:
            print("✅ WebSocket connected")
            
            # Send basic session config
            session_config = {
                "type": "session.update",
                "session": {
                    "modalities": ["text"],
                    "instructions": "You are a helpful assistant."
                }
            }
            
            await ws.send(json.dumps(session_config))
            print("📤 Sent session config")
            
            # Wait for response
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)
            data = json.loads(response)
            print(f"📥 Received: {data.get('type', 'unknown')}")
            
        print("✅ Connection test passed")
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 VOICE AI SYSTEM DIAGNOSTICS")
    print("=" * 40)
    
    results = []
    
    # Test 1: Audio
    print("\n1️⃣  AUDIO TEST")
    results.append(test_audio())
    
    # Test 2: API Key
    print("\n2️⃣  API KEY TEST")
    results.append(test_api_key())
    
    # Test 3: Connection
    print("\n3️⃣  CONNECTION TEST")
    results.append(await test_connection())
    
    print("\n" + "=" * 40)
    print("📊 RESULTS:")
    
    tests = ["Audio", "API Key", "Connection"]
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {test}: {status}")
    
    if all(results):
        print("\n🎉 ALL TESTS PASSED!")
        print("Your system is ready for voice AI!")
        
        print("\n🚀 Next steps:")
        print("1. Run: python3 src/cafe_voice_main.py")
        print("2. Wait for 'Recording started' message")
        print("3. Speak: 'Hello, show me the menu'")
        
    else:
        print("\n💔 Some tests failed.")
        print("Please check the errors above.")
        
        if not results[0]:  # Audio failed
            print("\n🔧 Audio troubleshooting:")
            print("- Check if microphone is connected")
            print("- Try: sudo apt-get install python3-pyaudio")
            
        if not results[1]:  # API key failed
            print("\n🔧 API Key troubleshooting:")
            print("- Check .env file has OPENAI_API_KEY=sk-...")
            print("- Verify API key is valid")
            
        if not results[2]:  # Connection failed
            print("\n🔧 Connection troubleshooting:")
            print("- Check internet connection")
            print("- Verify API key has Realtime API access")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted")
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        sys.exit(1)