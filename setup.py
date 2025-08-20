#!/usr/bin/env python3
"""
Setup script for Voice AI Agent HRI system.
"""

import subprocess
import sys
import os

def install_requirements():
    """Install Python requirements"""
    print("Installing Python requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install requirements: {e}")
        return False
    return True

def setup_env_file():
    """Setup environment file"""
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            print("Creating .env file from .env.example...")
            with open(".env.example", "r") as src, open(".env", "w") as dst:
                dst.write(src.read())
            print("✓ .env file created")
            print("⚠ Please edit .env file and add your OpenAI API key")
        else:
            print("⚠ .env.example not found")
    else:
        print("✓ .env file already exists")

def check_audio_dependencies():
    """Check if audio dependencies are available"""
    print("Checking audio dependencies...")
    try:
        import pyaudio
        print("✓ PyAudio is available")
    except ImportError:
        print("⚠ PyAudio not available. You may need to install it separately:")
        print("  Ubuntu/Debian: sudo apt-get install python3-pyaudio")
        print("  macOS: brew install portaudio && pip install pyaudio")
        print("  Windows: pip install pyaudio")

def main():
    """Main setup function"""
    print("Voice AI Agent HRI Setup")
    print("=" * 30)
    
    if not install_requirements():
        sys.exit(1)
        
    setup_env_file()
    check_audio_dependencies()
    
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Run: python src/main.py")

if __name__ == "__main__":
    main()