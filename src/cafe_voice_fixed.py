#!/usr/bin/env python3
"""
Fixed Cafe Voice Robot with resolved audio duplication issues
"""

import asyncio
import signal
import sys
import os
from voice_agent_fixed import VoiceAIAgentFixed
from hri_functions import RobotController, HRI_FUNCTION_SCHEMAS
from cafe_system import CafeKioskSystem, CAFE_FUNCTION_SCHEMAS

class CafeVoiceRobotFixed:
    def __init__(self):
        self.agent = VoiceAIAgentFixed()
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
        print("🤖 ☕ VOICE AI CAFE ROBOT (FIXED)")
        print("=" * 45)
        
        # Setup all functions
        self.setup_functions()
        
        print("\n🏪 Cafe System: Online")
        print("🤖 Robot System: Online")
        print("🎤 Audio System: Ready (No Duplication)")
        
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
        exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

async def main():
    """Main function"""
    print("🤖 ☕ VOICE AI CAFE ROBOT (FIXED VERSION)")
    print("=" * 55)
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found")
        print("Please set your OpenAI API key in .env file")
        sys.exit(1)
    else:
        print("✅ OpenAI API key configured")
    
    print("\n🔧 FIXES APPLIED:")
    print("• ✅ Eliminated audio duplication")
    print("• ✅ Improved response tracking")
    print("• ✅ Better speech detection")
    print("• ✅ Reduced false triggers")
    print("• ✅ Cleaner audio feedback")
    
    print("\n💡 VOICE COMMANDS:")
    print("☕ 'Hello, show me the coffee menu'")
    print("🤖 'Move forward 2 meters'")
    print("🔄 'Take my order then move to table 3'")
    
    # Create and configure the robot
    robot = CafeVoiceRobotFixed()
    setup_signal_handlers(robot)
    
    print("\n" + "=" * 55)
    print("🚀 Starting Fixed Voice AI Cafe Robot...")
    print("🎯 No more audio duplication!")
    print("💬 Speak clearly after 'Recording started'")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 55)
    
    try:
        await robot.start_service()
    except Exception as e:
        print(f"\n❌ Failed to start robot service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)