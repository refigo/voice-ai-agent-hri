#!/usr/bin/env python3
"""
Text-based version of the Cafe Service Robot
For testing without audio dependencies
"""

import asyncio
import signal
import sys
import os
from voice_agent_no_audio import VoiceAIAgentNoAudio
from hri_functions import RobotController, HRI_FUNCTION_SCHEMAS
from cafe_system import CafeKioskSystem, CAFE_FUNCTION_SCHEMAS

class CafeVoiceAgentText(VoiceAIAgentNoAudio):
    def __init__(self):
        super().__init__()
        self.cafe_system = CafeKioskSystem()
        self.robot = RobotController()
        self.conversation_context = {
            "mode": "general",
            "last_interaction": None,
            "customer_preferences": {},
            "order_in_progress": False
        }
        
    def setup_functions(self):
        """Register both cafe and robot functions"""
        
        # Register cafe functions
        for schema in CAFE_FUNCTION_SCHEMAS:
            func_name = schema["name"]
            func = getattr(self.cafe_system, func_name)
            self.register_function(func_name, func, schema)
            
        # Register robot functions
        for schema in HRI_FUNCTION_SCHEMAS:
            func_name = schema["name"]
            func = getattr(self.robot, func_name)
            self.register_function(func_name, func, schema)
            
        print(f"✅ Registered {len(CAFE_FUNCTION_SCHEMAS)} cafe functions")
        print(f"✅ Registered {len(HRI_FUNCTION_SCHEMAS)} robot functions")
        
    async def send_session_update(self):
        """Enhanced session configuration with cafe context"""
        session_config = {
            "type": "session.update",
            "session": {
                "modalities": ["text"],
                "instructions": """You are an intelligent cafe service robot with text interaction capabilities. 

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
                "tools": self.function_schemas
            }
        }
        
        await self.ws.send(json.dumps(session_config))

class CafeServiceRobotText:
    """Text-based cafe service robot"""
    
    def __init__(self):
        self.agent = CafeVoiceAgentText()
        self.running = False
        
    async def start_service(self):
        """Start the cafe service robot in text mode"""
        print("🤖 ☕ CAFE SERVICE ROBOT (Text Mode)")
        print("=" * 50)
        
        # Setup all functions
        self.agent.setup_functions()
        
        print("\n🏪 Cafe System Initialized")
        print("📋 Menu loaded with items across 4 categories")
        print("💳 Payment system ready")
        print("🤖 Robot systems online")
        
        try:
            self.running = True
            print("\n🔗 Connecting to OpenAI Realtime API...")
            
            # Start the voice agent
            await self.agent.run()
            
        except KeyboardInterrupt:
            print("\n👋 Service stopped by operator")
        except Exception as e:
            print(f"❌ Service error: {e}")
        finally:
            print("🧹 Cleaning up...")
            self.agent.cleanup()

def print_example_commands():
    """Print example commands"""
    print("\n💡 EXAMPLE COMMANDS:")
    print("\n☕ CAFE ORDERING:")
    print("  • 'Show me the coffee menu'")
    print("  • 'I want a latte with oat milk'")
    print("  • 'Add a blueberry muffin'")
    print("  • 'What's my order total?'")
    print("  • 'I want to pay with card'")
    
    print("\n🤖 ROBOT CONTROL:")
    print("  • 'Move forward 2 meters'")
    print("  • 'Turn left and check status'")
    print("  • 'Set LED to blue'")
    print("  • 'Take a photo'")
    
    print("\n🔄 COMBINED:")
    print("  • 'Take my order then move to table 3'")
    print("  • 'Show menu and recommend something cold'")

async def main():
    """Main function"""
    print("🤖 ☕ CAFE SERVICE ROBOT - TEXT MODE")
    print("=" * 50)
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found")
        print("Please set your OpenAI API key in .env file")
        sys.exit(1)
    else:
        print("✅ OpenAI API key configured")
    
    print_example_commands()
    
    robot = CafeServiceRobotText()
    
    print("\n🚀 Starting Cafe Service Robot (Text Mode)...")
    print("💬 Type your requests naturally!")
    print("🎯 Try: 'Hello, show me the menu' to get started")
    print("\n" + "=" * 50)
    
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