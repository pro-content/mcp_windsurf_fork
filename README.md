# Filesystem MCP Server

A Model Context Protocol (MCP) server that provides tools for interacting with the local filesystem. This server enables LLMs like Claude to access and manipulate files and directories on your system through a secure, standardized interface.

## Features

- **Read File Contents**: Access the contents of files on your system
- **List Directory Entries**: View files and directories with metadata
- **Search Files**: Find files matching patterns and containing specific content
- **Monitor File Changes** (optional): Track changes to files in real-time

## Installation

### Prerequisites

- Python 3.10 or higher
- Virtual environment (recommended)

### Setup

1. Clone this repository
2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install "mcp[cli]" watchdog
   ```

## Usage

### Running the Server

You can run the server directly:

```bash
python server.py
```

Or use the MCP CLI:

```bash
mcp run server.py
```

### Development Mode

For testing and debugging, use the MCP Inspector:

```bash
mcp dev server.py
```

### Integration with Cascade

To integrate with Cascade, update the MCP configuration file at `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "/usr/bin/python3",
      "args": [
        "/path/to/your/server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1",
        "LOG_LEVEL": "DEBUG",
        "MCP_BASE_DIR": "/path/to/allowed/directory"
      }
    }
  }
}
```

### Integration with Cursor

1. Open Cursor
2. Navigate to Settings > Features > MCP
3. Click "+ Add New MCP Server"
4. Configure as follows:
   - **Name:** `filesystem`
   - **Type:** `command`
   - **Command:** `/usr/bin/python3` (or path to your Python executable)
   - **Arguments:** `["/path/to/your/server.py"]`
   - **Environment Variables:**
     - `PYTHONUNBUFFERED`: `1`
     - `LOG_LEVEL`: `DEBUG`
     - `MCP_BASE_DIR`: `/path/to/allowed/directory`

## Configuration

The server can be configured using environment variables:

- `LOG_LEVEL`: Set the logging level (DEBUG, INFO, WARNING, ERROR)
- `MCP_BASE_DIR`: Set the base directory for file operations (default: current directory)

## Security

This server implements several security measures:

- **Path Validation**: Prevents directory traversal attacks
- **Base Directory Restriction**: Limits access to a specified directory
- **Error Handling**: Provides informative but safe error messages

## Tools and Resources

### Tools

1. **read_file(path: str) -> str**
   - Read and return the contents of a file
   - Path can be absolute or relative to the base directory

2. **list_directory(path: str, include_hidden: bool = False) -> List[Dict]**
   - List contents of a directory with metadata
   - Optionally include hidden files

3. **search_files(pattern: str, search_path: str = ".", recursive: bool = True, content_regex: Optional[str] = None) -> List[Dict]**
   - Search for files matching a glob pattern
   - Optionally search for content matching a regex pattern

### Resources

1. **file_changes://recent** (optional, requires watchdog)
   - Get a list of recent file changes monitored by the server

## License

MIT
