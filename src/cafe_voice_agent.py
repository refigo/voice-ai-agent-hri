"""
Enhanced Voice AI Agent with Cafe Kiosk Integration
Combines robot control with cafe ordering system
"""

import asyncio
import json
from voice_agent import VoiceAIAgent
from hri_functions import RobotController, HRI_FUNCTION_SCHEMAS
from cafe_system import CafeKioskSystem, CAFE_FUNCTION_SCHEMAS

class CafeVoiceAgent(VoiceAIAgent):
    def __init__(self):
        super().__init__()
        self.cafe_system = CafeKioskSystem()
        self.robot = RobotController()
        self.conversation_context = {
            "mode": "general",  # general, ordering, robot_control
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
            
        # Register conversation context functions
        self.register_function("set_conversation_mode", self.set_conversation_mode, {
            "name": "set_conversation_mode",
            "description": "Set the conversation mode (general, ordering, robot_control)",
            "parameters": {
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "enum": ["general", "ordering", "robot_control"],
                        "description": "Conversation mode to set"
                    }
                },
                "required": ["mode"]
            }
        })
        
        self.register_function("get_conversation_context", self.get_conversation_context, {
            "name": "get_conversation_context",
            "description": "Get current conversation context and mode",
            "parameters": {"type": "object", "properties": {}}
        })
        
        print(f"Registered {len(CAFE_FUNCTION_SCHEMAS)} cafe functions")
        print(f"Registered {len(HRI_FUNCTION_SCHEMAS)} robot functions")
        print("Registered 2 conversation context functions")
        
    async def set_conversation_mode(self, mode: str) -> str:
        """Set the conversation mode for better context handling"""
        valid_modes = ["general", "ordering", "robot_control"]
        
        if mode not in valid_modes:
            return f"Invalid mode. Valid modes: {', '.join(valid_modes)}"
            
        self.conversation_context["mode"] = mode
        self.conversation_context["last_interaction"] = asyncio.get_event_loop().time()
        
        if mode == "ordering":
            self.conversation_context["order_in_progress"] = True
            return "Switched to ordering mode. I can help you browse our menu and place an order."
        elif mode == "robot_control":
            return "Switched to robot control mode. I can help you control robot movements and functions."
        else:
            self.conversation_context["order_in_progress"] = False
            return "Switched to general mode. I can help with both cafe orders and robot control."
            
    async def get_conversation_context(self) -> str:
        """Get current conversation context"""
        context = self.conversation_context.copy()
        
        # Add order status
        if self.cafe_system.current_order:
            context["current_order_id"] = self.cafe_system.current_order.id
            context["current_order_total"] = self.cafe_system.current_order.total_amount
            context["current_order_items"] = len(self.cafe_system.current_order.items)
        else:
            context["current_order_id"] = None
            
        # Add robot status
        context["robot_position"] = self.robot.position
        context["robot_moving"] = self.robot.is_moving
        context["robot_battery"] = self.robot.battery_level
        
        return f"Context: {json.dumps(context, indent=2)}"
        
    async def send_session_update(self):
        """Enhanced session configuration with cafe context"""
        session_config = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": """You are an intelligent cafe service robot with voice interaction capabilities. 

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
                "voice": "alloy",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {
                    "model": "whisper-1"
                },
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 200
                },
                "tools": self.function_schemas
            }
        }
        
        await self.ws.send(json.dumps(session_config))
        
    async def handle_function_call(self, data):
        """Enhanced function call handling with context updates"""
        function_name = data.get("name")
        arguments = data.get("arguments", "{}")
        
        try:
            args = json.loads(arguments)
            if function_name in self.functions:
                result = await self.functions[function_name](**args)
                
                # Update conversation context based on function called
                self._update_context_from_function(function_name, args, result)
                
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
            error_response = {
                "type": "conversation.item.create",
                "item": {
                    "type": "function_call_output",
                    "call_id": data.get("call_id"),
                    "output": f"Error: {str(e)}"
                }
            }
            await self.ws.send(json.dumps(error_response))
            
    def _update_context_from_function(self, function_name: str, args: dict, result: str):
        """Update conversation context based on function calls"""
        current_time = asyncio.get_event_loop().time()
        self.conversation_context["last_interaction"] = current_time
        
        # Cafe-related functions
        if function_name in ["start_new_order", "add_item_to_order"]:
            self.conversation_context["mode"] = "ordering"
            self.conversation_context["order_in_progress"] = True
            
        elif function_name == "process_payment":
            self.conversation_context["order_in_progress"] = False
            
        elif function_name == "cancel_order":
            self.conversation_context["order_in_progress"] = False
            
        # Robot control functions
        elif function_name in ["move_forward", "move_backward", "turn_left", "turn_right"]:
            self.conversation_context["mode"] = "robot_control"
            
        # Track customer preferences
        if function_name == "get_recommendations" and "preference" in args:
            pref = args["preference"]
            if pref in self.conversation_context["customer_preferences"]:
                self.conversation_context["customer_preferences"][pref] += 1
            else:
                self.conversation_context["customer_preferences"][pref] = 1
                
        if function_name == "add_item_to_order" and "item_name" in args:
            item = args["item_name"]
            if "ordered_items" not in self.conversation_context:
                self.conversation_context["ordered_items"] = []
            self.conversation_context["ordered_items"].append(item)

class CafeServiceRobot:
    """Main class for the integrated cafe service robot"""
    
    def __init__(self):
        self.agent = CafeVoiceAgent()
        self.running = False
        
    async def start_service(self):
        """Start the cafe service robot"""
        print("🤖 ☕ Cafe Service Robot Starting...")
        print("=" * 40)
        
        # Setup all functions
        self.agent.setup_functions()
        
        # Initialize cafe system
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
            
    def get_system_status(self):
        """Get comprehensive system status"""
        status = {
            "robot": {
                "position": self.agent.robot.position,
                "battery": self.agent.robot.battery_level,
                "moving": self.agent.robot.is_moving
            },
            "cafe": {
                "menu_items": len(self.agent.cafe_system.menu),
                "active_order": bool(self.agent.cafe_system.current_order),
                "order_history": len(self.agent.cafe_system.order_history)
            },
            "conversation": self.agent.conversation_context
        }
        return status