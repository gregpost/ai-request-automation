#!/usr/bin/env python3

"""
Combines text files into one file with separators.
Useful for preparing structured multi-part input for AI prompts.

Usage:
  python concat-files.py path1 [path2 ...] [-o output.txt]

Examples:
  # Specify multiple files and/or directories (mixed is allowed)
  python concat-files.py file1.txt dir1 file2.txt -o combined.txt

Output format:
------------------------------------------------------------------------------
<<<FILE_START>>> file-1.txt
(content)
<<<FILE_END>>> file-1.txt

<<<FILE_START>>> file-2.txt
(content)
<<<FILE_END>>> file-2.txt
------------------------------------------------------------------------------
"""

import os
import argparse
import sys

START_SEP = "<<<FILE_START>>>"
END_SEP = "<<<FILE_END>>>"

def combine_files(input_files, output_file):
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for file_path in input_files:
            display_name = os.path.basename(file_path)
            outfile.write(f"{START_SEP} {display_name}\n")
            with open(file_path, 'r', encoding='utf-8') as infile:
                outfile.write(infile.read())
            outfile.write(f"\n{END_SEP} {display_name}\n\n")

def get_files_from_folder(folder_path):
    """Return sorted list of file paths in a folder."""
    return [
        os.path.join(folder_path, f)
        for f in sorted(os.listdir(folder_path))
        if os.path.isfile(os.path.join(folder_path, f))
    ]

def main():
    parser = argparse.ArgumentParser(
        description="Combine text files into one with hardcoded separators."
    )
    parser.add_argument(
        'paths',
        nargs='+',
        help="Files and/or directory paths"
    )
    parser.add_argument(
        '-o', '--output',
        default='combined-request.txt',
        help="Output filename (default: combined-request.txt)"
    )
    args = parser.parse_args()

    # Collect all files: expand directories, keep files
    input_files = []
    for p in args.paths:
        if os.path.isdir(p):
            input_files.extend(get_files_from_folder(p))
        else:
            input_files.append(p)

    if not input_files:
        print("Error: no input files found (check your paths)")
        sys.exit(1)

    # Check file existence
    missing = [f for f in input_files if not os.path.isfile(f)]
    if missing:
        print("Error: the following input files are missing:")
        for m in missing:
            print(f"  - {m}")
        sys.exit(1)

    combine_files(input_files, args.output)
    print(f"Successfully created {args.output} from {len(input_files)} files.")

if __name__ == "__main__":
    main()
