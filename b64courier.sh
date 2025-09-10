#!/bin/bash
# B64Courier - File transfer via base64 JSON for TTY
# Usage: ./b64courier.sh encode <path> <pattern1> [pattern2...] [-o output.json]
#        ./b64courier.sh decode <json_file> [-o output_dir]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python "${SCRIPT_DIR}/../etc/b64courier.py" "$@"
