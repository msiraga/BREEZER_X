"""OpenAI function-call compatible definitions for Breezer tools."""

TOOL_FUNCTIONS = [
    {
        "name": "file_read",
        "description": "Read the contents of a file within the current workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path to the file from the workspace root."
                },
                "encoding": {
                    "type": "string",
                    "description": "Encoding to use when reading the file (default utf-8).",
                    "enum": ["utf-8", "latin-1", "utf-16"],
                }
            },
            "required": ["path"],
            "additionalProperties": False
        }
    },
    {
        "name": "file_write",
        "description": "Write text content to a file within the workspace. Requires confirmation for destructive edits.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path to the target file."
                },
                "content": {
                    "type": "string",
                    "description": "Full text content to write into the file."
                },
                "mode": {
                    "type": "string",
                    "enum": ["overwrite", "append"],
                    "description": "Whether to overwrite or append to the file (default overwrite)."
                },
                "confirm": {
                    "type": "boolean",
                    "description": "Set to true once the user has approved the write operation."
                }
            },
            "required": ["path", "content"],
            "additionalProperties": False
        }
    },
    {
        "name": "file_list",
        "description": "List files and folders beneath a directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative directory path to inspect."
                },
                "max_entries": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 500,
                    "description": "Maximum number of entries to return (default 50)."
                }
            },
            "required": ["path"],
            "additionalProperties": False
        }
    },
    {
        "name": "git_status",
        "description": "Show git status for the workspace with optional short or detailed output.",
        "parameters": {
            "type": "object",
            "properties": {
                "detailed": {
                    "type": "boolean",
                    "description": "When true, include verbose porcelain output."
                }
            },
            "additionalProperties": False
        }
    },
    {
        "name": "git_diff",
        "description": "Compute a git diff for the workspace (optionally for a specific path).",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Optional relative path to limit the diff."
                },
                "staged": {
                    "type": "boolean",
                    "description": "When true, show staged changes (git diff --cached)."
                }
            },
            "additionalProperties": False
        }
    },
    {
        "name": "terminal_command",
        "description": "Run a whitelisted terminal command within the workspace sandbox.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Identifier of the whitelisted command to execute (e.g., npm_test, pytest)."
                }
            },
            "required": ["command"],
            "additionalProperties": False
        }
    },
    {
        "name": "web_lookup",
        "description": "Perform a curated web lookup (documentation or knowledge base).",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Short search query to forward to the approved provider."
                }
            },
            "required": ["query"],
            "additionalProperties": False
        }
    },
    {
        "name": "workspace_diagnostics",
        "description": "Fetch summarized LSP diagnostics and workspace symbols.",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 200,
                    "description": "Maximum number of diagnostics to return (default 50)."
                }
            },
            "additionalProperties": False
        }
    }
]
