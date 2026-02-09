#!/usr/bin/env python3
"""
Script to run the MCP server for the todo tools
"""

import os
import sys
import subprocess


def run_server():
    """Run the MCP server"""
    print("Starting MCP Server for Todo Tools...")
    print("The server will listen for MCP requests on stdin and write responses to stdout")

    # Set environment variable for user ID (this would normally come from the MCP client)
    os.environ.setdefault('USER_ID', 'default_user')

    try:
        # Run the server
        from server import main
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error running server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_server()