# Run the MCP Server

To run the MCP server for the todo tools:

```bash
python run_mcp_server.py
```

The server will start and listen for MCP protocol requests on stdin, responding on stdout according to the MCP specification.

# Test the Implementation

To verify that the MCP tools work correctly:

```bash
python test_mcp_tools.py
```

This will run through all the functionality of the MCP tools and confirm they work as expected.