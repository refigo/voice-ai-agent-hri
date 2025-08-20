"""
HRI (Human-Robot Interaction) functions for the voice AI agent.
These functions represent robot capabilities that can be called by the AI.
"""

import asyncio
import time
from typing import Dict, Any

class RobotController:
    def __init__(self):
        self.position = {"x": 0, "y": 0, "z": 0}
        self.battery_level = 85
        self.is_moving = False
        
    async def move_forward(self, distance: float = 1.0, speed: float = 0.5) -> str:
        """Move the robot forward by specified distance"""
        if self.is_moving:
            return "Robot is already moving. Please wait."
            
        self.is_moving = True
        print(f"Moving forward {distance}m at speed {speed}m/s")
        
        # Simulate movement time
        movement_time = distance / speed
        await asyncio.sleep(movement_time)
        
        self.position["x"] += distance
        self.is_moving = False
        
        return f"Moved forward {distance}m. Current position: {self.position}"
        
    async def move_backward(self, distance: float = 1.0, speed: float = 0.5) -> str:
        """Move the robot backward by specified distance"""
        if self.is_moving:
            return "Robot is already moving. Please wait."
            
        self.is_moving = True
        print(f"Moving backward {distance}m at speed {speed}m/s")
        
        movement_time = distance / speed
        await asyncio.sleep(movement_time)
        
        self.position["x"] -= distance
        self.is_moving = False
        
        return f"Moved backward {distance}m. Current position: {self.position}"
        
    async def turn_left(self, angle: float = 90.0) -> str:
        """Turn the robot left by specified angle in degrees"""
        if self.is_moving:
            return "Robot is already moving. Please wait."
            
        self.is_moving = True
        print(f"Turning left {angle} degrees")
        
        # Simulate turn time
        await asyncio.sleep(1.0)
        self.is_moving = False
        
        return f"Turned left {angle} degrees"
        
    async def turn_right(self, angle: float = 90.0) -> str:
        """Turn the robot right by specified angle in degrees"""
        if self.is_moving:
            return "Robot is already moving. Please wait."
            
        self.is_moving = True
        print(f"Turning right {angle} degrees")
        
        await asyncio.sleep(1.0)
        self.is_moving = False
        
        return f"Turned right {angle} degrees"
        
    async def stop(self) -> str:
        """Stop all robot movement"""
        self.is_moving = False
        print("Robot stopped")
        return "Robot movement stopped"
        
    async def get_status(self) -> str:
        """Get current robot status"""
        status = {
            "position": self.position,
            "battery_level": self.battery_level,
            "is_moving": self.is_moving,
            "timestamp": time.time()
        }
        return f"Robot status: {status}"
        
    async def set_led_color(self, color: str = "blue") -> str:
        """Set the robot's LED color"""
        valid_colors = ["red", "green", "blue", "yellow", "purple", "white", "off"]
        
        if color.lower() not in valid_colors:
            return f"Invalid color. Available colors: {', '.join(valid_colors)}"
            
        print(f"Setting LED color to {color}")
        return f"LED color set to {color}"
        
    async def play_sound(self, sound_type: str = "beep") -> str:
        """Play a sound effect"""
        valid_sounds = ["beep", "chirp", "notification", "alarm", "success"]
        
        if sound_type.lower() not in valid_sounds:
            return f"Invalid sound. Available sounds: {', '.join(valid_sounds)}"
            
        print(f"Playing {sound_type} sound")
        return f"Played {sound_type} sound"
        
    async def take_photo(self) -> str:
        """Take a photo with the robot's camera"""
        print("Taking photo...")
        await asyncio.sleep(1.0)  # Simulate camera operation
        
        filename = f"photo_{int(time.time())}.jpg"
        return f"Photo taken and saved as {filename}"
        
    async def scan_environment(self) -> str:
        """Scan the environment for obstacles and objects"""
        print("Scanning environment...")
        await asyncio.sleep(2.0)  # Simulate scanning time
        
        # Simulate detected objects
        objects = [
            {"type": "wall", "distance": 2.5, "direction": "front"},
            {"type": "chair", "distance": 1.8, "direction": "left"},
            {"type": "person", "distance": 3.2, "direction": "right"}
        ]
        
        return f"Environment scan complete. Detected objects: {objects}"

# Function schemas for OpenAI function calling
HRI_FUNCTION_SCHEMAS = [
    {
        "name": "move_forward",
        "description": "Move the robot forward by a specified distance",
        "parameters": {
            "type": "object",
            "properties": {
                "distance": {
                    "type": "number",
                    "description": "Distance to move in meters (default: 1.0)"
                },
                "speed": {
                    "type": "number",
                    "description": "Speed of movement in m/s (default: 0.5)"
                }
            }
        }
    },
    {
        "name": "move_backward",
        "description": "Move the robot backward by a specified distance",
        "parameters": {
            "type": "object",
            "properties": {
                "distance": {
                    "type": "number",
                    "description": "Distance to move in meters (default: 1.0)"
                },
                "speed": {
                    "type": "number",
                    "description": "Speed of movement in m/s (default: 0.5)"
                }
            }
        }
    },
    {
        "name": "turn_left",
        "description": "Turn the robot left by a specified angle",
        "parameters": {
            "type": "object",
            "properties": {
                "angle": {
                    "type": "number",
                    "description": "Angle to turn in degrees (default: 90)"
                }
            }
        }
    },
    {
        "name": "turn_right",
        "description": "Turn the robot right by a specified angle",
        "parameters": {
            "type": "object",
            "properties": {
                "angle": {
                    "type": "number",
                    "description": "Angle to turn in degrees (default: 90)"
                }
            }
        }
    },
    {
        "name": "stop",
        "description": "Stop all robot movement immediately",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "get_status",
        "description": "Get current robot status including position, battery, and movement state",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "set_led_color",
        "description": "Set the robot's LED color",
        "parameters": {
            "type": "object",
            "properties": {
                "color": {
                    "type": "string",
                    "description": "LED color (red, green, blue, yellow, purple, white, off)",
                    "enum": ["red", "green", "blue", "yellow", "purple", "white", "off"]
                }
            }
        }
    },
    {
        "name": "play_sound",
        "description": "Play a sound effect",
        "parameters": {
            "type": "object",
            "properties": {
                "sound_type": {
                    "type": "string",
                    "description": "Type of sound to play",
                    "enum": ["beep", "chirp", "notification", "alarm", "success"]
                }
            }
        }
    },
    {
        "name": "take_photo",
        "description": "Take a photo with the robot's camera",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "scan_environment",
        "description": "Scan the environment for obstacles and objects",
        "parameters": {"type": "object", "properties": {}}
    }
]