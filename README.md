# B64Courier

File transfer via base64 JSON for TTY when SFTP/FTP unavailable, with SHA256 integrity verification and copy-paste resilience.

## Overview

B64Courier enables secure file transfer through terminal copy-paste when traditional file transfer protocols (SFTP, FTP, SCP) are not available. It encodes files into JSON format with base64 content and SHA256 hashes, allowing transfer through any text-based channel.

## Features

- **Wildcard support**: Process multiple files with patterns like `*.log`, `*.tar.gz`
- **Integrity verification**: SHA256 hash validation ensures data integrity
- **Copy-paste resilient**: Handles line wrapping, smart quotes, and whitespace corruption
- **Cross-platform**: Python 2/3 compatible
- **TTY optimized**: Direct stdout output for easy copy-paste workflows

## Installation

Place files in your project structure:
```
yourpath/
├── bin/
│   └── b64courier.sh          # Shell wrapper
└── etc/
    └── b64courier.py          # Main script
```

## Usage

### Encode Files
```bash
# Single file
python b64courier.py encode /path/to/files "filename.txt"

# Multiple files with wildcards
python b64courier.py encode /var/log "*.log" "error*"

# Save to file
python b64courier.py encode /etc "*.conf" -o config_backup.json

# TTY output (for copy-paste)
python b64courier.py encode /home/user "*.tar.gz"
```

### Decode Files
```bash
# Restore to current directory
python b64courier.py decode backup.json

# Restore to specific directory
python b64courier.py decode backup.json -o /tmp/restored

# Using shell wrapper
./b64courier.sh decode backup.json -o ./files
```

## Workflow Example

**Source system:**
```bash
# Encode files to JSON
python b64courier.py encode /var/log "*.log" > logs.json

# Or direct TTY output
python b64courier.py encode /etc "nginx.conf"
# Copy the JSON output
```

**Target system:**
```bash
# Paste JSON into file, then decode
python b64courier.py decode logs.json -o /tmp/restored

# Verify files are identical (SHA256 verified automatically)
```

## JSON Format

```json
{
  "files": [
    {
      "filename": "example.txt",
      "sha256": "abc123...",
      "content_b64": "SGVsbG8gV29ybGQ="
    }
  ],
  "total_files": 1
}
```

## Integrity Protection

B64Courier handles common TTY corruption issues:

- **Line wrapping**: Removes all whitespace from base64 content
- **Smart quotes**: Converts `"` `"` `'` `'` to standard quotes
- **Character encoding**: Forces UTF-8 with ASCII-safe JSON output
- **Base64 padding**: Automatically corrects missing padding
- **SHA256 verification**: Validates file integrity after decode

## Error Handling

- **Missing files**: Warns about unmatched patterns, continues processing
- **Corrupted data**: SHA256 mismatch detection with detailed error messages
- **Invalid JSON**: Handles formatting issues from copy-paste corruption
- **Partial success**: Reports successful vs failed file counts

## Requirements

- Python 2.7+ or Python 3.x
- Standard library only (no external dependencies)

## Use Cases

- **Air-gapped systems**: Transfer files through terminal sessions
- **Restricted environments**: When file transfer protocols are blocked
- **Emergency recovery**: Quick file extraction through console access
- **Documentation**: Include small files directly in text documents
- **Remote support**: Transfer configuration files through screen sharing

## Limitations

- **File size**: Large files create very long JSON (base64 increases size by ~33%)
- **Memory usage**: Entire file content loaded into memory during processing
- **Terminal limits**: Some terminals have paste size restrictions

## Security Notes

- SHA256 provides integrity verification, not encryption
- Base64 encoding is not encryption - data is readable if intercepted
- Use secure channels when possible for sensitive data transfer
