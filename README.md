# Unified Voice AI Agent for Cafe Ordering & HRI

A comprehensive Python-based voice AI system combining cafe ordering and Human-Robot Interaction (HRI) using OpenAI's Realtime API with function calling capabilities.

## 🎯 Features

- **Unified Conversation System**: Single interface for both cafe ordering and robot control
- **Multi-Modal Input**: Voice and text input options for testing and accessibility
- **Real-time Voice Interaction**: OpenAI Realtime API with audio streaming
- **Cafe Ordering System**: Complete menu management, ordering, and payment processing
- **Robot Control**: Movement commands, sensor readings, and interaction capabilities
- **Intelligent Context Switching**: Automatic mode detection between ordering and robot control
- **Extensible Function Framework**: Easy addition of new cafe or robot functions

## 🚀 Quick Start

### 1. Install Dependencies
```bash
python setup.py
```

### 2. Configure API Key
Create a `.env` file with your OpenAI API key:
```bash
OPENAI_API_KEY=your_api_key_here
```

### 3. Install Audio Dependencies (Optional)
For voice input support:
- **Ubuntu/Debian**: `sudo apt-get install python3-pyaudio`
- **macOS**: `brew install portaudio && pip install pyaudio`
- **Windows**: `pip install pyaudio`

### 4. Run the Unified System
```bash
# Auto-detect voice/text mode
python src/unified_main.py

# Force voice mode
python src/unified_main.py --mode voice

# Force text mode (no audio dependencies needed)
python src/unified_main.py --mode text
```

## 💡 Example Interactions

### ☕ Cafe Ordering
- **"Hello, show me today's menu"**
- **"I'd like a latte with oat milk and extra shot"**
- **"What do you recommend for something cold?"**
- **"Add two blueberry muffins and check my total"**
- **"I'm ready to pay with card"**

### 🤖 Robot Control
- **"Move forward 3 meters then stop"**
- **"Turn left, set LED to blue, and take a photo"**
- **"What's your current status and battery level?"**
- **"Scan the environment and report what you see"**

### 🔄 Combined Interactions
- **"Take my order then deliver it to table 5"**
- **"Show me the menu while you move to the counter"**
- **"After I pay, guide me to the pickup area"**
- **"Switch to robot mode and patrol the cafe"**

## 🏗️ System Architecture

### Core Components
- **Unified Voice Agent**: Handles both voice and text input with OpenAI Realtime API
- **Cafe System**: Complete ordering system with 15+ menu items across 4 categories
- **Robot Controller**: Movement, sensors, and interaction capabilities
- **Context Manager**: Intelligent switching between cafe and robot modes

### Available Functions

#### 🤖 Robot Functions
- `move_forward(distance, speed)` - Move robot forward
- `move_backward(distance, speed)` - Move robot backward  
- `turn_left(angle)` - Turn robot left
- `turn_right(angle)` - Turn robot right
- `stop()` - Stop all movement
- `get_status()` - Get robot status
- `set_led_color(color)` - Control LED colors
- `play_sound(sound_type)` - Play sound effects
- `take_photo()` - Take a photo
- `scan_environment()` - Scan for objects

#### ☕ Cafe Functions
- `get_menu_by_category(category)` - Show menu by category
- `start_new_order(customer_name)` - Begin new order
- `add_item_to_order(item, quantity, customizations)` - Add items
- `view_current_order()` - Show order details
- `process_payment(method)` - Process payment
- `get_recommendations(preference)` - Get personalized suggestions

## 🧪 Testing

### Run Tests
```bash
python test_cafe_system.py
```

### Text Mode Testing
For development and testing without audio:
```bash
python src/unified_main.py --mode text
```

## 📁 Project Structure

```
src/
├── unified_main.py         # 🆕 Main unified entry point
├── unified_voice_agent.py  # 🆕 Unified voice/text agent
├── cafe_system.py          # Cafe ordering system
├── hri_functions.py        # Robot function definitions
├── main.py                 # Legacy HRI-only entry point
├── cafe_main.py            # Legacy cafe-only entry point
└── voice_agent.py          # Legacy base voice agent
test_cafe_system.py         # Test suite
```

## 🔧 Legacy Components

The repository includes legacy components for backward compatibility:
- `src/main.py` - Original HRI-only system
- `src/cafe_main.py` - Original cafe-only system
- Multiple voice agent variations for development history
