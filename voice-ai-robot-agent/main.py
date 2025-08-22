#!/usr/bin/env python3
"""
Main entry point for Voice AI Robot Agent
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from voice_cafe_kiosk_demo import main
import asyncio

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))