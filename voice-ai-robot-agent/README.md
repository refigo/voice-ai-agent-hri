# Voice Cafe Kiosk Demo

A voice-controlled AI cafe ordering system with real-time kiosk UI integration using OpenAI's Realtime API.

## 🎯 Features

- **Voice Interaction**: Natural voice conversations with real-time interruption support
- **Kiosk UI Control**: Dynamic visual display updates during conversation
- **Cafe Ordering**: Complete menu browsing, ordering, and payment processing
- **Robot Integration**: Basic robot control functions (LED, movement, status)
- **Multi-modal**: Supports both voice and text input modes

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API Key with Realtime API access
- PyAudio (for voice mode) - optional for text mode

### Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd voice-cafe-kiosk-repository
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export OPENAI_API_KEY=your_openai_api_key_here
```

### Running the Demo

**Voice Mode (recommended):**
```bash
python voice_cafe_kiosk_demo.py --mode voice
```

**Text Mode:**
```bash
python voice_cafe_kiosk_demo.py --mode text
```

**Auto Mode (detects PyAudio availability):**
```bash
python voice_cafe_kiosk_demo.py
```

## 🎤 Voice Commands

Try these example voice interactions:

- "Show me the coffee menu"
- "Highlight the americano" 
- "I want a latte with oat milk"
- "Show my cart"
- "Process payment with card"
- "Change LED to blue"

## 🖥️ Kiosk Display Features

The kiosk UI automatically updates to show:
- Welcome screen
- Menu categories and items
- Item highlights during conversation
- Shopping cart contents
- Checkout screens

## 🏗️ Architecture

- `voice_cafe_kiosk_demo.py` - Main application entry point
- `src/cafe_system.py` - Cafe ordering logic and menu management
- `src/kiosk_ui.py` - Kiosk display controller
- `src/hri_functions.py` - Robot control functions

## 🔧 Configuration

The system supports various configuration options:

- **Voice Detection Threshold**: Adjustable in session config
- **Audio Settings**: 24kHz PCM16 format
- **Model**: Uses GPT-4 Realtime Preview
- **Turn Detection**: Server-side VAD with interruption support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🛠️ Troubleshooting

**PyAudio Installation Issues:**
```bash
# Ubuntu/Debian
sudo apt-get install portaudio19-dev python3-pyaudio

# macOS
brew install portaudio
pip install pyaudio

# Windows
pip install pipwin
pipwin install pyaudio
```

**OpenAI API Issues:**
- Ensure you have access to the Realtime API
- Check your API key has proper permissions
- Verify your account has sufficient credits

## 📞 Support

For issues and questions, please open an issue in this repository.