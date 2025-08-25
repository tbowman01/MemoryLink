#!/usr/bin/env python3
"""
MemoryLink Backend Runner

Simple script to start the MemoryLink backend server with proper configuration.
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def main():
    """Main entry point."""
    try:
        import uvicorn
        from src.config import get_settings
        
        # Load settings
        settings = get_settings()
        
        print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
        print(f"📍 Running on {settings.host}:{settings.port}")
        print(f"🔧 Debug mode: {'ON' if settings.debug else 'OFF'}")
        print(f"📚 API docs: http://{settings.host}:{settings.port}/docs")
        print(f"❤️  Health check: http://{settings.host}:{settings.port}/health")
        print()
        
        # Run the server
        uvicorn.run(
            "src.main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            log_level="debug" if settings.debug else "info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down MemoryLink backend...")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Install dependencies with: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()