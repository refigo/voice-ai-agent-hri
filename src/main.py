#!/usr/bin/env python3
"""
Main entry point for the Voice AI Agent HRI system.
"""

import asyncio
import signal
import sys
from voice_agent import VoiceAIAgent
from hri_functions import RobotController, HRI_FUNCTION_SCHEMAS

class VoiceHRISystem:
    def __init__(self):
        self.agent = VoiceAIAgent()
        self.robot = RobotController()
        self.running = False
        
    def setup_functions(self):
        """Register HRI functions with the voice agent"""
        # Register each robot function with the agent
        for schema in HRI_FUNCTION_SCHEMAS:
            func_name = schema["name"]
            func = getattr(self.robot, func_name)
            self.agent.register_function(func_name, func, schema)
            
        print(f"Registered {len(HRI_FUNCTION_SCHEMAS)} HRI functions")
        
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            print("\nShutting down gracefully...")
            self.running = False
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    async def run(self):
        """Main run loop"""
        print("Starting Voice AI Agent for HRI...")
        
        self.setup_functions()
        self.setup_signal_handlers()
        
        try:
            self.running = True
            print("Connecting to OpenAI Realtime API...")
            
            # Start the voice agent
            await self.agent.run()
            
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            print("Cleaning up...")
            self.agent.cleanup()
            
def main():
    """Main function"""
    print("Voice AI Agent HRI System")
    print("=" * 30)
    
    # Check for required environment variables
    import os
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please create a .env file with your OpenAI API key")
        sys.exit(1)
        
    system = VoiceHRISystem()
    
    try:
        asyncio.run(system.run())
    except Exception as e:
        print(f"Failed to start system: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()