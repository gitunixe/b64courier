#!/usr/bin/env python
import os
import sys
import json
import hashlib
import base64
import glob
import argparse

def encode_files(path, patterns, output_file):
    """Encode files to JSON with SHA256 and base64"""
    results = []
    
    for pattern in patterns:
        search_pattern = os.path.join(path, pattern)
        matched_files = glob.glob(search_pattern)
        
        if not matched_files:
            print("Warning: No files found for pattern '{}'".format(pattern), file=sys.stderr)
            continue
        
        for filepath in matched_files:
            if os.path.isfile(filepath):
                try:
                    with open(filepath, 'rb') as f:
                        content = f.read()
                    
                    sha256_hash = hashlib.sha256(content).hexdigest()
                    b64_content = base64.b64encode(content).decode('utf-8')
                    
                    results.append({
                        'filename': os.path.basename(filepath),
                        'sha256': sha256_hash,
                        'content_b64': b64_content
                    })
                except Exception as e:
                    results.append({
                        'filename': os.path.basename(filepath),
                        'error': str(e)
                    })
    
    if not results:
        print("Error: No files processed", file=sys.stderr)
        return False
    
    output_data = {
        'files': results,
        'total_files': len(results)
    }
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=True)
        print("Encoded {} files to {}".format(len(results), output_file))
    else:
        print(json.dumps(output_data, indent=2, ensure_ascii=True))
    
    return True

def decode_files(json_file, output_dir):
    """Decode JSON files back to original format"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            content = f.read()
        # Normalize whitespace and remove potential formatting issues
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        # Remove smart quotes and common character substitutions
        content = content.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
        data = json.loads(content)
    except Exception as e:
        print("Error reading JSON file: {}".format(str(e)), file=sys.stderr)
        return False
    
    files = data.get('files', [])
    if not files:
        print("No files found in JSON data", file=sys.stderr)
        return False
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    success_count = 0
    for file_data in files:
        try:
            if 'error' in file_data:
                print("Error in source file: {}".format(file_data['error']), file=sys.stderr)
                continue
            
            filename = file_data['filename']
            expected_sha256 = file_data['sha256']
            b64_content = file_data['content_b64']
            
            # Clean base64 content: remove whitespace, newlines, and invalid chars
            b64_clean = ''.join(b64_content.split())
            # Ensure proper padding
            padding = len(b64_clean) % 4
            if padding:
                b64_clean += '=' * (4 - padding)
            
            content = base64.b64decode(b64_clean)
            
            actual_sha256 = hashlib.sha256(content).hexdigest()
            if actual_sha256 != expected_sha256:
                print("SHA256 mismatch for {}: expected {}, got {}".format(
                    filename, expected_sha256, actual_sha256), file=sys.stderr)
                continue
            
            output_path = os.path.join(output_dir, filename)
            with open(output_path, 'wb') as f:
                f.write(content)
            
            print("Decoded: {}".format(output_path))
            success_count += 1
            
        except Exception as e:
            print("Error decoding {}: {}".format(file_data.get('filename', 'unknown'), str(e)), file=sys.stderr)
    
    print("Successfully decoded {} of {} files".format(success_count, len(files)))
    return success_count > 0

def main():
    parser = argparse.ArgumentParser(description='B64Courier - File transfer via base64 JSON for TTY')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Encode command
    encode_parser = subparsers.add_parser('encode', help='Encode files to JSON')
    encode_parser.add_argument('path', help='Directory path to search')
    encode_parser.add_argument('patterns', nargs='+', help='File patterns (supports wildcards)')
    encode_parser.add_argument('-o', '--output', help='Output JSON file (default: stdout)')
    
    # Decode command
    decode_parser = subparsers.add_parser('decode', help='Decode JSON back to files')
    decode_parser.add_argument('json_file', help='Input JSON file')
    decode_parser.add_argument('-o', '--output-dir', default='.', help='Output directory (default: current)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'encode':
        success = encode_files(args.path, args.patterns, args.output)
    elif args.command == 'decode':
        success = decode_files(args.json_file, args.output_dir)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
