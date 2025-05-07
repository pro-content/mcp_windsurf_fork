# Project Tasks

## 1. Environment Setup

- [ ] Install Python 3.10 or higher.
- [ ] Set up a virtual environment using `uv` or `venv`.
- [ ] Install the MCP Python SDK:
  ```bash
  uv add "mcp[cli]"
  ```

## 2. Project Initialization

- [ ] Create the project directory structure.
- [ ] Initialize a Git repository.
- [ ] Set up `.gitignore` to exclude unnecessary files.

## 3. Basic MCP Server Implementation

- [ ] Create a Python script (e.g., `server.py`) and initialize the `FastMCP` server.
- [ ] Define a simple tool (e.g., addition function) to test server functionality.
- [ ] Run the server and verify it starts without errors.

## 4. Filesystem Tools Development

- [ ] Implement a tool to read file contents given a relative path.
- [ ] Implement a tool to list directory contents.
- [ ] Implement a tool to search files using regex patterns.
- [ ] Implement a resource to monitor file changes (optional).

## 5. Security Enhancements

- [ ] Implement directory access restrictions to prevent traversal attacks.
- [ ] Integrate `.gitignore` pattern recognition to exclude specific files.
- [ ] Set up API key authentication for accessing tools and resources.

## 6. Client Integration

- [ ] Configure Claude Desktop to connect with the MCP server.
- [ ] Test server functionalities through the client interface.
- [ ] Handle client requests and ensure appropriate responses.

## 7. Testing and Validation

- [ ] Write unit tests for each tool and resource.
- [ ] Perform integration testing with clients.
- [ ] Validate security measures against potential threats.

## 8. Documentation

- [ ] Document the setup process and usage instructions.
- [ ] Provide examples for each tool and resource.
- [ ] Include security guidelines and best practices.

## 9. Integrate MCP Server with Cascade

- [ ] Update Cascade MCP Configuration:

  - Edit `~/.codeium/windsurf/mcp_config.json` to include:

    ```json
    {
      "mcpServers": {
        "filesystem": {
          "command": "/usr/bin/python3",
          "args": [
            "/home/yourusername/path/to/server.py"
          ],
          "env": {
            "PYTHONUNBUFFERED": "1",
            "LOG_LEVEL": "DEBUG"
          }
        }
      }
    }
    ```

- [ ] Implement extensive debug logging in `server.py`:

  ```python
  import logging
  import os

  log_level = os.getenv("LOG_LEVEL", "INFO").upper()
  logging.basicConfig(
      level=log_level,
      format='%(asctime)s [%(levelname)s] %(message)s',
      handlers=[logging.StreamHandler()]
  )

  logger = logging.getLogger(__name__)

  @mcp.tool()
  def read_file(path: str) -> str:
      logger.debug(f"Attempting to read file at path: {path}")
      try:
          with open(path, 'r') as file:
              content = file.read()
          logger.debug(f"Successfully read file at path: {path}")
          return content
      except Exception as e:
          logger.error(f"Error reading file at path: {path} - {e}")
          raise
  ```

- [ ] Restart Cascade and verify MCP connection and debug log output.

## 10. Integrate MCP Server with Cursor

- [ ] **Configure MCP Server in Cursor:**

  - Open Cursor.
  - Navigate to `Settings` > `Features` > `MCP`.
  - Click on `+ Add New MCP Server`.
  - In the configuration window:
    - **Name:** `filesystem`
    - **Type:** `command`
    - **Command:** `/usr/bin/python3`
    - **Arguments:** `["/home/yourusername/path/to/server.py"]`
    - **Environment Variables:**
      - `PYTHONUNBUFFERED`: `1`
      - `LOG_LEVEL`: `DEBUG`
  - Save the configuration.

- [ ] **Verify Integration:**

  - Restart Cursor to apply the new configuration.
  - Open the MCP panel to ensure the `filesystem` server is listed.
  - Test the server functionalities through Cursor's interface.
  - Check the logs to ensure that debug messages are being recorded as expected.

**Note:** Replace `/usr/bin/python3` and `/home/yourusername/path/to/server.py` with the appropriate paths on your system.

