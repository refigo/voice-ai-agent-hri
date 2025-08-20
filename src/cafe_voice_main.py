#!/usr/bin/env python3
"""
Main entry point for the Voice AI Cafe Robot with improved audio handling
"""

import asyncio
import signal
import sys
import os
from voice_agent_improved import VoiceAIAgentImproved
from hri_functions import RobotController, HRI_FUNCTION_SCHEMAS
from cafe_system import CafeKioskSystem, CAFE_FUNCTION_SCHEMAS

class CafeVoiceRobot:
    def __init__(self):
        self.agent = VoiceAIAgentImproved()
        self.cafe_system = CafeKioskSystem()
        self.robot = RobotController()
        self.running = False
        
    def setup_functions(self):
        """Register both cafe and robot functions"""
        
        # Register cafe functions
        for schema in CAFE_FUNCTION_SCHEMAS:
            func_name = schema["name"]
            func = getattr(self.cafe_system, func_name)
            self.agent.register_function(func_name, func, schema)
            
        # Register robot functions
        for schema in HRI_FUNCTION_SCHEMAS:
            func_name = schema["name"]
            func = getattr(self.robot, func_name)
            self.agent.register_function(func_name, func, schema)
            
        print(f"✅ Registered {len(CAFE_FUNCTION_SCHEMAS)} cafe functions")
        print(f"✅ Registered {len(HRI_FUNCTION_SCHEMAS)} robot functions")
        print(f"📊 Total functions: {len(CAFE_FUNCTION_SCHEMAS) + len(HRI_FUNCTION_SCHEMAS)}")
        
    async def start_service(self):
        """Start the cafe voice robot service"""
        print("🤖 ☕ VOICE AI CAFE ROBOT")
        print("=" * 40)
        
        # Setup all functions
        self.setup_functions()
        
        print("\n🏪 Cafe System: Online")
        print("🤖 Robot System: Online")
        print("🎤 Audio System: Ready")
        
        try:
            self.running = True
            
            # Start the voice agent
            await self.agent.run()
            
        except KeyboardInterrupt:
            print("\n👋 Service stopped by user")
        except Exception as e:
            print(f"❌ Service error: {e}")
        finally:
            print("🧹 Cleaning up...")
            self.agent.cleanup()

def setup_signal_handlers(robot):
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum}")
        print("Shutting down voice AI cafe robot...")
        robot.running = False
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def check_environment():
    """Check environment setup"""
    print("🔧 ENVIRONMENT CHECK:")
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found")
        print("   Please set your OpenAI API key in .env file")
        return False
    else:
        print("✅ OpenAI API key configured")
    
    # Check audio dependencies
    try:
        import pyaudio
        pa = pyaudio.PyAudio()
        device_count = pa.get_device_count()
        pa.terminate()
        print(f"✅ PyAudio available ({device_count} audio devices)")
    except ImportError:
        print("❌ PyAudio not available")
        return False
    except Exception as e:
        print(f"⚠️  Audio setup warning: {e}")
    
    # Check other dependencies
    try:
        import websockets
        print("✅ WebSockets available")
    except ImportError:
        print("❌ WebSockets not available")
        return False
        
    return True

def print_voice_examples():
    """Print example voice commands"""
    print("\n🎤 VOICE COMMAND EXAMPLES:")
    print("\n☕ CAFE ORDERING:")
    print("  • 'Hello, I'd like to see the menu'")
    print("  • 'Can you show me the coffee options?'")
    print("  • 'I want a large latte with oat milk'")
    print("  • 'Add a blueberry muffin to my order'")
    print("  • 'What's my total so far?'")
    print("  • 'I'd like to pay with my card'")
    print("  • 'Can you recommend something cold?'")
    
    print("\n🤖 ROBOT CONTROL:")
    print("  • 'Move forward two meters'")
    print("  • 'Turn left and scan the area'")
    print("  • 'What's your current status?'")
    print("  • 'Set your LED to blue'")
    print("  • 'Take a photo'")
    print("  • 'Stop moving immediately'")
    
    print("\n🔄 COMBINED INTERACTIONS:")
    print("  • 'Take my order then move to table three'")
    print("  • 'Show me the menu and set LED to green'")
    print("  • 'After I pay, scan the environment'")
    print("  • 'Help me order coffee and take a photo'")

async def main():
    """Main function"""
    print("🤖 ☕ VOICE AI CAFE ROBOT")
    print("=" * 50)
    
    # Environment check
    if not check_environment():
        print("\n❌ Environment check failed. Please fix the issues above.")
        sys.exit(1)
        
    print_voice_examples()
    
    # Create and configure the robot
    robot = CafeVoiceRobot()
    setup_signal_handlers(robot)
    
    print("\n" + "=" * 50)
    print("🚀 Starting Voice AI Cafe Robot...")
    print("🎯 Speak naturally after you see 'Recording started'")
    print("💬 I understand both cafe orders and robot commands!")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        await robot.start_service()
    except Exception as e:
        print(f"\n❌ Failed to start robot service: {e}")
        print("💡 Make sure your OpenAI API key is valid and you have internet connection")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)