"""
Cafe Kiosk Order System for Voice AI Agent
Handles menu management, orders, payments, and customer interactions
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PaymentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class MenuItem:
    id: str
    name: str
    description: str
    price: float
    category: str
    available: bool = True
    preparation_time: int = 5  # minutes
    customizations: List[str] = None
    
    def __post_init__(self):
        if self.customizations is None:
            self.customizations = []

@dataclass
class OrderItem:
    menu_item: MenuItem
    quantity: int
    customizations: List[str] = None
    notes: str = ""
    
    def __post_init__(self):
        if self.customizations is None:
            self.customizations = []
    
    @property
    def total_price(self) -> float:
        return self.menu_item.price * self.quantity

@dataclass
class Order:
    id: str
    customer_name: str
    items: List[OrderItem]
    status: OrderStatus
    payment_status: PaymentStatus
    total_amount: float
    created_at: float
    estimated_ready_time: Optional[float] = None
    special_instructions: str = ""
    
    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self.items)

class CafeKioskSystem:
    def __init__(self):
        self.menu = self._initialize_menu()
        self.current_order: Optional[Order] = None
        self.order_history: List[Order] = []
        self.order_counter = 1
        self.customer_name = ""
        
    def _initialize_menu(self) -> Dict[str, MenuItem]:
        """Initialize the cafe menu"""
        menu_items = [
            # Coffee
            MenuItem("esp001", "Espresso", "Rich and bold espresso shot", 3.50, "coffee", 
                    customizations=["extra_shot", "decaf"]),
            MenuItem("cap001", "Cappuccino", "Espresso with steamed milk foam", 4.50, "coffee",
                    customizations=["extra_shot", "decaf", "oat_milk", "almond_milk", "soy_milk"]),
            MenuItem("lat001", "Latte", "Smooth espresso with steamed milk", 4.75, "coffee",
                    customizations=["extra_shot", "decaf", "vanilla", "caramel", "oat_milk", "almond_milk"]),
            MenuItem("ame001", "Americano", "Espresso with hot water", 3.75, "coffee",
                    customizations=["extra_shot", "decaf"]),
            MenuItem("mac001", "Macchiato", "Espresso marked with milk foam", 4.25, "coffee",
                    customizations=["extra_shot", "decaf", "caramel"]),
            
            # Cold Drinks
            MenuItem("ice001", "Iced Coffee", "Cold brew coffee over ice", 4.00, "cold_drinks",
                    customizations=["extra_shot", "vanilla", "caramel", "oat_milk"]),
            MenuItem("fra001", "Frappuccino", "Blended ice coffee drink", 5.50, "cold_drinks",
                    customizations=["extra_shot", "vanilla", "caramel", "chocolate"]),
            MenuItem("smo001", "Smoothie", "Fresh fruit smoothie", 6.00, "cold_drinks",
                    customizations=["protein_powder", "extra_fruit"]),
            
            # Pastries
            MenuItem("cro001", "Croissant", "Buttery, flaky pastry", 3.25, "pastries"),
            MenuItem("muf001", "Blueberry Muffin", "Fresh blueberry muffin", 2.75, "pastries"),
            MenuItem("dan001", "Danish", "Sweet pastry with fruit filling", 3.00, "pastries"),
            MenuItem("bag001", "Bagel", "Fresh bagel with cream cheese", 4.00, "pastries",
                    customizations=["everything", "sesame", "plain"]),
            
            # Sandwiches
            MenuItem("san001", "Club Sandwich", "Turkey, bacon, lettuce, tomato", 8.50, "sandwiches"),
            MenuItem("gri001", "Grilled Cheese", "Melted cheese on sourdough", 6.00, "sandwiches"),
            MenuItem("veg001", "Veggie Wrap", "Fresh vegetables in tortilla wrap", 7.25, "sandwiches"),
        ]
        
        return {item.id: item for item in menu_items}
        
    async def get_menu_by_category(self, category: str = "all") -> str:
        """Get menu items by category"""
        if category == "all":
            categories = ["coffee", "cold_drinks", "pastries", "sandwiches"]
        else:
            categories = [category.lower()]
        
        menu_text = "📋 **CAFE MENU**\n\n"
        
        for cat in categories:
            items = [item for item in self.menu.values() 
                    if item.category == cat and item.available]
            
            if items:
                cat_name = cat.replace("_", " ").title()
                menu_text += f"**{cat_name}:**\n"
                
                for item in items:
                    menu_text += f"• {item.name} - ${item.price:.2f}\n"
                    menu_text += f"  {item.description}\n"
                    if item.customizations:
                        menu_text += f"  Customizations: {', '.join(item.customizations)}\n"
                    menu_text += "\n"
                    
        return menu_text
        
    async def start_new_order(self, customer_name: str = "") -> str:
        """Start a new order for a customer"""
        if self.current_order and self.current_order.status == OrderStatus.PENDING:
            return "You already have an active order. Would you like to continue with it or cancel and start fresh?"
            
        self.customer_name = customer_name if customer_name else f"Customer {self.order_counter}"
        
        self.current_order = Order(
            id=f"ORD{self.order_counter:04d}",
            customer_name=self.customer_name,
            items=[],
            status=OrderStatus.PENDING,
            payment_status=PaymentStatus.PENDING,
            total_amount=0.0,
            created_at=time.time()
        )
        
        self.order_counter += 1
        
        return f"Hello {self.customer_name}! I've started a new order for you (Order #{self.current_order.id}). What would you like to order today?"
        
    async def add_item_to_order(self, item_name: str, quantity: int = 1, 
                              customizations: List[str] = None, notes: str = "") -> str:
        """Add an item to the current order"""
        if not self.current_order:
            await self.start_new_order()
            
        # Find menu item by name (fuzzy matching)
        menu_item = None
        item_name_lower = item_name.lower()
        
        for item in self.menu.values():
            if (item_name_lower in item.name.lower() or 
                item.name.lower() in item_name_lower):
                menu_item = item
                break
                
        if not menu_item:
            available_items = [item.name for item in self.menu.values() if item.available]
            return f"Sorry, I couldn't find '{item_name}' on our menu. Available items include: {', '.join(available_items[:5])}..."
            
        if not menu_item.available:
            return f"Sorry, {menu_item.name} is currently unavailable."
            
        # Validate customizations
        if customizations:
            invalid_customizations = [c for c in customizations if c not in menu_item.customizations]
            if invalid_customizations:
                return f"Invalid customizations for {menu_item.name}: {', '.join(invalid_customizations)}. Available: {', '.join(menu_item.customizations)}"
        
        order_item = OrderItem(
            menu_item=menu_item,
            quantity=quantity,
            customizations=customizations or [],
            notes=notes
        )
        
        self.current_order.items.append(order_item)
        self.current_order.total_amount += order_item.total_price
        
        customization_text = ""
        if customizations:
            customization_text = f" with {', '.join(customizations)}"
            
        return f"Added {quantity}x {menu_item.name}{customization_text} to your order (${order_item.total_price:.2f}). Current total: ${self.current_order.total_amount:.2f}"
        
    async def remove_item_from_order(self, item_name: str, quantity: int = 1) -> str:
        """Remove an item from the current order"""
        if not self.current_order or not self.current_order.items:
            return "No active order or order is empty."
            
        item_name_lower = item_name.lower()
        
        for i, order_item in enumerate(self.current_order.items):
            if item_name_lower in order_item.menu_item.name.lower():
                if order_item.quantity <= quantity:
                    # Remove entire item
                    removed_item = self.current_order.items.pop(i)
                    self.current_order.total_amount -= removed_item.total_price
                    return f"Removed {removed_item.menu_item.name} from your order. Current total: ${self.current_order.total_amount:.2f}"
                else:
                    # Reduce quantity
                    price_reduction = order_item.menu_item.price * quantity
                    order_item.quantity -= quantity
                    self.current_order.total_amount -= price_reduction
                    return f"Reduced {order_item.menu_item.name} quantity by {quantity}. Current total: ${self.current_order.total_amount:.2f}"
                    
        return f"Item '{item_name}' not found in your current order."
        
    async def view_current_order(self) -> str:
        """View the current order details"""
        if not self.current_order or not self.current_order.items:
            return "No active order."
            
        order_text = f"🛍️ **Current Order #{self.current_order.id}**\n"
        order_text += f"Customer: {self.current_order.customer_name}\n\n"
        
        for i, item in enumerate(self.current_order.items, 1):
            order_text += f"{i}. {item.quantity}x {item.menu_item.name} - ${item.total_price:.2f}\n"
            if item.customizations:
                order_text += f"   Customizations: {', '.join(item.customizations)}\n"
            if item.notes:
                order_text += f"   Notes: {item.notes}\n"
                
        order_text += f"\n**Total Items:** {self.current_order.item_count}\n"
        order_text += f"**Total Amount:** ${self.current_order.total_amount:.2f}\n"
        order_text += f"**Status:** {self.current_order.status.value}\n"
        
        return order_text
        
    async def confirm_order(self) -> str:
        """Confirm the current order"""
        if not self.current_order or not self.current_order.items:
            return "No items in order to confirm."
            
        # Calculate estimated preparation time
        max_prep_time = max(item.menu_item.preparation_time for item in self.current_order.items)
        self.current_order.estimated_ready_time = time.time() + (max_prep_time * 60)
        self.current_order.status = OrderStatus.CONFIRMED
        
        estimated_time = time.strftime("%H:%M", time.localtime(self.current_order.estimated_ready_time))
        
        order_summary = await self.view_current_order()
        return f"{order_summary}\n✅ Order confirmed! Estimated ready time: {estimated_time}\nPlease proceed to payment."
        
    async def process_payment(self, payment_method: str = "card", amount: float = None) -> str:
        """Process payment for the current order"""
        if not self.current_order:
            return "No active order to pay for."
            
        if self.current_order.payment_status == PaymentStatus.COMPLETED:
            return "Payment already completed for this order."
            
        if amount and amount < self.current_order.total_amount:
            return f"Insufficient payment. Order total: ${self.current_order.total_amount:.2f}, Paid: ${amount:.2f}"
            
        self.current_order.payment_status = PaymentStatus.PROCESSING
        
        # Simulate payment processing
        await asyncio.sleep(2)
        
        self.current_order.payment_status = PaymentStatus.COMPLETED
        self.current_order.status = OrderStatus.PREPARING
        
        # Add to order history
        self.order_history.append(self.current_order)
        
        result = f"💳 Payment of ${self.current_order.total_amount:.2f} processed successfully via {payment_method}!\n"
        result += f"Order #{self.current_order.id} is now being prepared.\n"
        
        if self.current_order.estimated_ready_time:
            ready_time = time.strftime("%H:%M", time.localtime(self.current_order.estimated_ready_time))
            result += f"Estimated ready time: {ready_time}"
            
        # Clear current order
        self.current_order = None
        
        return result
        
    async def cancel_order(self) -> str:
        """Cancel the current order"""
        if not self.current_order:
            return "No active order to cancel."
            
        order_id = self.current_order.id
        self.current_order.status = OrderStatus.CANCELLED
        self.current_order = None
        
        return f"Order {order_id} has been cancelled."
        
    async def check_order_status(self, order_id: str = None) -> str:
        """Check the status of an order"""
        if order_id:
            # Check specific order from history
            for order in self.order_history:
                if order.id == order_id:
                    status_text = f"📋 Order {order.id} Status: {order.status.value.title()}\n"
                    status_text += f"Payment: {order.payment_status.value.title()}\n"
                    
                    if order.estimated_ready_time and order.status == OrderStatus.PREPARING:
                        ready_time = time.strftime("%H:%M", time.localtime(order.estimated_ready_time))
                        current_time = time.time()
                        if current_time >= order.estimated_ready_time:
                            status_text += "Your order should be ready now!"
                        else:
                            status_text += f"Estimated ready time: {ready_time}"
                            
                    return status_text
                    
            return f"Order {order_id} not found."
        else:
            # Check current order
            if self.current_order:
                return await self.view_current_order()
            else:
                return "No active order."
                
    async def get_recommendations(self, preference: str = "") -> str:
        """Get menu recommendations based on preferences"""
        recommendations = []
        
        preference_lower = preference.lower()
        
        if "coffee" in preference_lower or "caffeine" in preference_lower:
            recommendations.extend(["lat001", "cap001", "ame001"])
        elif "cold" in preference_lower or "iced" in preference_lower:
            recommendations.extend(["ice001", "fra001", "smo001"])
        elif "sweet" in preference_lower or "dessert" in preference_lower:
            recommendations.extend(["fra001", "dan001", "muf001"])
        elif "healthy" in preference_lower or "light" in preference_lower:
            recommendations.extend(["smo001", "veg001"])
        elif "filling" in preference_lower or "hungry" in preference_lower:
            recommendations.extend(["san001", "veg001", "bag001"])
        else:
            # Popular items
            recommendations = ["lat001", "cap001", "san001", "muf001"]
            
        rec_text = "🌟 **Recommendations for you:**\n\n"
        
        for item_id in recommendations[:3]:  # Top 3 recommendations
            item = self.menu[item_id]
            rec_text += f"• **{item.name}** - ${item.price:.2f}\n"
            rec_text += f"  {item.description}\n\n"
            
        return rec_text
        
    async def modify_order_item(self, item_name: str, new_customizations: List[str] = None, 
                               new_notes: str = None) -> str:
        """Modify an item in the current order"""
        if not self.current_order or not self.current_order.items:
            return "No active order to modify."
            
        item_name_lower = item_name.lower()
        
        for order_item in self.current_order.items:
            if item_name_lower in order_item.menu_item.name.lower():
                if new_customizations is not None:
                    # Validate customizations
                    invalid_customizations = [c for c in new_customizations 
                                            if c not in order_item.menu_item.customizations]
                    if invalid_customizations:
                        return f"Invalid customizations: {', '.join(invalid_customizations)}"
                    order_item.customizations = new_customizations
                    
                if new_notes is not None:
                    order_item.notes = new_notes
                    
                return f"Modified {order_item.menu_item.name} in your order."
                
        return f"Item '{item_name}' not found in your current order."

# Function schemas for the cafe kiosk system
CAFE_FUNCTION_SCHEMAS = [
    {
        "type": "function",
        "name": "get_menu_by_category",
        "description": "Show menu items by category (coffee, cold_drinks, pastries, sandwiches, or all)",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Menu category to display",
                    "enum": ["all", "coffee", "cold_drinks", "pastries", "sandwiches"]
                }
            }
        }
    },
    {
        "name": "start_new_order",
        "description": "Start a new order for a customer",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_name": {
                    "type": "string",
                    "description": "Customer's name (optional)"
                }
            }
        }
    },
    {
        "name": "add_item_to_order",
        "description": "Add an item to the current order",
        "parameters": {
            "type": "object",
            "properties": {
                "item_name": {
                    "type": "string",
                    "description": "Name of the menu item to add"
                },
                "quantity": {
                    "type": "integer",
                    "description": "Quantity of the item (default: 1)"
                },
                "customizations": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of customizations (e.g., extra_shot, oat_milk)"
                },
                "notes": {
                    "type": "string",
                    "description": "Special notes or instructions"
                }
            },
            "required": ["item_name"]
        }
    },
    {
        "name": "remove_item_from_order",
        "description": "Remove an item from the current order",
        "parameters": {
            "type": "object",
            "properties": {
                "item_name": {
                    "type": "string",
                    "description": "Name of the item to remove"
                },
                "quantity": {
                    "type": "integer",
                    "description": "Quantity to remove (default: 1)"
                }
            },
            "required": ["item_name"]
        }
    },
    {
        "name": "view_current_order",
        "description": "View the current order details and total",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "confirm_order",
        "description": "Confirm the current order and calculate preparation time",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "process_payment",
        "description": "Process payment for the confirmed order",
        "parameters": {
            "type": "object",
            "properties": {
                "payment_method": {
                    "type": "string",
                    "description": "Payment method (card, cash, mobile)",
                    "enum": ["card", "cash", "mobile"]
                },
                "amount": {
                    "type": "number",
                    "description": "Payment amount (optional, will use order total)"
                }
            }
        }
    },
    {
        "name": "cancel_order",
        "description": "Cancel the current order",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "check_order_status",
        "description": "Check the status of an order",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "Order ID to check (optional, checks current order if not provided)"
                }
            }
        }
    },
    {
        "name": "get_recommendations",
        "description": "Get menu recommendations based on customer preferences",
        "parameters": {
            "type": "object",
            "properties": {
                "preference": {
                    "type": "string",
                    "description": "Customer preference (coffee, cold, sweet, healthy, filling, etc.)"
                }
            }
        }
    },
    {
        "name": "modify_order_item",
        "description": "Modify customizations or notes for an item in the current order",
        "parameters": {
            "type": "object",
            "properties": {
                "item_name": {
                    "type": "string",
                    "description": "Name of the item to modify"
                },
                "new_customizations": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "New customizations for the item"
                },
                "new_notes": {
                    "type": "string",
                    "description": "New notes for the item"
                }
            },
            "required": ["item_name"]
        }
    }
]