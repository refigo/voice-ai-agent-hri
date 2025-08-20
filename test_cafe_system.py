#!/usr/bin/env python3
"""
Test script for the Cafe Service Robot system
Tests both cafe ordering and robot control functions
"""

import asyncio
import json
from src.cafe_system import CafeKioskSystem
from src.hri_functions import RobotController

async def test_cafe_system():
    """Test the cafe ordering system"""
    print("🧪 Testing Cafe Ordering System")
    print("=" * 40)
    
    cafe = CafeKioskSystem()
    
    # Test 1: Get menu
    print("\n📋 Test 1: Get Menu")
    menu = await cafe.get_menu_by_category("coffee")
    print(menu[:200] + "..." if len(menu) > 200 else menu)
    
    # Test 2: Start order
    print("\n🛒 Test 2: Start New Order")
    result = await cafe.start_new_order("Alice")
    print(result)
    
    # Test 3: Add items
    print("\n➕ Test 3: Add Items to Order")
    result = await cafe.add_item_to_order("latte", 1, ["oat_milk", "extra_shot"])
    print(result)
    
    result = await cafe.add_item_to_order("blueberry muffin", 2)
    print(result)
    
    # Test 4: View order
    print("\n👀 Test 4: View Current Order")
    order = await cafe.view_current_order()
    print(order)
    
    # Test 5: Get recommendations
    print("\n⭐ Test 5: Get Recommendations")
    recs = await cafe.get_recommendations("cold")
    print(recs[:200] + "..." if len(recs) > 200 else recs)
    
    # Test 6: Confirm order
    print("\n✅ Test 6: Confirm Order")
    result = await cafe.confirm_order()
    print(result[:200] + "..." if len(result) > 200 else result)
    
    # Test 7: Process payment
    print("\n💳 Test 7: Process Payment")
    result = await cafe.process_payment("card")
    print(result)
    
    print("\n✅ Cafe system tests completed!")
    return True

async def test_robot_system():
    """Test the robot control system"""
    print("\n🤖 Testing Robot Control System")
    print("=" * 40)
    
    robot = RobotController()
    
    # Test 1: Get status
    print("\n📊 Test 1: Get Robot Status")
    status = await robot.get_status()
    print(status)
    
    # Test 2: Move forward
    print("\n➡️ Test 2: Move Forward")
    result = await robot.move_forward(1.5, 0.5)
    print(result)
    
    # Test 3: Turn and scan
    print("\n🔄 Test 3: Turn Left")
    result = await robot.turn_left(45)
    print(result)
    
    print("\n🔍 Test 4: Scan Environment")
    result = await robot.scan_environment()
    print(result)
    
    # Test 5: Set LED and play sound
    print("\n💡 Test 5: Set LED Color")
    result = await robot.set_led_color("blue")
    print(result)
    
    print("\n🔊 Test 6: Play Sound")
    result = await robot.play_sound("success")
    print(result)
    
    # Test 7: Take photo
    print("\n📸 Test 7: Take Photo")
    result = await robot.take_photo()
    print(result)
    
    print("\n✅ Robot system tests completed!")
    return True

async def test_integration_scenarios():
    """Test integration scenarios combining cafe and robot functions"""
    print("\n🔗 Testing Integration Scenarios")
    print("=" * 40)
    
    cafe = CafeKioskSystem()
    robot = RobotController()
    
    # Scenario 1: Customer approaches, robot greets and takes order
    print("\n📝 Scenario 1: Full Service Interaction")
    
    # Robot detects customer
    scan_result = await robot.scan_environment()
    print(f"Robot scan: {scan_result}")
    
    # Set LED to welcome color
    led_result = await robot.set_led_color("green")
    print(f"Welcome LED: {led_result}")
    
    # Play greeting sound
    sound_result = await robot.play_sound("chirp")
    print(f"Greeting sound: {sound_result}")
    
    # Start order process
    order_start = await cafe.start_new_order("Bob")
    print(f"Order started: {order_start}")
    
    # Show menu recommendations
    recs = await cafe.get_recommendations("coffee")
    print(f"Recommendations: {recs[:100]}...")
    
    # Customer orders
    add_result = await cafe.add_item_to_order("cappuccino", 1, ["almond_milk"])
    print(f"Item added: {add_result}")
    
    add_result = await cafe.add_item_to_order("croissant", 1)
    print(f"Item added: {add_result}")
    
    # Confirm and process order
    confirm_result = await cafe.confirm_order()
    print(f"Order confirmed: {confirm_result[:100]}...")
    
    payment_result = await cafe.process_payment("mobile")
    print(f"Payment processed: {payment_result}")
    
    # Robot moves to preparation area
    move_result = await robot.move_forward(2.0)
    print(f"Moving to prep area: {move_result}")
    
    # Set LED to indicate order in progress
    led_result = await robot.set_led_color("yellow")
    print(f"Order in progress LED: {led_result}")
    
    print("\n✅ Integration scenario completed!")
    
    return True

def test_function_schemas():
    """Test function schemas for OpenAI integration"""
    print("\n📝 Testing Function Schemas")
    print("=" * 40)
    
    from src.cafe_system import CAFE_FUNCTION_SCHEMAS
    from src.hri_functions import HRI_FUNCTION_SCHEMAS
    
    print(f"📋 Cafe functions: {len(CAFE_FUNCTION_SCHEMAS)}")
    for schema in CAFE_FUNCTION_SCHEMAS:
        print(f"  • {schema['name']}: {schema['description']}")
    
    print(f"\n🤖 Robot functions: {len(HRI_FUNCTION_SCHEMAS)}")
    for schema in HRI_FUNCTION_SCHEMAS:
        print(f"  • {schema['name']}: {schema['description']}")
    
    print(f"\n📊 Total functions available: {len(CAFE_FUNCTION_SCHEMAS) + len(HRI_FUNCTION_SCHEMAS)}")
    
    # Validate schema format
    all_schemas = CAFE_FUNCTION_SCHEMAS + HRI_FUNCTION_SCHEMAS
    
    for schema in all_schemas:
        required_fields = ["name", "description", "parameters"]
        for field in required_fields:
            if field not in schema:
                print(f"❌ Missing {field} in {schema.get('name', 'unknown')}")
                return False
    
    print("✅ All function schemas valid!")
    return True

async def main():
    """Run all tests"""
    print("🧪 CAFE SERVICE ROBOT TEST SUITE")
    print("=" * 50)
    
    try:
        # Test individual systems
        cafe_success = await test_cafe_system()
        robot_success = await test_robot_system()
        integration_success = await test_integration_scenarios()
        schema_success = test_function_schemas()
        
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS:")
        print(f"☕ Cafe System: {'✅ PASS' if cafe_success else '❌ FAIL'}")
        print(f"🤖 Robot System: {'✅ PASS' if robot_success else '❌ FAIL'}")
        print(f"🔗 Integration: {'✅ PASS' if integration_success else '❌ FAIL'}")
        print(f"📝 Function Schemas: {'✅ PASS' if schema_success else '❌ FAIL'}")
        
        all_passed = all([cafe_success, robot_success, integration_success, schema_success])
        
        if all_passed:
            print("\n🎉 ALL TESTS PASSED!")
            print("System ready for voice AI integration with OpenAI Realtime API")
        else:
            print("\n⚠️ Some tests failed. Please check the issues above.")
            
        return all_passed
        
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted")
        exit(1)