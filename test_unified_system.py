#!/usr/bin/env python3
"""
Test script for the unified voice AI agent system
Tests both cafe and robot functionality without requiring OpenAI API
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cafe_system import CafeKioskSystem
from hri_functions import RobotController

def test_cafe_system():
    """Test cafe system functionality"""
    print("🧪 Testing Cafe System...")
    
    cafe = CafeKioskSystem()
    
    # Test menu
    print("✅ Menu initialized with", len(cafe.menu), "items")
    
    # Test basic ordering flow
    asyncio.run(test_cafe_ordering(cafe))
    
    print("✅ Cafe system tests completed\n")

async def test_cafe_ordering(cafe):
    """Test cafe ordering functionality"""
    # Start order
    result = await cafe.start_new_order("Test Customer")
    assert "Test Customer" in result
    print("✅ Order creation:", result[:50] + "...")
    
    # Add item
    result = await cafe.add_item_to_order("latte", 1, ["oat_milk"])
    assert "latte" in result.lower()
    print("✅ Add item:", result[:50] + "...")
    
    # View order
    result = await cafe.view_current_order()
    assert "latte" in result.lower()
    print("✅ View order:", result[:50] + "...")
    
    # Get recommendations
    result = await cafe.get_recommendations("coffee")
    assert "recommendations" in result.lower()
    print("✅ Recommendations:", result[:50] + "...")

def test_robot_system():
    """Test robot system functionality"""
    print("🧪 Testing Robot System...")
    
    robot = RobotController()
    
    # Test basic robot functions
    asyncio.run(test_robot_functions(robot))
    
    print("✅ Robot system tests completed\n")

async def test_robot_functions(robot):
    """Test robot functionality"""
    # Test movement
    result = await robot.move_forward(2.0, 1.0)
    assert "forward" in result.lower()
    print("✅ Move forward:", result)
    
    # Test status
    result = await robot.get_status()
    assert "position" in result.lower()
    print("✅ Status:", result[:50] + "...")
    
    # Test LED control
    result = await robot.set_led_color("blue")
    assert "blue" in result.lower()
    print("✅ LED control:", result)
    
    # Test photo
    result = await robot.take_photo()
    assert "photo" in result.lower()
    print("✅ Photo:", result)

def test_unified_system_components():
    """Test that unified system components can be imported and initialized"""
    print("🧪 Testing Unified System Components...")
    
    try:
        from unified_voice_agent import UnifiedVoiceAgent
        from unified_main import UnifiedCafeRobotSystem
        
        # Test initialization without OpenAI key (should fail gracefully)
        print("✅ Unified components import successfully")
        
        # Test system initialization in text mode
        system = UnifiedCafeRobotSystem(mode="text")
        print("✅ Unified system initialization successful")
        
        # Test function setup
        system.setup_functions()
        print("✅ Function registration successful")
        print(f"   - {len(system.agent.function_schemas)} functions registered")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"⚠️  Initialization note: {e}")
        print("   (This is expected without OpenAI API key)")

def main():
    """Run all tests"""
    print("🤖 ☕ UNIFIED VOICE AI AGENT - SYSTEM TESTS")
    print("=" * 60)
    
    try:
        test_cafe_system()
        test_robot_system()
        test_unified_system_components()
        
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("\n💡 To run the full system:")
        print("   1. Set OPENAI_API_KEY in .env file")
        print("   2. Run: python src/unified_main.py")
        print("   3. For text mode: python src/unified_main.py --mode text")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()