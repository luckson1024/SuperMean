#!/usr/bin/env python3
"""
SuperMean API Server

This script launches the FastAPI application using Uvicorn server.
It provides configuration for host, port, workers, and other server settings.
"""

import os
import sys
import argparse
import logging
from dotenv import load_dotenv
import uvicorn

# Add the parent directory to the Python path for proper imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("supermean-server")


def parse_arguments():
    """
    Parse command line arguments for server configuration.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(description="SuperMean API Server")
    parser.add_argument(
        "--host",
        type=str,
        default=os.getenv("API_HOST", "0.0.0.0"),
        help="Host to bind the server to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("API_PORT", "8000")),
        help="Port to bind the server to (default: 8000)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=int(os.getenv("API_WORKERS", "1")),
        help="Number of worker processes (default: 1)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload on code changes (development mode)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    return parser.parse_args()


def main():
    """
    Main function to start the Uvicorn server with the FastAPI application.
    """
    args = parse_arguments()
    
    # Log server configuration
    logger.info(f"Starting SuperMean API Server")
    logger.info(f"Host: {args.host}")
    logger.info(f"Port: {args.port}")
    logger.info(f"Workers: {args.workers}")
    logger.info(f"Reload: {args.reload}")
    logger.info(f"Debug: {args.debug}")
    
    # Configure Uvicorn settings
    uvicorn_config = {
        "app": "api.main:app",
        "host": args.host,
        "port": args.port,
        "workers": args.workers if not args.reload else 1,  # Workers must be 1 when reload is enabled
        "reload": args.reload,
        "log_level": "debug" if args.debug else "info",
        "proxy_headers": True,
        "forwarded_allow_ips": "*",
    }
    
    try:
        # Start the Uvicorn server
        uvicorn.run(**uvicorn_config)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()