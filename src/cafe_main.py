#!/usr/bin/env python3
"""
Main entry point for the Cafe Service Robot with Voice AI Agent
Integrates HRI robot control with cafe kiosk ordering system
"""

import asyncio
import signal
import sys
import os
from cafe_voice_agent import CafeServiceRobot

def print_welcome():
    """Print welcome message and system information"""
    print("🤖 ☕ CAFE SERVICE ROBOT")
    print("=" * 50)
    print("🎯 Features:")
    print("  • Voice-controlled cafe ordering system")
    print("  • Robot movement and interaction")
    print("  • Menu browsing and recommendations")
    print("  • Order management and payment processing")
    print("  • Real-time conversation with OpenAI")
    print("=" * 50)

def print_voice_commands():
    """Print example voice commands"""
    print("\n🎤 EXAMPLE VOICE COMMANDS:")
    print("\n☕ CAFE ORDERING:")
    print("  • 'Show me the menu'")
    print("  • 'I'd like a latte with oat milk'")
    print("  • 'Add a blueberry muffin to my order'")
    print("  • 'What do you recommend for something cold?'")
    print("  • 'Can I see my current order?'")
    print("  • 'I'd like to pay with card'")
    print("  • 'Cancel my order'")
    
    print("\n🤖 ROBOT CONTROL:")
    print("  • 'Move forward 2 meters'")
    print("  • 'Turn left and scan the area'")
    print("  • 'What's your current status?'")
    print("  • 'Set LED to blue'")
    print("  • 'Take a photo'")
    print("  • 'Stop moving'")
    
    print("\n🔄 COMBINED INTERACTIONS:")
    print("  • 'Bring me the menu and help me order'")
    print("  • 'After I order, move to the pickup area'")
    print("  • 'Check my order status and move to table 3'")

def setup_signal_handlers(robot):
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum}")
        print("Shutting down cafe service robot...")
        robot.running = False
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def check_environment():
    """Check environment setup"""
    print("\n🔧 ENVIRONMENT CHECK:")
    
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
        print("✅ PyAudio available")
    except ImportError:
        print("⚠️  PyAudio not available - audio features may not work")
        print("   Install with: pip install pyaudio")
    
    # Check other dependencies
    try:
        import websockets
        print("✅ WebSockets available")
    except ImportError:
        print("❌ WebSockets not available")
        return False
        
    return True

async def main():
    """Main function"""
    print_welcome()
    
    # Environment check
    if not check_environment():
        print("\n❌ Environment check failed. Please fix the issues above.")
        sys.exit(1)
    
    print_voice_commands()
    
    # Create and configure the robot
    robot = CafeServiceRobot()
    setup_signal_handlers(robot)
    
    print("\n🚀 Starting Cafe Service Robot...")
    print("📱 Speak naturally - I understand both cafe orders and robot commands!")
    print("🎯 Say 'hello' or 'show me the menu' to get started")
    print("\n" + "=" * 50)
    
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