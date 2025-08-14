#!/usr/bin/env python3

"""
Combines text files into one file with separators.
Useful for preparing structured multi-part input for AI prompts.

Usage:
  python concat-files.py -p path1 [path2 ...] [-o output.txt] [-r request.txt] [-w work.txt]
    - Combine specified files and/or all files in specified directories.
      Optionally prepend contents of request.txt (default 'request.txt') wrapped
      with <<<REQUEST_START>>> and <<<REQUEST_END>>> delimiters.

  python concat-files.py -c codes-list.txt [-m codes.txt] [-o output.txt] [-r request.txt] [-w work.txt]
    - Read a list of codes from 'codes-list.txt', map them to file paths using
      a codes mapping file (default 'codes.txt' or specified by -m),
      then combine those files.
      Optionally prepend contents of request.txt (default 'request.txt' if -r used without argument) wrapped
      with <<<REQUEST_START>>> and <<<REQUEST_END>>> delimiters.

Input files are included with start/end delimiters in the output file.
"""

import os
import argparse
import sys

START_SEP = "<<<FILE_START>>>"
END_SEP = "<<<FILE_END>>>"
REQUEST_START_SEP = "<<<REQUEST_START>>>"
REQUEST_END_SEP = "<<<REQUEST_END>>>"

DEFAULT_CODES_MAPPING_FILE = "codes.txt"
DEFAULT_REQUEST_FILE = "request.txt"
DEFAULT_OUTPUT_FILE = "OUTPUT.txt"
DEFAULT_WORK_FILE = "work.txt"

def combine_files(input_files, output_file, request_file_path=None):
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Write request file content at the top wrapped with delimiters, if exists
        if request_file_path and os.path.isfile(request_file_path):
            outfile.write(f"{REQUEST_START_SEP}\n")
            with open(request_file_path, 'r', encoding='utf-8') as rf:
                outfile.write(rf.read())
            outfile.write(f"\n{REQUEST_END_SEP}\n\n")

        # Then write all input files with delimiters
        for file_path in input_files:
            display_name = os.path.basename(file_path)
            outfile.write(f"{START_SEP} {display_name}\n")
            if os.path.isfile(file_path):
                with open(file_path, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())
            else:
                outfile.write(f"[Warning: file '{file_path}' not found]\n")
            outfile.write(f"\n{END_SEP} {display_name}\n\n")

def get_files_from_folder(folder_path):
    """Return sorted list of file paths in a folder."""
    return [
        os.path.join(folder_path, f)
        for f in sorted(os.listdir(folder_path))
        if os.path.isfile(os.path.join(folder_path, f))
    ]

def read_codes_mapping(mapping_file):
    """Read codes mapping file and return dict code -> filepath"""
    mapping = {}
    with open(mapping_file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(None, 1)
            if len(parts) == 2:
                code, path = parts
                mapping[code] = path
    return mapping

def read_codes_list(codes_list_file):
    """Read codes from the given file, one code per line"""
    codes = []
    with open(codes_list_file, 'r', encoding='utf-8') as f:
        for line in f:
            code = line.strip()
            if code:
                codes.append(code)
    return codes

def read_work_dirs(work_file):
    """Read root directories from a work.txt file"""
    dirs = []
    if os.path.isfile(work_file):
        with open(work_file, 'r', encoding='utf-8') as f:
            for line in f:
                d = line.strip()
                if d and os.path.isdir(d):
                    dirs.append(os.path.abspath(d))
    return dirs

def resolve_file_paths(input_paths, base_dirs):
    """
    Resolve a list of file paths against base directories.
    If a path has no extension, also try adding '.txt'.
    """
    resolved = []
    for p in input_paths:
        if os.path.isabs(p) and os.path.isfile(p):
            resolved.append(p)
            continue

        found = None
        for base_dir in base_dirs:
            candidate = os.path.abspath(os.path.join(base_dir, p))
            # Try as-is
            if os.path.isfile(candidate):
                found = candidate
                break
            # Try with .txt if no extension
            if not os.path.splitext(p)[1]:
                candidate_txt = candidate + ".txt"
                if os.path.isfile(candidate_txt):
                    found = candidate_txt
                    break

        # fallback: keep absolute path (with .txt if possible)
        if found is None:
            abs_path = os.path.abspath(p)
            if not os.path.splitext(p)[1] and os.path.isfile(abs_path + ".txt"):
                found = abs_path + ".txt"
            else:
                found = abs_path
        resolved.append(found)
    return resolved

def main():
    parser = argparse.ArgumentParser(
        description="Combine text files into one with hardcoded separators."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-p', '--paths',
        nargs='+',
        help="Files and/or directory paths"
    )
    group.add_argument(
        '-c', '--codes',
        help="File containing list of codes to map to file paths via codes mapping file"
    )
    parser.add_argument(
        '-m', '--mapping',
        default=None,
        help=f"Codes mapping file (default: search for '{DEFAULT_CODES_MAPPING_FILE}')"
    )
    parser.add_argument(
        '-o', '--output',
        default=DEFAULT_OUTPUT_FILE,
        help=f"Output filename (default: {DEFAULT_OUTPUT_FILE})"
    )
    parser.add_argument(
        '-r', '--request',
        nargs='?',
        const=DEFAULT_REQUEST_FILE,
        default=None,
        help="Request file to prepend wrapped with <<<REQUEST_START>>> and <<<REQUEST_END>>> delimiters (default: 'request.txt' if -r used without argument)"
    )
    parser.add_argument(
        '-w', '--work',
        default=DEFAULT_WORK_FILE,
        help=f"File containing list of root directories to search input files (default: {DEFAULT_WORK_FILE})"
    )
    args = parser.parse_args()

    # Read work directories
    work_dirs = read_work_dirs(args.work)
    if not work_dirs:
        print(f"Warning: No valid directories found in '{args.work}', using current directory only.")
        work_dirs = [os.getcwd()]

    if args.codes:
        # Resolve codes list file using work dirs
        codes_list_path = resolve_file_paths([args.codes], base_dirs=work_dirs)[0]
        if not os.path.isfile(codes_list_path):
            print(f"Error: codes list file '{args.codes}' not found in work directories.")
            sys.exit(1)
        codes = read_codes_list(codes_list_path)

        # Resolve mapping file using work dirs
        mapping_file = args.mapping or DEFAULT_CODES_MAPPING_FILE
        mapping_path = resolve_file_paths([mapping_file], base_dirs=work_dirs)[0]
        if not os.path.isfile(mapping_path):
            print(f"Error: mapping file '{mapping_file}' not found in work directories.")
            sys.exit(1)
        mapping = read_codes_mapping(mapping_path)

        # Resolve input files from codes
        input_files_raw = []
        missing_codes = []
        for code in codes:
            if code in mapping:
                input_files_raw.append(mapping[code])
            else:
                missing_codes.append(code)
        if missing_codes:
            print("Error: the following codes are missing in the mapping file:")
            for c in missing_codes:
                print(f"  - {c}")
            sys.exit(1)

        input_files = resolve_file_paths(input_files_raw, base_dirs=work_dirs)

    elif args.paths:
        input_files_raw = []
        for p in args.paths:
            if os.path.isdir(p):
                input_files_raw.extend(get_files_from_folder(p))
            else:
                input_files_raw.append(p)
        input_files = resolve_file_paths(input_files_raw, base_dirs=work_dirs)

    # Determine request file path if -r used
    request_file_path = None
    if args.request:
        found = resolve_file_paths([args.request], base_dirs=work_dirs)[0]
        if os.path.isfile(found):
            request_file_path = found
        else:
            print(f"Warning: request file '{args.request}' not found, skipping it.")

    # Output file path in script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, args.output)

    combine_files(input_files, output_path, request_file_path=request_file_path)
    print(f"Successfully created {output_path} from {len(input_files)} files.")

if __name__ == "__main__":
    main()
