#!/usr/bin/env python3
"""
Simple demo of the Cafe Service Robot functionality
"""

import asyncio
from src.cafe_system import CafeKioskSystem
from src.hri_functions import RobotController

async def demo_cafe_interaction():
    """Demo a complete cafe interaction"""
    print("🤖 ☕ CAFE SERVICE ROBOT DEMO")
    print("=" * 40)
    
    # Initialize systems
    cafe = CafeKioskSystem()
    robot = RobotController()
    
    print("\n🎬 SCENARIO: Customer approaches the robot")
    
    # Robot detects customer and greets
    print("\n🤖 Robot: Welcome to our cafe! Let me scan the area...")
    scan_result = await robot.scan_environment()
    print(f"📍 {scan_result}")
    
    # Set welcome LED
    led_result = await robot.set_led_color("green")
    print(f"💡 {led_result}")
    
    # Play greeting sound
    sound_result = await robot.play_sound("chirp")
    print(f"🔊 {sound_result}")
    
    print("\n🤖 Robot: Hello! I'm your cafe service robot. Let me help you with your order.")
    
    # Start order
    order_result = await cafe.start_new_order("Sarah")
    print(f"📝 {order_result}")
    
    print("\n👤 Customer: Can you show me the coffee menu?")
    
    # Show coffee menu
    menu_result = await cafe.get_menu_by_category("coffee")
    print(f"📋 Robot shows menu:\n{menu_result[:300]}...")
    
    print("\n👤 Customer: I'd like a latte with oat milk and an extra shot, plus a blueberry muffin")
    
    # Add latte
    add_result = await cafe.add_item_to_order("latte", 1, ["oat_milk", "extra_shot"])
    print(f"➕ {add_result}")
    
    # Add muffin
    add_result = await cafe.add_item_to_order("blueberry muffin", 1)
    print(f"➕ {add_result}")
    
    print("\n👤 Customer: What's my total?")
    
    # Show order
    order_view = await cafe.view_current_order()
    print(f"📊 {order_view}")
    
    print("\n👤 Customer: Looks good! I'll pay with card")
    
    # Confirm order
    confirm_result = await cafe.confirm_order()
    print(f"✅ {confirm_result[:200]}...")
    
    # Process payment
    payment_result = await cafe.process_payment("card")
    print(f"💳 {payment_result}")
    
    print("\n🤖 Robot: Thank you! I'll move to the preparation area now.")
    
    # Robot moves to prep area
    move_result = await robot.move_forward(3.0, 0.5)
    print(f"🚶‍♂️ {move_result}")
    
    # Set LED to indicate preparing
    led_result = await robot.set_led_color("yellow")
    print(f"💡 {led_result} (order in preparation)")
    
    print("\n🤖 Robot: Your order is being prepared! I'll notify you when it's ready.")
    
    # Simulate some time passing
    await asyncio.sleep(1)
    
    # Take a photo for order verification
    photo_result = await robot.take_photo()
    print(f"📸 {photo_result}")
    
    # Play completion sound
    sound_result = await robot.play_sound("success")
    print(f"🔊 {sound_result}")
    
    # Set LED to ready
    led_result = await robot.set_led_color("blue")
    print(f"💡 {led_result} (order ready)")
    
    print("\n🤖 Robot: Your order is ready! Thank you for visiting our cafe!")
    
    print("\n" + "=" * 40)
    print("🎉 DEMO COMPLETED SUCCESSFULLY!")
    print("\nThis demo shows how the robot can:")
    print("• Greet customers with LEDs and sounds")
    print("• Take orders with natural conversation")
    print("• Process payments and confirmations")
    print("• Move around the cafe space")
    print("• Provide visual and audio feedback")
    print("• Handle the complete service workflow")

async def demo_menu_features():
    """Demo menu browsing and recommendations"""
    print("\n\n📋 MENU SYSTEM DEMO")
    print("=" * 30)
    
    cafe = CafeKioskSystem()
    
    print("\n🔍 Browsing menu by categories:")
    
    categories = ["coffee", "cold_drinks", "pastries", "sandwiches"]
    for category in categories:
        menu = await cafe.get_menu_by_category(category)
        print(f"\n📂 {category.title().replace('_', ' ')} Menu:")
        print(menu[:150] + "..." if len(menu) > 150 else menu)
    
    print("\n⭐ Getting recommendations:")
    preferences = ["coffee", "cold", "sweet", "healthy"]
    for pref in preferences:
        recs = await cafe.get_recommendations(pref)
        print(f"\n🌟 Recommendations for '{pref}':")
        print(recs[:200] + "..." if len(recs) > 200 else recs)

async def demo_robot_functions():
    """Demo robot control functions"""
    print("\n\n🤖 ROBOT CONTROL DEMO")
    print("=" * 30)
    
    robot = RobotController()
    
    print("\n📊 Initial robot status:")
    status = await robot.get_status()
    print(status)
    
    print("\n🚶‍♂️ Movement commands:")
    
    # Forward movement
    result = await robot.move_forward(2.0, 0.3)
    print(f"➡️ {result}")
    
    # Turn around
    result = await robot.turn_right(180)
    print(f"🔄 {result}")
    
    # Scan environment
    result = await robot.scan_environment()
    print(f"🔍 {result}")
    
    print("\n🎨 LED and sound effects:")
    
    colors = ["red", "green", "blue", "yellow"]
    sounds = ["beep", "chirp", "success"]
    
    for color in colors:
        result = await robot.set_led_color(color)
        print(f"💡 {result}")
        await asyncio.sleep(0.5)
    
    for sound in sounds:
        result = await robot.play_sound(sound)
        print(f"🔊 {result}")
        await asyncio.sleep(0.5)
    
    # Take final photo
    result = await robot.take_photo()
    print(f"📸 {result}")

async def main():
    """Run all demos"""
    try:
        await demo_cafe_interaction()
        await demo_menu_features()
        await demo_robot_functions()
        
        print("\n\n🎯 NEXT STEPS:")
        print("=" * 20)
        print("✅ All systems tested and working!")
        print("\n🔥 To run with voice AI:")
        print("1. Install PyAudio for voice features:")
        print("   sudo apt-get install python3-pyaudio")
        print("2. Run: python3 src/cafe_main.py")
        print("\n📝 For text-mode testing:")
        print("   python3 src/cafe_main_text.py")
        print("\n🧪 Run tests anytime:")
        print("   python3 test_cafe_system.py")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")

if __name__ == "__main__":
    asyncio.run(main())