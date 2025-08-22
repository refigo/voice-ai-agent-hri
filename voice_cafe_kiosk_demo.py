#!/usr/bin/env python3
"""
Simple Voice AI Robot Cafe Agent with Kiosk UI Control
Demonstrates voice-controlled cafe kiosk using OpenAI Realtime API
"""

import asyncio
import os
import sys
import json
import signal
from typing import Dict, List

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
load_dotenv()

class VoiceCafeKioskAgent:
    """Simple voice-controlled cafe agent with kiosk UI"""
    
    def __init__(self, voice_enabled: bool = True):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Voice/Audio settings
        self.voice_enabled = voice_enabled
        self.audio_in = None
        self.audio_out = None
        
        # Initialize audio if requested
        if self.voice_enabled:
            try:
                import pyaudio
                self._init_audio()
                print("🎤 Voice input enabled")
            except ImportError:
                print("⚠️  PyAudio not available, falling back to text mode")
                self.voice_enabled = False
        
        # Initialize subsystems
        from cafe_system import CafeKioskSystem
        from kiosk_ui import KioskUIController
        from hri_functions import RobotController
        
        self.cafe_system = CafeKioskSystem()
        self.kiosk_ui = KioskUIController(self.cafe_system)
        self.robot = RobotController()
        
        # WebSocket connection
        self.ws = None
        self.running = False
        
        # Voice interruption management
        self.is_speaking = False
        self.current_response_id = None
        
        # Function registry
        self.functions = {}
        self.function_schemas = []
        
        # Setup all functions
        self._setup_functions()
        
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
            
            print("🔊 Audio input/output initialized")
            
        except Exception as e:
            print(f"⚠️  Audio initialization failed: {e}")
            self.voice_enabled = False
        
    def _setup_functions(self):
        """Setup all available functions for the voice agent"""
        print("🔧 Setting up voice-controlled functions...")
        
        # Cafe ordering functions
        cafe_functions = [
            ('get_menu_by_category', 'Show menu items by category'),
            ('start_new_order', 'Start a new customer order'),
            ('add_item_to_order', 'Add item to current order'),
            ('view_current_order', 'View current order details'),
            ('process_payment', 'Process order payment'),
            ('get_recommendations', 'Get menu recommendations'),
        ]
        
        for func_name, desc in cafe_functions:
            if hasattr(self.cafe_system, func_name):
                func = getattr(self.cafe_system, func_name)
                self.functions[func_name] = func
                print(f"✅ Registered cafe function: {func_name}")
        
        # Kiosk UI functions
        kiosk_functions = [
            ('display_welcome_screen', 'Display kiosk welcome screen'),
            ('display_menu_categories', 'Show menu categories on kiosk'),
            ('display_menu_items', 'Show menu items for category'),
            ('highlight_menu_item', 'Highlight specific menu item'),
            ('display_item_details', 'Show item details on kiosk'),
            ('display_cart_view', 'Display cart contents on kiosk'),
            ('display_checkout_screen', 'Show payment screen'),
        ]
        
        for func_name, desc in kiosk_functions:
            if hasattr(self.kiosk_ui, func_name):
                func = getattr(self.kiosk_ui, func_name)
                self.functions[func_name] = func
                print(f"✅ Registered kiosk function: {func_name}")
        
        # Robot control functions (essential ones)
        robot_functions = [
            ('move_forward', 'Move robot forward'),
            ('get_status', 'Get robot status'),
            ('set_led_color', 'Control LED colors'),
        ]
        
        for func_name, desc in robot_functions:
            if hasattr(self.robot, func_name):
                func = getattr(self.robot, func_name)
                self.functions[func_name] = func
                print(f"✅ Registered robot function: {func_name}")
        
        # Build function schemas for OpenAI
        self._build_function_schemas()
        
        print(f"🎯 Total functions registered: {len(self.functions)}")
        
    def _build_function_schemas(self):
        """Build OpenAI function schemas"""
        # Core cafe functions with simplified schemas
        self.function_schemas = [
            {
                "type": "function",
                "name": "get_menu_by_category",
                "description": "Show menu items by category on kiosk display",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": ["all", "coffee", "cold_drinks", "pastries", "sandwiches"],
                            "description": "Menu category to display"
                        }
                    }
                }
            },
            {
                "type": "function",
                "name": "display_menu_categories",
                "description": "Show all menu categories on the kiosk screen",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "type": "function",
                "name": "highlight_menu_item",
                "description": "Highlight a specific menu item on the kiosk display",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "item_name": {
                            "type": "string",
                            "description": "Name of menu item to highlight (e.g. americano, latte, cappuccino)"
                        }
                    },
                    "required": ["item_name"]
                }
            },
            {
                "type": "function",
                "name": "display_item_details",
                "description": "Show detailed information about a menu item on kiosk",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "item_name": {
                            "type": "string", 
                            "description": "Name of menu item to show details for"
                        }
                    },
                    "required": ["item_name"]
                }
            },
            {
                "type": "function",
                "name": "add_item_to_order",
                "description": "Add a menu item to the customer's order",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "item_name": {
                            "type": "string",
                            "description": "Name of the menu item"
                        },
                        "quantity": {
                            "type": "integer",
                            "description": "Number of items (default: 1)"
                        },
                        "customizations": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Customizations like extra_shot, oat_milk, decaf"
                        }
                    },
                    "required": ["item_name"]
                }
            },
            {
                "type": "function",
                "name": "display_cart_view",
                "description": "Show the customer's current order on kiosk screen",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "type": "function",
                "name": "display_checkout_screen",
                "description": "Display payment options and checkout on kiosk",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "type": "function",
                "name": "start_new_order",
                "description": "Start a new order for a customer",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_name": {
                            "type": "string",
                            "description": "Customer name (optional)"
                        }
                    }
                }
            },
            {
                "type": "function",
                "name": "process_payment",
                "description": "Process payment for the order",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "payment_method": {
                            "type": "string",
                            "enum": ["card", "cash", "mobile"],
                            "description": "Payment method"
                        }
                    }
                }
            },
            {
                "type": "function",
                "name": "set_led_color",
                "description": "Change robot LED color",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "color": {
                            "type": "string",
                            "description": "LED color (red, blue, green, yellow, white)"
                        }
                    },
                    "required": ["color"]
                }
            }
        ]
    
    async def connect_to_openai(self):
        """Connect to OpenAI Realtime API"""
        try:
            import websockets
            
            uri = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "OpenAI-Beta": "realtime=v1"
            }
            
            header_list = [(key, value) for key, value in headers.items()]
            self.ws = await websockets.connect(uri, additional_headers=header_list)
            
            print("✅ Connected to OpenAI Realtime API")
            await self.send_session_config()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to OpenAI: {e}")
            return False
    
    async def send_session_config(self):
        """Configure the session with our functions"""
        # Determine modalities based on voice capability
        modalities = ["text", "audio"] if self.voice_enabled else ["text"]
        
        # Build session config
        session_data = {
            "modalities": modalities,
            "instructions": """You are a helpful cafe service robot that controls both ordering and a visual kiosk display.

CAPABILITIES:
- Take cafe orders (coffee, pastries, sandwiches, cold drinks)
- Control kiosk display (show menus, highlight items, display cart)  
- Basic robot functions (LED control, status)

GUIDELINES:
- Always greet customers warmly
- Use kiosk display functions to show visual information
- When customer mentions a menu item, highlight it on screen
- Show cart after adding items
- Guide customers through the ordering process
- Be helpful with recommendations
- You can talk about small talk topics

EXAMPLE INTERACTIONS:
Customer: "Show me the coffee menu"
→ Use display_menu_categories then get_menu_by_category with "coffee"

Customer: "I want an americano"
→ Use highlight_menu_item with "americano", then add_item_to_order

Customer: "What's in my order?"
→ Use display_cart_view to show their cart on screen

Always use the appropriate kiosk display functions to enhance the visual experience!""",
            "tools": self.function_schemas
        }
        
        # Add voice-specific settings if enabled
        if self.voice_enabled:
            session_data.update({
                "voice": "alloy",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {"model": "whisper-1"},
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.1,
                    "prefix_padding_ms": 200,
                    "silence_duration_ms": 150
                }
            })
        
        session_config = {
            "type": "session.update",
            "session": session_data
        }
        
        await self.ws.send(json.dumps(session_config))
        print("🎯 Session configured with cafe and kiosk functions")
    
    async def handle_function_call(self, function_call):
        """Execute function calls from the AI"""
        func_name = function_call.get("name")
        call_id = function_call.get("call_id")
        arguments = function_call.get("arguments", "{}")
        
        try:
            # Parse arguments
            if isinstance(arguments, str):
                args = json.loads(arguments) if arguments else {}
            else:
                args = arguments
            
            print(f"\n🔧 AI called: {func_name}({args})")
            
            # Execute function
            if func_name in self.functions:
                result = await self.functions[func_name](**args)
                print(f"📋 Function result: {result[:100]}{'...' if len(str(result)) > 100 else ''}")
                
                # Send result back to AI
                response = {
                    "type": "conversation.item.create",
                    "item": {
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": str(result)
                    }
                }
                await self.ws.send(json.dumps(response))
                
            else:
                error_msg = f"Function {func_name} not found"
                print(f"❌ {error_msg}")
                
                error_response = {
                    "type": "conversation.item.create", 
                    "item": {
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": f"Error: {error_msg}"
                    }
                }
                await self.ws.send(json.dumps(error_response))
                
        except Exception as e:
            error_msg = f"Function execution error: {e}"
            print(f"❌ {error_msg}")
            
            error_response = {
                "type": "conversation.item.create",
                "item": {
                    "type": "function_call_output", 
                    "call_id": call_id,
                    "output": error_msg
                }
            }
            await self.ws.send(json.dumps(error_response))
    
    async def handle_function_call_complete(self, data: dict):
        """Handle completed function call with arguments"""
        func_name = data.get("name")
        call_id = data.get("call_id")
        arguments = data.get("arguments", "{}")
        
        try:
            # Parse arguments
            if isinstance(arguments, str):
                args = json.loads(arguments) if arguments else {}
            else:
                args = arguments
            
            print(f"\n🔧 AI called: {func_name}({args})")
            
            # Execute function
            if func_name in self.functions:
                result = await self.functions[func_name](**args)
                print(f"📋 Function result: {result[:100]}{'...' if len(str(result)) > 100 else ''}")
                
                # Send result back to AI
                response = {
                    "type": "conversation.item.create",
                    "item": {
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": str(result)
                    }
                }
                await self.ws.send(json.dumps(response))
                
            else:
                error_msg = f"Function {func_name} not found"
                print(f"❌ {error_msg}")
                
                error_response = {
                    "type": "conversation.item.create", 
                    "item": {
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": f"Error: {error_msg}"
                    }
                }
                await self.ws.send(json.dumps(error_response))
                
        except Exception as e:
            error_msg = f"Function execution error: {e}"
            print(f"❌ {error_msg}")
            
            error_response = {
                "type": "conversation.item.create",
                "item": {
                    "type": "function_call_output", 
                    "call_id": call_id,
                    "output": error_msg
                }
            }
            await self.ws.send(json.dumps(error_response))
    
    async def send_user_message(self, text: str):
        """Send user message to AI"""
        message = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user", 
                "content": [{"input_type": "text", "text": text}]
            }
        }
        await self.ws.send(json.dumps(message))
        
        # Trigger AI response
        response_trigger = {"type": "response.create"}
        await self.ws.send(json.dumps(response_trigger))
    
    async def send_audio_data(self, audio_data: bytes):
        """Send audio data to the API"""
        if self.ws and self.voice_enabled:
            import base64
            audio_message = {
                "type": "input_audio_buffer.append",
                "audio": base64.b64encode(audio_data).decode()
            }
            await self.ws.send(json.dumps(audio_message))
    
    async def handle_messages(self):
        """Handle incoming messages from OpenAI"""
        async for message in self.ws:
            try:
                data = json.loads(message)
                # print(data)
                msg_type = data.get("type")
                print(f"msg_type: {msg_type}")
                
                if msg_type == "response.created":
                    # Track current response for interruption handling
                    self.current_response_id = data.get("response", {}).get("id")
                    self.is_speaking = True
                
                elif msg_type == "response.text.delta":
                    # Print AI response
                    text = data.get("delta", "")
                    print(text, end="", flush=True)
                    
                elif msg_type == "response.audio.delta":
                    # Play AI audio response
                    if self.voice_enabled and self.audio_out:
                        audio_data = data.get("delta", "")
                        if audio_data:
                            import base64
                            audio_bytes = base64.b64decode(audio_data)
                            try:
                                self.audio_out.write(audio_bytes)
                            except Exception as e:
                                # Audio output might be interrupted
                                pass
                    
                elif msg_type == "response.function_call_delta":
                    # Handle function calls
                    print("\n🔧 AI called: ", data.get("delta"))
                    if data.get("delta"):
                        await self.handle_function_call(data.get("delta"))
                        
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
                    print()  # New line after AI response
                    
                elif msg_type == "input_audio_buffer.speech_started":
                    print("🎤 You're speaking...")
                    
                elif msg_type == "input_audio_buffer.speech_stopped":
                    print("🔇 Processing your message...")
                    
                elif msg_type == "conversation.item.created":
                    # Show transcription of user speech
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
                        
                elif msg_type == "input_audio_buffer.committed":
                    # Buffer committed, response will be created
                    pass
                    
                elif msg_type == "error":
                    print(f"\n❌ API Error: {data}")
                    
            except Exception as e:
                print(f"\n❌ Message handling error: {e}")
    
    async def audio_input_loop(self):
        """Capture and send audio input"""
        if not self.voice_enabled or not self.audio_in:
            return
            
        print("🎤 Audio input active - speak normally")
        
        while self.running:
            try:
                # Read audio data
                audio_data = self.audio_in.read(1024, exception_on_overflow=False)
                await self.send_audio_data(audio_data)
                await asyncio.sleep(0.01)  # Small delay
                
            except Exception as e:
                print(f"❌ Audio input error: {e}")
                break
    
    async def text_input_loop(self):
        """Text-based interaction loop"""
        while self.running:
            try:
                # Get user input
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, input, "\n👤 You (text): "
                )
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\n👋 Thanks for visiting our cafe!")
                    break
                    
                # Send to AI
                await self.send_user_message(user_input)
                print("🤖 Cafe Agent: ", end="", flush=True)
                
            except KeyboardInterrupt:
                print("\n👋 Session ended by user")
                break
            except Exception as e:
                print(f"❌ Text input error: {e}")
                break
    
    async def run_interactive_session(self):
        """Run interactive voice cafe session"""
        print("\n🤖 ☕ VOICE CAFE AGENT WITH KIOSK CONTROL")
        print("=" * 60)
        
        # Display input mode information
        if self.voice_enabled:
            print("🎤 VOICE MODE ACTIVE - Speak naturally!")
            print("⚡ Voice interruption enabled - interrupt the AI anytime")
            print("🖥️  Watch the kiosk display update in real-time!")
            print("✨ Try voice commands like:")
            print("   • 'Show me the coffee menu'")
            print("   • 'Highlight the americano'") 
            print("   • 'I want a latte with oat milk'")
            print("   • 'Show my cart'")
        else:
            print("💬 TEXT MODE ACTIVE - Type your messages")
            print("🖥️  Watch the kiosk display update in real-time!")
            print("✨ Try text commands like:")
            print("   • 'Show me the coffee menu'")
            print("   • 'Highlight the americano'") 
            print("   • 'I want a latte with oat milk'")
            print("   • 'Show my cart'")
            
        print("=" * 60)
        
        # Start with welcome screen
        await self.kiosk_ui.display_welcome_screen()
        
        # Start message handler
        message_task = asyncio.create_task(self.handle_messages())
        
        self.running = True
        
        try:
            if self.voice_enabled:
                # Voice mode - start audio input loop
                print("🎤 Speak now - the AI will respond with voice and text")
                audio_task = asyncio.create_task(self.audio_input_loop())
                await audio_task
            else:
                # Text mode - start text input loop
                await self.text_input_loop()
                
        except KeyboardInterrupt:
            print("\n\n👋 Session ended by user")
        finally:
            self.running = False
            message_task.cancel()
            
            if self.ws:
                await self.ws.close()
    
    def cleanup(self):
        """Clean up audio resources"""
        self.running = False
        
        if self.voice_enabled and hasattr(self, 'pa'):
            if self.audio_in:
                self.audio_in.stop_stream()
                self.audio_in.close()
            if self.audio_out:
                self.audio_out.stop_stream()
                self.audio_out.close()
            self.pa.terminate()

def setup_signal_handlers(agent):
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum} - shutting down...")
        agent.running = False
        exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Voice AI Cafe Agent with Kiosk Control",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
MODES:
  voice   - Voice input mode with audio I/O (requires PyAudio)
  text    - Text input mode (no audio dependencies)
  auto    - Auto-detect based on PyAudio availability (default)

EXAMPLES:
  python voice_cafe_kiosk_demo.py                # Auto mode
  python voice_cafe_kiosk_demo.py --mode voice   # Force voice mode
  python voice_cafe_kiosk_demo.py --mode text    # Force text mode
        """
    )
    
    parser.add_argument(
        "--mode", "-m",
        choices=["auto", "voice", "text"],
        default="auto",
        help="Input mode for the agent"
    )
    
    args = parser.parse_args()
    
    try:
        # Check environment
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ OPENAI_API_KEY not found in environment variables")
            print("Please set your OpenAI API key:")
            print("export OPENAI_API_KEY=your_key_here")
            return 1
        
        # Determine voice mode
        voice_enabled = True
        if args.mode == "text":
            voice_enabled = False
        elif args.mode == "auto":
            try:
                import pyaudio
                voice_enabled = True
                print("✅ PyAudio detected - voice mode available")
            except ImportError:
                voice_enabled = False
                print("⚠️  PyAudio not available - using text mode")
        
        # Create agent
        print(f"🚀 Starting Cafe Agent in {('VOICE' if voice_enabled else 'TEXT')} mode...")
        agent = VoiceCafeKioskAgent(voice_enabled=voice_enabled)
        
        # Setup signal handlers
        setup_signal_handlers(agent)
        
        # Connect to OpenAI
        if not await agent.connect_to_openai():
            return 1
        
        # Run interactive session
        try:
            await agent.run_interactive_session()
        finally:
            agent.cleanup()
        
        return 0
        
    except Exception as e:
        print(f"❌ Startup error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))