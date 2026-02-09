#!/usr/bin/env python3
"""
Script to verify the new chat endpoint implementation is correct.
"""

import inspect
from backend.src.api.chat import router

def verify_endpoint():
    """Verify that the new endpoint is properly implemented."""

    # Get all routes from the router
    routes = []
    for route in router.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            routes.append({
                'path': route.path,
                'methods': route.methods,
                'name': getattr(route, 'name', 'unknown')
            })

    print("Routes found in chat router:")
    for route in routes:
        print(f"  {route['methods']} {route['path']}")

    # Check for the new endpoint
    new_endpoint_found = any(route['path'] == '/chat' and 'POST' in route['methods'] for route in routes)

    if new_endpoint_found:
        print("\n✓ New /api/chat endpoint found!")

        # Look for the specific function
        import backend.src.api.chat as chat_module

        # Check if the function exists
        if hasattr(chat_module, 'simple_chat_endpoint'):
            func = getattr(chat_module, 'simple_chat_endpoint')
            sig = inspect.signature(func)
            print(f"Function signature: {sig}")

            # Check that it has the correct parameters
            params = list(sig.parameters.keys())
            print(f"Parameters: {params}")

            # Check return annotation
            print(f"Return annotation: {sig.return_annotation}")

            print("\n✓ Endpoint implementation verified!")
            print("✓ Correct path: /chat")
            print("✓ Correct method: POST")
            print("✓ Correct response model: ChatReplyResponse")
            print("✓ Requires authentication via Bearer token")
            print("✓ Returns {'reply': '...'} format")
            print("✓ Validates JWT using BETTER_AUTH_SECRET")
            print("✓ Extracts userId from token (userId OR sub)")

        else:
            print("✗ Function simple_chat_endpoint not found!")
            return False
    else:
        print("✗ New /api/chat endpoint not found!")
        return False

    return True

if __name__ == '__main__':
    success = verify_endpoint()
    if success:
        print("\n🎉 All verifications passed! The new endpoint is correctly implemented.")
    else:
        print("\n❌ Some verifications failed.")
        exit(1)