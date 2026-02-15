#!/usr/bin/env python3
"""
Unified launcher for the Incident Handler Dashboard
Starts the FastAPI server and provides options to run the automation
"""

import uvicorn
import sys
import os

def main():
    print("=" * 60)
    print("🚀 Incident Handler Dashboard")
    print("=" * 60)
    print()
    print("Starting dashboard server on http://localhost:8000")
    print()
    print("📊 Dashboard Features:")
    print("  • Real-time incident processing feed")
    print("  • Live execution logs")
    print("  • Processing statistics")
    print("  • Historical data viewer")
    print()
    print("💡 To run the automation:")
    print("  python main.py")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    try:
        uvicorn.run(
            "api_server:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard server stopped")
        sys.exit(0)

if __name__ == "__main__":
    main()
