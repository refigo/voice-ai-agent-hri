# Voice AI Agent for HRI

A Python-based voice AI agent for Human-Robot Interaction (HRI) using OpenAI's Realtime API with function calling capabilities.

## Features

- Real-time voice interaction using OpenAI Realtime API
- Function calling for robot control commands
- Audio input/output handling
- WebSocket connection management
- Extensible robot function framework

## Setup

1. **Install dependencies:**
   ```bash
   python setup.py
   ```

2. **Configure API key:**
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key to `.env`

3. **Install audio dependencies (if needed):**
   - Ubuntu/Debian: `sudo apt-get install python3-pyaudio`
   - macOS: `brew install portaudio && pip install pyaudio`
   - Windows: `pip install pyaudio`

## Usage

Run the voice AI agent:
```bash
python src/main.py
```

## Available Robot Functions

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

## Voice Commands Examples

- "Move forward 2 meters"
- "Turn left 45 degrees"
- "What's your current status?"
- "Set LED to blue"
- "Take a photo"
- "Scan the environment"

## Cafe Service Robot

The system now includes a complete cafe kiosk ordering system with conversational AI:

### Run Cafe Service Robot:
```bash
python src/cafe_main.py
```

### Cafe Features:
- **Menu Management**: 15+ items across 4 categories (coffee, cold drinks, pastries, sandwiches)
- **Order Management**: Add/remove items, customizations, order confirmation
- **Payment Processing**: Card, cash, mobile payment simulation
- **Conversation Context**: Intelligent mode switching between ordering and robot control
- **Recommendations**: Personalized suggestions based on preferences

### Voice Commands for Cafe:
- "Show me the coffee menu"
- "I'd like a latte with oat milk and extra shot"
- "What do you recommend for something cold?"
- "Add two blueberry muffins to my order"
- "Can I see my current order?"
- "I'd like to pay with card"
- "Cancel my order"

### Combined Interactions:
- "Take my order and then move to table 3"
- "After I pay, scan the environment"
- "Set LED to green and show me the menu"

## Testing

Run the test suite:
```bash
python test_cafe_system.py
```

## Project Structure

```
src/
├── main.py              # Original HRI-only entry point
├── cafe_main.py         # Cafe service robot entry point
├── voice_agent.py       # Base voice AI agent
├── cafe_voice_agent.py  # Enhanced agent with cafe integration
├── hri_functions.py     # Robot function definitions
└── cafe_system.py       # Cafe ordering system
test_cafe_system.py      # Test suite
```
