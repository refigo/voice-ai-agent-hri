# Voice AI Robot Cafe Agent with Kiosk Control - Demo Script

A comprehensive voice-controlled cafe ordering system with real-time kiosk UI manipulation using OpenAI's Realtime API. Supports both voice and text input with automatic audio capability detection.

## 🚀 Quick Start

### 1. Prerequisites
```bash
# Set your OpenAI API key
export OPENAI_API_KEY=your_actual_api_key_here

# Install basic dependencies
pip install -r requirements.txt

# For voice mode, install PyAudio (optional)
pip install pyaudio
```

### 2. Run the Demo
```bash
# Auto-detect voice/text mode based on PyAudio availability
python voice_cafe_kiosk_demo.py

# Force voice mode (requires PyAudio)
python voice_cafe_kiosk_demo.py --mode voice

# Force text mode (no audio dependencies)
python voice_cafe_kiosk_demo.py --mode text
```

### 3. Voice & Text Interactions

#### Voice Mode (with PyAudio)
```
🎤 [Speak naturally] "Show me the coffee menu"
🔊 AI responds with natural speech
🖥️  Kiosk displays coffee menu with prices and descriptions

🎤 [Speak naturally] "Highlight the americano"  
🔊 "Perfect choice! I've highlighted the Americano on the screen."
🖥️  Kiosk highlights americano with details

🎤 [Speak naturally] "I want a latte with oat milk"
🔊 "Great! I'll add a latte with oat milk to your order."
🖥️  Kiosk shows updated cart with order total
```

#### Text Mode (fallback)
```
👤 You (text): Show me the coffee menu
🤖 Cafe Agent: I'll display our coffee menu for you right now!
🖥️  [Kiosk displays coffee menu with prices and descriptions]

👤 You (text): I want a latte with oat milk  
🤖 Cafe Agent: Great! I'll add a latte with oat milk to your order.
🖥️  [Kiosk shows updated cart with order total]
```

## 🎯 Key Features

### 🎤 Voice Capabilities
- **Speech Recognition**: OpenAI Whisper for accurate voice transcription
- **Natural Speech Output**: AI responds with natural voice synthesis
- **Voice Interruption**: Interrupt AI responses in real-time
- **Auto-Detection**: Automatically detects PyAudio availability
- **Fallback Mode**: Graceful degradation to text mode

### 🖥️ Voice-Controlled Kiosk Functions
- **Menu Display**: `display_menu_categories()`, `get_menu_by_category()`
- **Item Highlighting**: `highlight_menu_item()`, `display_item_details()`
- **Cart Management**: `display_cart_view()`, `display_checkout_screen()`
- **Order Processing**: `add_item_to_order()`, `process_payment()`

### 🤖 Integrated Robot Controls
- **LED Control**: Change robot LED colors with voice commands
- **Status Monitoring**: Get robot system status via voice
- **Movement**: Basic robot navigation commands

### ⚡ Real-time Interactive Features
- **Voice-driven UI updates**: Kiosk responds immediately to voice commands
- **Visual menu highlighting**: Items highlighted when mentioned in speech
- **Dynamic cart display**: Real-time cart updates with pricing
- **Professional interface**: Clean terminal-based kiosk design
- **Interruption support**: Natural conversation flow with voice interruption

## 💬 Example Voice Interactions

### Menu Browsing
```
"Show me the menu"
"Display coffee options"
"What pastries do you have?"
"Show cold drinks"
```

### Item Selection
```
"Highlight the americano"
"Show me details for the latte"
"Tell me about the cappuccino"
```

### Ordering
```
"I want an americano"
"Add a latte with oat milk to my order"
"Order a cappuccino with extra shot and almond milk"
"Get me two blueberry muffins"
```

### Cart and Checkout
```
"Show my current order"
"What's in my cart?"
"Display checkout options"
"I want to pay with card"
```

### Robot Control
```
"Change LED to blue"
"Make the robot light red"
"What's the robot status?"
```

## 🛠️ Technical Implementation

### Function Registration System
- **16 total functions** registered with the voice agent
- **10 OpenAI function schemas** for Realtime API integration
- **Automatic function discovery** from cafe, kiosk, and robot modules

### OpenAI Realtime API Integration
- **Text-mode interaction** for reliable testing and development
- **Function calling** with proper parameter validation
- **Error handling** with user-friendly feedback
- **Session configuration** optimized for cafe service scenarios

### Modular Architecture
```
voice_cafe_kiosk_demo.py
├── VoiceCafeKioskAgent (main agent class)
├── CafeKioskSystem (ordering logic)
├── KioskUIController (display management)
└── RobotController (robot functions)
```

## 🧪 Testing

### Run Tests
```bash
python test_voice_cafe_demo.py
```

### Test Coverage
- ✅ Component initialization
- ✅ Function registration
- ✅ OpenAI schema formatting
- ✅ Function execution
- ✅ Kiosk UI updates
- ✅ Cafe system integration

## 📝 Supported Menu Items

### ☕ Coffee (5 items)
- Espresso, Cappuccino, Latte, Americano, Macchiato
- Customizations: extra shot, decaf, milk alternatives, syrups

### 🥤 Cold Drinks (3 items)
- Iced Coffee, Frappuccino, Smoothie
- Customizations: extra shot, flavors, protein powder

### 🥐 Pastries (4 items)
- Croissant, Blueberry Muffin, Danish, Bagel
- Customizations: bagel types (everything, sesame, plain)

### 🥪 Sandwiches (3 items)
- Club Sandwich, Grilled Cheese, Veggie Wrap
- Fresh, made-to-order options

## 🔧 Configuration

### Environment Variables
```bash
export OPENAI_API_KEY=your_openai_api_key
```

### Customization Options
- Modify menu items in `src/cafe_system.py`
- Adjust kiosk display layout in `src/kiosk_ui.py`
- Add robot functions in `src/hri_functions.py`
- Update AI instructions in `voice_cafe_kiosk_demo.py`

## 📈 Performance

- **Function Registration**: 16 functions in ~200ms
- **Kiosk Display Updates**: Real-time visual feedback
- **OpenAI API Calls**: Optimized for function calling
- **Memory Usage**: Lightweight, terminal-based interface

## 🎨 Visual Interface

The kiosk UI provides:
- **80-character wide** professional display
- **Category-based navigation** with emoji indicators
- **Item highlighting** with visual focus (►)
- **Real-time cart updates** with pricing calculations
- **Checkout interface** with payment method selection

## 🚀 Next Steps

To extend the demo:
1. **Add voice input**: Integrate PyAudio for speech recognition
2. **Enhance UI**: Create web-based kiosk interface
3. **Add payment**: Integrate real payment processing
4. **Robot integration**: Connect to actual robot hardware
5. **Analytics**: Add order tracking and customer insights

## ⚠️ Notes

- Uses **text input** for reliable testing (no PyAudio dependency)
- Requires **OpenAI API key** with Realtime API access
- **Terminal-based** kiosk display for development convenience
- **Function calls** are executed locally (no actual robot hardware needed)

---

This demo showcases the power of combining conversational AI with real-time function calling to create an interactive, voice-controlled cafe experience with visual feedback!