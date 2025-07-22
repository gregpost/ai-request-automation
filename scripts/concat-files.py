#!/usr/bin/env python3

"""
Combines text files into one file with separators.
Useful for preparing structured multi-part input for AI prompts.

Usage:
  python concat-files.py path1 [path2 ...] [-o output.txt]

Examples:
  # FILES:
  # "-o" key is optional to set output file name
  python concat-files.py file1.txt file2.txt -o combined.txt

  # DIRECTORY:
  python concat-files.py day-plan

Output format:
------------------------------------------------------------------------------
<<<FILE_START>>> file-1.txt
(content)
<<<FILE_END>>> file-1.txt

<<<FILE_START>>> file-2.txt
(content)
<<<FILE_END>>> file-2.xt
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
        nargs='*',
        help="Files or single folder name"
    )
    parser.add_argument(
        '-o', '--output',
        default='combined-request.txt',
        help="Output filename (default: combined-request.txt)"
    )
    args = parser.parse_args()

    if not args.paths:
        print("Error: no input paths provided (files or directory)")
        sys.exit(1)

    if len(args.paths) == 1 and '.' not in args.paths[0] and os.path.isdir(args.paths[0]):
        input_files = get_files_from_folder(args.paths[0])
    else:
        input_files = args.paths

    # check file existence
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
