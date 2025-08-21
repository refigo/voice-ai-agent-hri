#!/usr/bin/env python3
"""
Test script for kiosk UI manipulation functions
Demonstrates visual menu display and interaction capabilities
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_kiosk_ui_components():
    """Test kiosk UI components and functionality"""
    print("🧪 Testing Kiosk UI Components...")
    
    try:
        from cafe_system import CafeKioskSystem
        from kiosk_ui import KioskUIController, KIOSK_UI_FUNCTION_SCHEMAS
        
        # Initialize systems
        cafe_system = CafeKioskSystem()
        kiosk_ui = KioskUIController(cafe_system)
        
        print("✅ Kiosk UI components initialized successfully")
        print(f"✅ {len(KIOSK_UI_FUNCTION_SCHEMAS)} kiosk UI functions available")
        
        return kiosk_ui, True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return None, False
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return None, False

async def test_ui_display_functions(kiosk_ui):
    """Test all UI display functions"""
    print("\n🧪 Testing UI Display Functions...")
    
    try:
        # Test welcome screen
        result = await kiosk_ui.display_welcome_screen()
        print(f"✅ Welcome screen: {result}")
        await asyncio.sleep(1)
        
        # Test menu categories
        result = await kiosk_ui.display_menu_categories()
        print(f"✅ Menu categories: {result}")
        await asyncio.sleep(1)
        
        # Test menu items display
        result = await kiosk_ui.display_menu_items("coffee")
        print(f"✅ Coffee menu: {result}")
        await asyncio.sleep(1)
        
        # Test item highlighting
        result = await kiosk_ui.highlight_menu_item("latte")
        print(f"✅ Item highlighting: {result}")
        await asyncio.sleep(1)
        
        # Test item details
        result = await kiosk_ui.display_item_details("americano")
        print(f"✅ Item details: {result}")
        await asyncio.sleep(1)
        
        # Test cart view
        result = await kiosk_ui.display_cart_view()
        print(f"✅ Cart view: {result}")
        await asyncio.sleep(1)
        
        return True
        
    except Exception as e:
        print(f"❌ Display function error: {e}")
        return False

async def test_navigation_functions(kiosk_ui):
    """Test navigation and interaction functions"""
    print("\n🧪 Testing Navigation Functions...")
    
    try:
        # Start with menu categories
        await kiosk_ui.display_menu_categories()
        
        # Test navigation
        result = await kiosk_ui.navigate_down()
        print(f"✅ Navigate down: {result}")
        
        result = await kiosk_ui.navigate_up()
        print(f"✅ Navigate up: {result}")
        
        # Test selection
        result = await kiosk_ui.select_highlighted_item()
        print(f"✅ Select item: {result}")
        
        # Test back navigation
        result = await kiosk_ui.go_back()
        print(f"✅ Go back: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Navigation function error: {e}")
        return False

async def test_integration_with_cafe_system(kiosk_ui):
    """Test integration with cafe ordering system"""
    print("\n🧪 Testing Cafe System Integration...")
    
    try:
        # Start an order
        await kiosk_ui.cafe_system.start_new_order("Test Customer")
        
        # Add items to order
        await kiosk_ui.cafe_system.add_item_to_order("latte", 1, ["oat_milk"])
        await kiosk_ui.cafe_system.add_item_to_order("croissant", 1)
        
        # Display cart with items
        result = await kiosk_ui.display_cart_view()
        print(f"✅ Cart with items: {result}")
        
        # Test checkout screen
        result = await kiosk_ui.display_checkout_screen()
        print(f"✅ Checkout screen: {result}")
        
        # Simulate payment and confirmation
        await kiosk_ui.cafe_system.process_payment("card")
        
        # Get order ID from history
        if kiosk_ui.cafe_system.order_history:
            order_id = kiosk_ui.cafe_system.order_history[-1].id
            result = await kiosk_ui.display_order_confirmation(order_id)
            print(f"✅ Order confirmation: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration error: {e}")
        return False

async def test_function_schemas():
    """Test function schemas for voice agent integration"""
    print("\n🧪 Testing Function Schemas...")
    
    try:
        from kiosk_ui import KIOSK_UI_FUNCTION_SCHEMAS
        
        required_functions = [
            "display_welcome_screen",
            "display_menu_categories", 
            "display_menu_items",
            "highlight_menu_item",
            "display_item_details",
            "display_cart_view",
            "display_checkout_screen",
            "navigate_up",
            "navigate_down",
            "select_highlighted_item",
            "go_back"
        ]
        
        schema_names = [schema["name"] for schema in KIOSK_UI_FUNCTION_SCHEMAS]
        
        for func_name in required_functions:
            if func_name in schema_names:
                print(f"✅ Function schema: {func_name}")
            else:
                print(f"❌ Missing schema: {func_name}")
                return False
                
        print(f"✅ All {len(KIOSK_UI_FUNCTION_SCHEMAS)} function schemas validated")
        return True
        
    except Exception as e:
        print(f"❌ Schema validation error: {e}")
        return False

def test_unified_system_integration():
    """Test integration with unified system"""
    print("\n🧪 Testing Unified System Integration...")
    
    try:
        from unified_main import UnifiedCafeRobotSystem
        
        # Test system initialization
        system = UnifiedCafeRobotSystem(mode="text")
        
        # Verify kiosk UI is integrated
        assert hasattr(system, 'kiosk_ui'), "Kiosk UI not integrated"
        assert system.kiosk_ui is not None, "Kiosk UI not initialized"
        
        print("✅ Kiosk UI integrated in unified system")
        
        # Test function registration
        system.setup_functions()
        
        # Check if kiosk functions are registered
        kiosk_function_names = [schema["name"] for schema in system.agent.function_schemas 
                              if any(kiosk_name in schema["name"] for kiosk_name in 
                                   ["display", "navigate", "highlight", "cart", "checkout"])]
        
        print(f"✅ {len(kiosk_function_names)} kiosk functions registered with voice agent")
        
        return True
        
    except Exception as e:
        print(f"❌ Unified system integration error: {e}")
        return False

async def demonstrate_kiosk_workflow():
    """Demonstrate complete kiosk workflow"""
    print("\n🎬 DEMONSTRATING COMPLETE KIOSK WORKFLOW")
    print("=" * 60)
    
    try:
        from cafe_system import CafeKioskSystem
        from kiosk_ui import KioskUIController
        
        cafe_system = CafeKioskSystem()
        kiosk_ui = KioskUIController(cafe_system)
        
        print("🎯 Workflow: Customer ordering an Americano")
        print("\n1️⃣  Show welcome screen...")
        await kiosk_ui.display_welcome_screen()
        await asyncio.sleep(2)
        
        print("\n2️⃣  Display menu categories...")
        await kiosk_ui.display_menu_categories()
        await asyncio.sleep(2)
        
        print("\n3️⃣  Select coffee category...")
        kiosk_ui.highlighted_index = 0  # Coffee category
        await kiosk_ui.select_highlighted_item()
        await asyncio.sleep(2)
        
        print("\n4️⃣  Highlight Americano...")
        await kiosk_ui.highlight_menu_item("americano")
        await asyncio.sleep(2)
        
        print("\n5️⃣  Show Americano details...")
        await kiosk_ui.display_item_details("americano")
        await asyncio.sleep(2)
        
        print("\n6️⃣  Add to order and show cart...")
        await cafe_system.start_new_order("Demo Customer")
        await cafe_system.add_item_to_order("americano", 1)
        await kiosk_ui.display_cart_view()
        await asyncio.sleep(2)
        
        print("\n7️⃣  Show checkout screen...")
        await kiosk_ui.display_checkout_screen()
        await asyncio.sleep(2)
        
        print("\n8️⃣  Process payment and confirm...")
        await cafe_system.process_payment("card")
        if cafe_system.order_history:
            order_id = cafe_system.order_history[-1].id
            await kiosk_ui.display_order_confirmation(order_id)
        
        print("\n🎉 Complete workflow demonstrated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Workflow demonstration error: {e}")
        return False

def print_usage_guide():
    """Print usage guide for kiosk UI functions"""
    print("\n📋 KIOSK UI USAGE GUIDE")
    print("=" * 50)
    
    print("\n🎯 VOICE COMMANDS FOR KIOSK CONTROL:")
    print("• 'Show welcome screen' - Display main welcome")
    print("• 'Show menu categories' - Display category selection")
    print("• 'Show coffee menu' - Display coffee items")
    print("• 'Highlight americano' - Highlight specific item")
    print("• 'Show item details for latte' - Item detail view")
    print("• 'Display my cart' - Show cart contents")
    print("• 'Show checkout screen' - Payment options")
    print("• 'Navigate up/down' - Move through lists")
    print("• 'Go back' - Return to previous screen")
    
    print("\n🖥️  KIOSK DISPLAY FEATURES:")
    print("• Visual menu layouts with highlighting")
    print("• Category-based navigation")
    print("• Item details with customization options")
    print("• Cart management with totals")
    print("• Checkout and payment interface")
    print("• Order confirmation displays")
    
    print("\n🔄 INTEGRATION BENEFITS:")
    print("• Voice commands control visual display")
    print("• Visual feedback enhances conversation")
    print("• Seamless ordering workflow")
    print("• Accessible interface design")
    print("• Real-time UI state management")

async def main():
    """Run all kiosk UI tests"""
    print("🖥️  ☕ KIOSK UI TESTING SUITE")
    print("=" * 60)
    
    all_tests_passed = True
    
    # Test component initialization
    kiosk_ui, init_success = await test_kiosk_ui_components()
    if not init_success:
        all_tests_passed = False
        print("\n❌ Cannot continue without kiosk UI components")
        return 1
    
    # Test display functions
    if not await test_ui_display_functions(kiosk_ui):
        all_tests_passed = False
    
    # Test navigation
    if not await test_navigation_functions(kiosk_ui):
        all_tests_passed = False
    
    # Test cafe system integration
    if not await test_integration_with_cafe_system(kiosk_ui):
        all_tests_passed = False
    
    # Test function schemas
    if not await test_function_schemas():
        all_tests_passed = False
    
    # Test unified system integration
    if not test_unified_system_integration():
        all_tests_passed = False
    
    # Demonstrate complete workflow
    if not await demonstrate_kiosk_workflow():
        all_tests_passed = False
    
    if all_tests_passed:
        print("\n🎉 ALL KIOSK UI TESTS PASSED!")
        print_usage_guide()
        
        print("\n🚀 TO USE KIOSK UI WITH VOICE AGENT:")
        print("1. Set OPENAI_API_KEY in .env file")
        print("2. Run: python src/unified_main.py")
        print("3. Say commands like 'show me the coffee menu'")
        print("4. Watch the kiosk display update in real-time")
        
    else:
        print("\n❌ SOME KIOSK UI TESTS FAILED")
        
    return 0 if all_tests_passed else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))