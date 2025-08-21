#!/usr/bin/env python3
"""
Unified Voice AI Agent Main Application
Consolidates cafe ordering and HRI in one system with voice/text input options
"""

import asyncio
import signal
import sys
import os
import argparse
from unified_voice_agent import UnifiedVoiceAgent
from hri_functions import RobotController, HRI_FUNCTION_SCHEMAS
from cafe_system import CafeKioskSystem, CAFE_FUNCTION_SCHEMAS
from kiosk_ui import KioskUIController, KIOSK_UI_FUNCTION_SCHEMAS

class UnifiedCafeRobotSystem:
    """Unified system combining cafe ordering and robot control"""
    
    def __init__(self, mode: str = "auto"):
        # Initialize subsystems
        self.cafe_system = CafeKioskSystem()
        self.robot = RobotController()
        self.kiosk_ui = KioskUIController(self.cafe_system)
        
        # Initialize voice agent
        audio_enabled = mode in ["auto", "voice"]
        self.agent = UnifiedVoiceAgent(audio_enabled=audio_enabled)
        
        self.mode = mode
        self.running = False
        
        # Conversation context for better interactions
        self.conversation_context = {
            "mode": "general",  # general, ordering, robot_control
            "last_interaction": None,
            "customer_preferences": {},
            "order_in_progress": False,
            "interaction_count": 0
        }
        
    def setup_functions(self):
        """Register all cafe and robot functions with the voice agent"""
        print("🔧 Setting up functions...")
        
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
            
        # Register kiosk UI functions
        for schema in KIOSK_UI_FUNCTION_SCHEMAS:
            func_name = schema["name"]
            func = getattr(self.kiosk_ui, func_name)
            self.agent.register_function(func_name, func, schema)
            
        # Register system management functions
        self.agent.register_function("get_system_status", self.get_system_status, {
            "name": "get_system_status",
            "description": "Get comprehensive system status including robot and cafe information",
            "parameters": {"type": "object", "properties": {}}
        })
        
        self.agent.register_function("switch_mode", self.switch_mode, {
            "name": "switch_mode",
            "description": "Switch conversation mode between general, ordering, or robot_control",
            "parameters": {
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "enum": ["general", "ordering", "robot_control"],
                        "description": "Mode to switch to"
                    }
                },
                "required": ["mode"]
            }
        })
        
        print(f"✅ Registered {len(CAFE_FUNCTION_SCHEMAS)} cafe functions")
        print(f"✅ Registered {len(HRI_FUNCTION_SCHEMAS)} robot functions")
        print(f"✅ Registered {len(KIOSK_UI_FUNCTION_SCHEMAS)} kiosk UI functions")
        print("✅ Registered 2 system management functions")
        
    async def get_system_status(self) -> str:
        """Get comprehensive system status"""
        status = {
            "robot": {
                "position": self.robot.position,
                "battery": f"{self.robot.battery_level}%",
                "moving": self.robot.is_moving,
                "led_color": self.robot.led_color
            },
            "cafe": {
                "menu_categories": 4,
                "total_menu_items": len(self.cafe_system.menu),
                "active_order": bool(self.cafe_system.current_order),
                "orders_completed": len(self.cafe_system.order_history)
            },
            "kiosk": {
                "current_screen": self.kiosk_ui.current_state.value,
                "highlighted_item": self.kiosk_ui.highlighted_index,
                "current_category": self.kiosk_ui.current_category or "none"
            },
            "conversation": {
                "mode": self.conversation_context["mode"],
                "interactions": self.conversation_context["interaction_count"],
                "order_in_progress": self.conversation_context["order_in_progress"]
            },
            "system": {
                "input_mode": "voice" if self.agent.audio_enabled else "text",
                "api_connected": bool(self.agent.ws)
            }
        }
        
        return f"🤖 **SYSTEM STATUS**\n\n" + \
               f"**Robot:** Position {status['robot']['position']}, Battery {status['robot']['battery']}\n" + \
               f"**Cafe:** {status['cafe']['total_menu_items']} menu items, {status['cafe']['orders_completed']} orders completed\n" + \
               f"**Kiosk:** {status['kiosk']['current_screen']} screen, item {status['kiosk']['highlighted_item']}\n" + \
               f"**Mode:** {status['conversation']['mode'].title()}, {status['conversation']['interactions']} interactions\n" + \
               f"**Input:** {status['system']['input_mode'].title()} mode"
        
    async def switch_mode(self, mode: str) -> str:
        """Switch conversation mode"""
        if mode not in ["general", "ordering", "robot_control"]:
            return "❌ Invalid mode. Available modes: general, ordering, robot_control"
            
        self.conversation_context["mode"] = mode
        self.conversation_context["interaction_count"] += 1
        
        mode_messages = {
            "general": "🔄 Switched to general mode. I can help with both cafe orders and robot control!",
            "ordering": "☕ Switched to ordering mode. Let me help you browse our menu and place an order!",
            "robot_control": "🤖 Switched to robot control mode. I'm ready to help with robot movements and functions!"
        }
        
        return mode_messages[mode]
        
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            print(f"\n🛑 Received signal {signum}")
            print("Shutting down unified system...")
            self.running = False
            exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    def print_welcome(self):
        """Print welcome message and system information"""
        print("🤖 ☕ UNIFIED VOICE AI AGENT")
        print("=" * 60)
        print("🎯 INTEGRATED FEATURES:")
        print("  • Voice/Text conversation with OpenAI Realtime API")
        print("  • Complete cafe ordering system (15+ menu items)")
        print("  • Robot movement and interaction control")
        print("  • Intelligent conversation context switching")
        print("  • Real-time status monitoring")
        print("=" * 60)
        
    def print_usage_examples(self):
        """Print example commands"""
        print("\n💡 EXAMPLE COMMANDS:")
        print("\n☕ CAFE ORDERING:")
        print("  • 'Hello, show me today's menu'")
        print("  • 'I'd like a latte with oat milk and extra shot'")
        print("  • 'What do you recommend for something cold?'")
        print("  • 'Add a blueberry muffin and check my total'")
        print("  • 'I'm ready to pay with card'")
        
        print("\n🤖 ROBOT CONTROL:")
        print("  • 'Move forward 3 meters then stop'")
        print("  • 'Turn left, set LED to blue, and take a photo'")
        print("  • 'What's your current status and battery level?'")
        print("  • 'Scan the environment and report what you see'")
        
        print("\n🖥️  KIOSK UI CONTROL:")
        print("  • 'Show the menu on the screen'")
        print("  • 'Highlight the americano on the display'")
        print("  • 'Display my cart contents'")
        print("  • 'Navigate to the coffee category'")
        print("  • 'Show checkout screen'")
        
        print("\n🔄 COMBINED INTERACTIONS:")
        print("  • 'Show me the coffee menu on screen and recommend something'")
        print("  • 'Highlight the latte while you move to prepare it'")
        print("  • 'Display my cart and then move to the pickup area'")
        print("  • 'Show welcome screen and patrol the cafe'")
        
    def check_environment(self):
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
        if self.mode in ["auto", "voice"]:
            try:
                import pyaudio
                print("✅ PyAudio available for voice input")
            except ImportError:
                print("⚠️  PyAudio not available - will use text mode")
                self.mode = "text"
        
        # Check other dependencies
        try:
            import websockets
            print("✅ WebSockets available")
        except ImportError:
            print("❌ WebSockets not available")
            return False
            
        return True
        
    async def start(self):
        """Start the unified system"""
        self.print_welcome()
        
        # Environment check
        if not self.check_environment():
            print("\n❌ Environment check failed. Please fix the issues above.")
            sys.exit(1)
            
        self.print_usage_examples()
        
        # Setup system
        self.setup_functions()
        self.setup_signal_handlers()
        
        print(f"\n🚀 Starting Unified Voice AI Agent...")
        print(f"🎤 Input mode: {self.mode.upper()}")
        print("💬 Say 'hello' or type 'show me the menu' to get started")
        print("\n" + "=" * 60)
        
        try:
            self.running = True
            await self.agent.run(mode=self.mode)
            
        except Exception as e:
            print(f"\n❌ Failed to start system: {e}")
            print("💡 Check your OpenAI API key and internet connection")
            sys.exit(1)
        finally:
            print("🧹 Cleaning up...")
            self.agent.cleanup()

def main():
    """Main function with command line argument parsing"""
    parser = argparse.ArgumentParser(
        description="Unified Voice AI Agent for Cafe Ordering and HRI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
MODES:
  auto    - Auto-detect voice/text based on audio availability (default)
  voice   - Voice input mode (requires PyAudio)
  text    - Text input mode (no audio dependencies)

EXAMPLES:
  python src/unified_main.py                # Auto mode
  python src/unified_main.py --mode voice   # Force voice mode
  python src/unified_main.py --mode text    # Force text mode
        """
    )
    
    parser.add_argument(
        "--mode", "-m",
        choices=["auto", "voice", "text"],
        default="auto",
        help="Input mode for the voice agent"
    )
    
    args = parser.parse_args()
    
    print("🤖 ☕ UNIFIED VOICE AI AGENT FOR CAFE & HRI")
    print("=" * 50)
    
    # Create and start the system
    system = UnifiedCafeRobotSystem(mode=args.mode)
    
    try:
        asyncio.run(system.start())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()