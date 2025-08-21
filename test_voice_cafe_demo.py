#!/usr/bin/env python3
"""
Test script for the voice cafe kiosk demo
Tests function registration and basic functionality
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_demo_initialization():
    """Test that the demo script initializes properly"""
    print("🧪 Testing Voice Cafe Demo Initialization...")
    
    try:
        # Import and create agent
        sys.path.insert(0, os.path.dirname(__file__))
        
        # Mock the API key for testing
        os.environ['OPENAI_API_KEY'] = 'test_key_for_initialization'
        
        from voice_cafe_kiosk_demo import VoiceCafeKioskAgent
        
        # Test text mode initialization
        agent_text = VoiceCafeKioskAgent(voice_enabled=False)
        print(f"✅ Text mode agent initialized successfully")
        print(f"✅ {len(agent_text.functions)} functions registered")
        print(f"✅ {len(agent_text.function_schemas)} function schemas created")
        
        # Test voice mode initialization (will fall back to text if PyAudio not available)
        agent_voice = VoiceCafeKioskAgent(voice_enabled=True)
        if agent_voice.voice_enabled:
            print("✅ Voice mode agent initialized successfully")
            print("✅ Audio input/output configured")
        else:
            print("✅ Voice mode fell back to text (PyAudio not available)")
        
        agent = agent_text  # Use text agent for remaining tests
        
        # Test key functions are available
        key_functions = [
            'get_menu_by_category',
            'highlight_menu_item', 
            'add_item_to_order',
            'display_cart_view',
            'display_menu_categories'
        ]
        
        missing_functions = []
        for func in key_functions:
            if func not in agent.functions:
                missing_functions.append(func)
            else:
                print(f"✅ Key function available: {func}")
        
        if missing_functions:
            print(f"❌ Missing functions: {missing_functions}")
            return False
        
        # Test that subsystems are working
        await agent.kiosk_ui.display_welcome_screen()
        print("✅ Kiosk UI working")
        
        await agent.cafe_system.get_menu_by_category("coffee")
        print("✅ Cafe system working")
        
        await agent.robot.get_status()
        print("✅ Robot system working")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo initialization error: {e}")
        return False

def test_function_schemas():
    """Test that function schemas are properly formatted"""
    print("\n🧪 Testing Function Schemas...")
    
    try:
        os.environ['OPENAI_API_KEY'] = 'test_key_for_schemas'
        
        from voice_cafe_kiosk_demo import VoiceCafeKioskAgent
        
        agent = VoiceCafeKioskAgent()
        
        # Check schema format
        for schema in agent.function_schemas:
            # Required fields
            if 'type' not in schema:
                print(f"❌ Missing 'type' in schema: {schema.get('name', 'unknown')}")
                return False
            
            if 'name' not in schema:
                print(f"❌ Missing 'name' in schema")
                return False
                
            if 'parameters' not in schema:
                print(f"❌ Missing 'parameters' in schema: {schema['name']}")
                return False
                
            print(f"✅ Schema valid: {schema['name']}")
        
        print(f"✅ All {len(agent.function_schemas)} schemas are properly formatted")
        return True
        
    except Exception as e:
        print(f"❌ Schema testing error: {e}")
        return False

async def test_function_execution():
    """Test that functions can be executed"""
    print("\n🧪 Testing Function Execution...")
    
    try:
        os.environ['OPENAI_API_KEY'] = 'test_key_for_functions'
        
        from voice_cafe_kiosk_demo import VoiceCafeKioskAgent
        
        agent = VoiceCafeKioskAgent()
        
        # Test key functions
        test_cases = [
            ('display_menu_categories', {}),
            ('get_menu_by_category', {'category': 'coffee'}),
            ('highlight_menu_item', {'item_name': 'americano'}),
            ('start_new_order', {'customer_name': 'Test Customer'}),
            ('add_item_to_order', {'item_name': 'americano', 'quantity': 1}),
            ('display_cart_view', {}),
            ('set_led_color', {'color': 'blue'})
        ]
        
        for func_name, args in test_cases:
            if func_name in agent.functions:
                try:
                    result = await agent.functions[func_name](**args)
                    print(f"✅ Function executed: {func_name}")
                except Exception as e:
                    print(f"❌ Function execution failed: {func_name} - {e}")
                    return False
            else:
                print(f"⚠️  Function not registered: {func_name}")
        
        print("✅ All registered functions executed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Function execution testing error: {e}")
        return False

def print_usage_guide():
    """Print usage guide for the demo script"""
    print("\n📋 VOICE CAFE KIOSK DEMO USAGE GUIDE")
    print("=" * 60)
    
    print("\n🚀 TO RUN THE DEMO:")
    print("1. Set your OpenAI API key:")
    print("   export OPENAI_API_KEY=your_actual_api_key_here")
    print("2. Install PyAudio for voice mode (optional):")
    print("   pip install pyaudio")
    print("3. Run the demo script:")
    print("   python voice_cafe_kiosk_demo.py                # Auto mode")
    print("   python voice_cafe_kiosk_demo.py --mode voice   # Voice mode")
    print("   python voice_cafe_kiosk_demo.py --mode text    # Text mode")
    
    print("\n💬 EXAMPLE INTERACTIONS:")
    print("👤 'Show me the coffee menu'")
    print("   → AI displays coffee category and highlights items")
    print()
    print("👤 'Highlight the americano'") 
    print("   → Kiosk focuses on americano with details")
    print()
    print("👤 'I want a latte with oat milk'")
    print("   → AI adds latte to order and shows cart")
    print()
    print("👤 'Show my cart'")
    print("   → Displays current order on kiosk screen")
    print()
    print("👤 'Make the robot LED blue'")
    print("   → Changes robot LED color")
    
    print("\n🎯 KEY FEATURES:")
    print("• 🎤 Voice input with speech recognition (OpenAI Whisper)")
    print("• 🔊 Voice output with natural speech synthesis")
    print("• 🖥️  Voice-controlled kiosk display updates")
    print("• ⚡ Real-time voice interruption support")
    print("• 📋 Complete ordering workflow with visual feedback")
    print("• 🤖 Integration of robot controls with cafe operations")
    print("• 💬 Fallback text mode for development/testing")
    print("• 🎯 Auto-detection of audio capabilities")
    
    print("\n📝 SUPPORTED COMMANDS:")
    print("• Menu browsing: 'show menu', 'coffee menu', 'pastries'")
    print("• Item selection: 'highlight americano', 'show latte details'")
    print("• Ordering: 'I want X', 'add Y to order', 'order Z with customizations'")
    print("• Cart management: 'show cart', 'what's in my order'")
    print("• Payment: 'checkout', 'pay with card'")
    print("• Robot control: 'change LED to red', 'robot status'")

async def main():
    """Run all tests"""
    print("🤖 ☕ VOICE CAFE KIOSK DEMO - TESTING")
    print("=" * 60)
    
    all_tests_passed = True
    
    # Test initialization
    if not await test_demo_initialization():
        all_tests_passed = False
        print("❌ Cannot continue without proper initialization")
        return 1
    
    # Test schemas
    if not test_function_schemas():
        all_tests_passed = False
    
    # Test function execution  
    if not await test_function_execution():
        all_tests_passed = False
    
    if all_tests_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Voice Cafe Kiosk Demo is ready to use")
        print_usage_guide()
    else:
        print("\n❌ SOME TESTS FAILED")
        print("Please check the issues above")
        
    return 0 if all_tests_passed else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))