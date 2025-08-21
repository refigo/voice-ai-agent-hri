#!/usr/bin/env python3
"""
Kiosk UI Manipulation System for Robot Cafe Service
Provides visual menu display and interaction functions for terminal testing
"""

import asyncio
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from cafe_system import CafeKioskSystem, MenuItem

class UIState(Enum):
    WELCOME = "welcome"
    MENU_CATEGORIES = "menu_categories"
    MENU_ITEMS = "menu_items"
    ITEM_DETAILS = "item_details"
    CART_VIEW = "cart_view"
    CHECKOUT = "checkout"
    ORDER_CONFIRMATION = "order_confirmation"

@dataclass
class KioskDisplay:
    title: str
    content: List[str]
    footer: str
    highlighted_item: Optional[int] = None
    
class KioskUIController:
    """Controls the kiosk UI display and interactions"""
    
    def __init__(self, cafe_system: CafeKioskSystem):
        self.cafe_system = cafe_system
        self.current_state = UIState.WELCOME
        self.current_category = None
        self.highlighted_index = 0
        self.cart_items = []
        self.display_history = []
        
        # UI Configuration
        self.screen_width = 80
        self.screen_height = 25
        self.border_char = "="
        self.highlight_char = "►"
        self.normal_prefix = "  "
        
    def clear_screen(self):
        """Clear terminal screen (simulated)"""
        print("\n" * 3)  # Simple clear for testing
        print("🖥️  KIOSK DISPLAY UPDATED")
        print(self.border_char * self.screen_width)
        
    def format_display_box(self, title: str, content: List[str], footer: str = "") -> str:
        """Format content in a display box"""
        box = []
        
        # Top border
        box.append(self.border_char * self.screen_width)
        
        # Title
        title_line = f"║ {title.center(self.screen_width - 4)} ║"
        box.append(title_line)
        box.append("║" + "─" * (self.screen_width - 2) + "║")
        
        # Content
        for line in content:
            if len(line) > self.screen_width - 4:
                line = line[:self.screen_width - 7] + "..."
            content_line = f"║ {line.ljust(self.screen_width - 4)} ║"
            box.append(content_line)
            
        # Padding to maintain consistent height
        while len(box) < self.screen_height - 3:
            box.append(f"║{' ' * (self.screen_width - 2)}║")
            
        # Footer
        if footer:
            box.append("║" + "─" * (self.screen_width - 2) + "║")
            footer_line = f"║ {footer.ljust(self.screen_width - 4)} ║"
            box.append(footer_line)
            
        # Bottom border
        box.append(self.border_char * self.screen_width)
        
        return "\n".join(box)
        
    async def display_welcome_screen(self) -> str:
        """Display welcome screen"""
        self.current_state = UIState.WELCOME
        self.clear_screen()
        
        content = [
            "",
            "🤖 ☕ WELCOME TO ROBOT CAFE",
            "",
            "Your AI-powered coffee experience awaits!",
            "",
            "🎤 VOICE COMMANDS:",
            "• Say 'show menu' to browse our offerings",
            "• Say 'I want a latte' for quick orders",
            "• Say 'help' for assistance",
            "",
            "🖱️  TOUCH COMMANDS:",
            "• Touch here to start browsing",
            "• Swipe to navigate categories",
            "",
            "Ready to serve you!"
        ]
        
        display = self.format_display_box(
            "ROBOT CAFE KIOSK",
            content,
            "🎯 Say 'show menu' or touch to begin"
        )
        
        print(display)
        return "Welcome screen displayed on kiosk"
        
    async def display_menu_categories(self) -> str:
        """Display menu categories for selection"""
        self.current_state = UIState.MENU_CATEGORIES
        self.clear_screen()
        
        categories = [
            ("☕ COFFEE", "Espresso, Latte, Cappuccino & more"),
            ("🥤 COLD DRINKS", "Iced Coffee, Frappuccino, Smoothies"),
            ("🥐 PASTRIES", "Fresh Croissants, Muffins, Danish"),
            ("🥪 SANDWICHES", "Gourmet sandwiches & wraps")
        ]
        
        content = ["", "SELECT A CATEGORY:", ""]
        
        for i, (category, description) in enumerate(categories):
            prefix = self.highlight_char if i == self.highlighted_index else self.normal_prefix
            content.append(f"{prefix}{category}")
            content.append(f"    {description}")
            content.append("")
            
        display = self.format_display_box(
            "MENU CATEGORIES",
            content,
            "🎤 Say category name or 📱 touch to select"
        )
        
        print(display)
        return f"Menu categories displayed, highlighting index {self.highlighted_index}"
        
    async def display_menu_items(self, category: str) -> str:
        """Display menu items for a specific category"""
        self.current_state = UIState.MENU_ITEMS
        self.current_category = category.lower().replace(" ", "_")
        self.clear_screen()
        
        # Get items from cafe system
        menu_items = [item for item in self.cafe_system.menu.values() 
                     if item.category == self.current_category and item.available]
        
        if not menu_items:
            return f"No items available in category: {category}"
            
        content = [f"", f"🍽️  {category.upper()} MENU", ""]
        
        for i, item in enumerate(menu_items):
            prefix = self.highlight_char if i == self.highlighted_index else self.normal_prefix
            content.append(f"{prefix}{item.name} - ${item.price:.2f}")
            content.append(f"    {item.description}")
            if item.customizations:
                content.append(f"    Customizations: {', '.join(item.customizations[:3])}")
            content.append("")
            
        display = self.format_display_box(
            f"{category.upper()} MENU",
            content,
            "🎤 Say item name or 📱 touch to select • 🔙 Say 'back' for categories"
        )
        
        print(display)
        return f"Displaying {len(menu_items)} items in {category} category"
        
    async def highlight_menu_item(self, item_name: str) -> str:
        """Highlight a specific menu item"""
        if self.current_state != UIState.MENU_ITEMS:
            return "Must be viewing menu items to highlight"
            
        menu_items = [item for item in self.cafe_system.menu.values() 
                     if item.category == self.current_category and item.available]
        
        # Find item index
        for i, item in enumerate(menu_items):
            if item_name.lower() in item.name.lower():
                self.highlighted_index = i
                await self.display_menu_items(self.current_category.replace("_", " "))
                return f"Highlighted {item.name} on kiosk display"
                
        return f"Item '{item_name}' not found in current menu"
        
    async def display_item_details(self, item_name: str) -> str:
        """Display detailed view of a menu item"""
        self.current_state = UIState.ITEM_DETAILS
        self.clear_screen()
        
        # Find the item
        item = None
        for menu_item in self.cafe_system.menu.values():
            if item_name.lower() in menu_item.name.lower():
                item = menu_item
                break
                
        if not item:
            return f"Item '{item_name}' not found"
            
        content = [
            "",
            f"📋 ITEM DETAILS",
            "",
            f"🏷️  Name: {item.name}",
            f"💰 Price: ${item.price:.2f}",
            f"📝 Description: {item.description}",
            f"⏱️  Prep Time: ~{item.preparation_time} minutes",
            "",
            "🎛️  CUSTOMIZATIONS:",
        ]
        
        if item.customizations:
            for customization in item.customizations:
                content.append(f"  • {customization.replace('_', ' ').title()}")
        else:
            content.append("  • No customizations available")
            
        content.extend([
            "",
            "🛒 ADD TO ORDER:",
            "  Quantity: [ 1 ] [ 2 ] [ 3 ] [ 4+ ]",
            ""
        ])
        
        display = self.format_display_box(
            f"{item.name.upper()} - ${item.price:.2f}",
            content,
            "🎤 Say 'add to cart' or 📱 touch quantity • 🔙 Say 'back' for menu"
        )
        
        print(display)
        return f"Displaying details for {item.name}"
        
    async def display_cart_view(self) -> str:
        """Display current cart contents"""
        self.current_state = UIState.CART_VIEW
        self.clear_screen()
        
        if not self.cafe_system.current_order or not self.cafe_system.current_order.items:
            content = [
                "",
                "🛒 YOUR CART",
                "",
                "Your cart is empty",
                "",
                "Start browsing our menu to add items!",
                ""
            ]
            
            display = self.format_display_box(
                "SHOPPING CART - EMPTY",
                content,
                "🎤 Say 'show menu' to start shopping"
            )
        else:
            order = self.cafe_system.current_order
            content = [
                "",
                f"🛒 YOUR CART ({order.item_count} items)",
                ""
            ]
            
            for i, item in enumerate(order.items):
                prefix = self.highlight_char if i == self.highlighted_index else self.normal_prefix
                content.append(f"{prefix}{item.quantity}x {item.menu_item.name} - ${item.total_price:.2f}")
                if item.customizations:
                    content.append(f"    Customizations: {', '.join(item.customizations)}")
                if item.notes:
                    content.append(f"    Notes: {item.notes}")
                content.append("")
                
            content.extend([
                "─" * 40,
                f"💰 SUBTOTAL: ${order.total_amount:.2f}",
                f"📊 TAX: ${order.total_amount * 0.08:.2f}",
                f"💵 TOTAL: ${order.total_amount * 1.08:.2f}",
                ""
            ])
            
            display = self.format_display_box(
                f"SHOPPING CART - ${order.total_amount:.2f}",
                content,
                "🎤 Say 'checkout' to pay or 'add more' to continue shopping"
            )
            
        print(display)
        return "Cart view displayed on kiosk"
        
    async def display_checkout_screen(self) -> str:
        """Display checkout/payment screen"""
        self.current_state = UIState.CHECKOUT
        self.clear_screen()
        
        if not self.cafe_system.current_order:
            return "No order to checkout"
            
        order = self.cafe_system.current_order
        total_with_tax = order.total_amount * 1.08
        
        content = [
            "",
            "💳 CHECKOUT",
            "",
            f"Order Total: ${order.total_amount:.2f}",
            f"Tax (8%): ${order.total_amount * 0.08:.2f}",
            f"Final Total: ${total_with_tax:.2f}",
            "",
            "💳 PAYMENT METHODS:",
            "",
            "  [💳] Credit/Debit Card",
            "  [📱] Mobile Payment",
            "  [💵] Cash",
            "",
            "Select your preferred payment method"
        ]
        
        display = self.format_display_box(
            f"CHECKOUT - ${total_with_tax:.2f}",
            content,
            "🎤 Say payment method or 📱 touch to select"
        )
        
        print(display)
        return f"Checkout screen displayed with total ${total_with_tax:.2f}"
        
    async def display_order_confirmation(self, order_id: str) -> str:
        """Display order confirmation screen"""
        self.current_state = UIState.ORDER_CONFIRMATION
        self.clear_screen()
        
        content = [
            "",
            "✅ ORDER CONFIRMED!",
            "",
            f"🎫 Order Number: {order_id}",
            f"⏰ Estimated Time: 8-12 minutes",
            "",
            "📱 You will receive notifications when:",
            "  • Your order is being prepared",
            "  • Your order is ready for pickup",
            "",
            "📍 PICKUP LOCATION:",
            "  Main Counter - Follow the green lights",
            "",
            "Thank you for choosing Robot Cafe!"
        ]
        
        display = self.format_display_box(
            "ORDER CONFIRMED ✅",
            content,
            "🎤 Say 'new order' to start again or 'track order' for status"
        )
        
        print(display)
        return f"Order confirmation displayed for order {order_id}"
        
    async def navigate_up(self) -> str:
        """Navigate up in current menu"""
        if self.highlighted_index > 0:
            self.highlighted_index -= 1
            
        # Refresh current display
        if self.current_state == UIState.MENU_CATEGORIES:
            await self.display_menu_categories()
        elif self.current_state == UIState.MENU_ITEMS:
            await self.display_menu_items(self.current_category.replace("_", " "))
        elif self.current_state == UIState.CART_VIEW:
            await self.display_cart_view()
            
        return f"Navigated up, now highlighting index {self.highlighted_index}"
        
    async def navigate_down(self) -> str:
        """Navigate down in current menu"""
        # Get max index based on current state
        max_index = 0
        if self.current_state == UIState.MENU_CATEGORIES:
            max_index = 3  # 4 categories
        elif self.current_state == UIState.MENU_ITEMS:
            items = [item for item in self.cafe_system.menu.values() 
                    if item.category == self.current_category and item.available]
            max_index = len(items) - 1
        elif self.current_state == UIState.CART_VIEW and self.cafe_system.current_order:
            max_index = len(self.cafe_system.current_order.items) - 1
            
        if self.highlighted_index < max_index:
            self.highlighted_index += 1
            
        # Refresh current display
        if self.current_state == UIState.MENU_CATEGORIES:
            await self.display_menu_categories()
        elif self.current_state == UIState.MENU_ITEMS:
            await self.display_menu_items(self.current_category.replace("_", " "))
        elif self.current_state == UIState.CART_VIEW:
            await self.display_cart_view()
            
        return f"Navigated down, now highlighting index {self.highlighted_index}"
        
    async def select_highlighted_item(self) -> str:
        """Select the currently highlighted item"""
        if self.current_state == UIState.MENU_CATEGORIES:
            categories = ["coffee", "cold_drinks", "pastries", "sandwiches"]
            if self.highlighted_index < len(categories):
                category = categories[self.highlighted_index]
                self.highlighted_index = 0  # Reset for next screen
                await self.display_menu_items(category.replace("_", " "))
                return f"Selected {category} category"
                
        elif self.current_state == UIState.MENU_ITEMS:
            items = [item for item in self.cafe_system.menu.values() 
                    if item.category == self.current_category and item.available]
            if self.highlighted_index < len(items):
                item = items[self.highlighted_index]
                await self.display_item_details(item.name)
                return f"Selected {item.name} for details"
                
        return "No item to select"
        
    async def go_back(self) -> str:
        """Navigate back to previous screen"""
        if self.current_state == UIState.MENU_ITEMS:
            self.highlighted_index = 0
            await self.display_menu_categories()
            return "Returned to menu categories"
        elif self.current_state == UIState.ITEM_DETAILS:
            self.highlighted_index = 0
            await self.display_menu_items(self.current_category.replace("_", " "))
            return "Returned to menu items"
        elif self.current_state in [UIState.CART_VIEW, UIState.CHECKOUT]:
            await self.display_menu_categories()
            return "Returned to menu categories"
        else:
            await self.display_welcome_screen()
            return "Returned to welcome screen"

# Function schemas for kiosk UI manipulation
KIOSK_UI_FUNCTION_SCHEMAS = [
    {
        "name": "display_welcome_screen",
        "description": "Display the welcome screen on the kiosk",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "display_menu_categories",
        "description": "Show menu categories on kiosk display for customer selection",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "display_menu_items",
        "description": "Display menu items for a specific category on the kiosk",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Category to display (coffee, cold drinks, pastries, sandwiches)"
                }
            },
            "required": ["category"]
        }
    },
    {
        "name": "highlight_menu_item",
        "description": "Highlight a specific menu item on the kiosk display",
        "parameters": {
            "type": "object",
            "properties": {
                "item_name": {
                    "type": "string",
                    "description": "Name of the menu item to highlight"
                }
            },
            "required": ["item_name"]
        }
    },
    {
        "name": "display_item_details",
        "description": "Show detailed information about a menu item on the kiosk",
        "parameters": {
            "type": "object",
            "properties": {
                "item_name": {
                    "type": "string",
                    "description": "Name of the menu item to show details for"
                }
            },
            "required": ["item_name"]
        }
    },
    {
        "name": "display_cart_view",
        "description": "Show current cart contents on the kiosk display",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "display_checkout_screen",
        "description": "Display checkout and payment options on the kiosk",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "display_order_confirmation",
        "description": "Show order confirmation screen with order details",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "Order ID to display in confirmation"
                }
            },
            "required": ["order_id"]
        }
    },
    {
        "name": "navigate_up",
        "description": "Navigate up in the current kiosk menu (move highlight up)",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "navigate_down",
        "description": "Navigate down in the current kiosk menu (move highlight down)",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "select_highlighted_item",
        "description": "Select the currently highlighted item on the kiosk",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "go_back",
        "description": "Navigate back to the previous kiosk screen",
        "parameters": {"type": "object", "properties": {}}
    }
]