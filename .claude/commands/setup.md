# Claude Token Monitor - Setup Guide

This guide will help you install the claude-token-monitor statusline plugin.

## Installation Steps

### 1. Detect Platform

First, detect the user's platform and architecture:
- Windows: `os.platform() === 'win32'`
- macOS: `os.platform() === 'darwin'`
- Linux: `os.platform() === 'linux'`

For architecture:
- AMD64/Intel: `process.arch === 'x64'` or `os.arch() === 'amd64'`
- ARM64: `process.arch === 'arm64'` or `os.arch() === 'arm64'`

### 2. Get Latest Version

Fetch the latest release version from GitHub:
```
GET https://api.github.com/repos/young1lin/claude-token-monitor/releases/latest
```

Extract the `tag_name` (e.g., `v1.0.0`) and remove the `v` prefix.

### 3. Download Binary

Download URLs are constructed as:
```
https://github.com/young1lin/claude-token-monitor/releases/download/v{VERSION}/statusline_{OS}_{ARCH}.{EXT}
```

| Platform | OS | Arch | Extension |
|----------|-----|------|-----------|
| Windows | windows | amd64 | .zip |
| macOS (Intel) | darwin | amd64 | .tar.gz |
| macOS (Apple Silicon) | darwin | arm64 | .tar.gz |
| Linux | linux | amd64 | .tar.gz |

Example download URLs:
- Windows: `https://github.com/young1lin/claude-token-monitor/releases/download/v1.0.0/statusline_windows_amd64.zip`
- macOS Intel: `https://github.com/young1lin/claude-token-monitor/releases/download/v1.0.0/statusline_darwin_amd64.tar.gz`
- macOS ARM: `https://github.com/young1lin/claude-token-monitor/releases/download/v1.0.0/statusline_darwin_arm64.tar.gz`
- Linux: `https://github.com/young1lin/claude-token-monitor/releases/download/v1.0.0/statusline_linux_amd64.tar.gz`

### 4. Extract and Install

**Windows (.zip)**:
```bash
# Extract to temporary directory
unzip statusline_windows_amd64.zip -d /tmp/claude-token-monitor
# Move to Claude directory
mv /tmp/claude-token-monitor/statusline.exe ~/.claude/statusline.exe
```

**macOS/Linux (.tar.gz)**:
```bash
# Extract to temporary directory
tar -xzf statusline_darwin_amd64.tar.gz -C /tmp/claude-token-monitor
# Move to Claude directory
mv /tmp/claude-token-monitor/statusline ~/.claude/statusline
# Set executable permission
chmod +x ~/.claude/statusline
```

### 5. Configure Claude Code

Add or update the statusLine configuration in `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline{.exe}",
    "env": {
      "STATUSLINE_MULTILINE": "1"
    }
  }
}
```

**Note**: On Windows, the path should be:
```json
"command": "C:\\\\Users\\\\<username>\\\\.claude\\\\statusline.exe"
```

### 6. Verify Installation

Test the installation:
```bash
# Windows
~\.claude\statusline.exe --help

# macOS/Linux
~/.claude/statusline --help
```

Expected output: Statusline plugin showing token usage, git status, etc.

## Troubleshooting

### Download Fails
- Verify the version exists at: https://github.com/young1lin/claude-token-monitor/releases
- Check your internet connection

### Binary Won't Execute (macOS/Linux)
```bash
chmod +x ~/.claude/statusline
```

### Statusline Not Showing
1. Check `~/.claude/settings.json` has the correct statusLine configuration
2. Restart Claude Code
3. Verify the binary path is correct

### Windows Path Issues
Ensure paths in settings.json use double backslashes:
```json
"command": "C:\\\\Users\\\\username\\\\.claude\\\\statusline.exe"
```

## Uninstallation

To remove the plugin:
1. Delete the binary: `rm ~/.claude/statusline` (or `~\.claude\statusline.exe` on Windows)
2. Remove the statusLine configuration from `~/.claude/settings.json`
