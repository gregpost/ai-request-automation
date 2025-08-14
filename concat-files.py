#!/usr/bin/env python3

"""
Combines text files into one file with structured separators.
Useful for preparing structured multi-part input for AI prompts.

Usage:
  python concat-files.py -i work_dir [-o output.txt] [-r request.txt] [-rh "Header content or file"]
  python concat-files.py -p path1 [path2 ...] [-o output.txt] [-r request.txt] [-rh "Header content or file"]
  python concat-files.py -c codes-list.txt [-m codes.txt] [-o output.txt] [-r request.txt] [-w work.txt] [-rh "Header content or file"]

New:
  -e / --error           Adds a note indicating that the request header contains a bottom string indicating an error, not the REQUEST_BODY.
"""


import os

import argparse
import sys

START_SEP = "<<<BLOCK_START>>>"
END_SEP = "<<<BLOCK_END>>>"
REQUEST_START_SEP = "<<<BLOCK_START>>> REQUEST_BODY"
REQUEST_END_SEP = "<<<BLOCK_END>>> REQUEST_BODY"
REQUEST_HEADER_START_SEP = "<<<BLOCK_START>>> REQUEST_HEADER"
REQUEST_HEADER_END_SEP = "<<<BLOCK_END>>> REQUEST_HEADER"

DEFAULT_CODES_MAPPING_FILE = "file-codes.txt"
DEFAULT_OUTPUT_FILE = "OUTPUT.txt"
DEFAULT_WORK_FILE = "work.txt"

ERROR_APPEND_STRING = (
    "The REQUEST_BODY contains console output with the error that needs to be solved.\n"
)

def read_text_from_file_or_string(value):
    if value and os.path.isfile(value):
        with open(value, 'r', encoding='utf-8') as f:
            return f.read()
    return value

def combine_files(input_files, output_file, request_file_path=None, request_header=None, append_error=False):
    with open(output_file, 'w', encoding='utf-8') as outfile:
        if request_header:
            header_content = read_text_from_file_or_string(request_header)
            outfile.write(f"{REQUEST_HEADER_START_SEP}\n")
            outfile.write(f"{header_content}\n")
            if append_error:
                outfile.write(f"\n{ERROR_APPEND_STRING}")
            outfile.write(f"{REQUEST_HEADER_END_SEP}\n\n")
        if request_file_path and os.path.isfile(request_file_path):
            outfile.write(f"{REQUEST_START_SEP}\n")
            with open(request_file_path, 'r', encoding='utf-8') as rf:
                outfile.write(rf.read())
            outfile.write(f"{REQUEST_END_SEP}\n\n")

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
    return [
        os.path.join(folder_path, f)
        for f in sorted(os.listdir(folder_path))
        if os.path.isfile(os.path.join(folder_path, f))
    ]

def read_codes_mapping(mapping_file):
    mapping = {}
    with open(mapping_file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(None, 1)
            if len(parts) == 2:
                code, path = parts
                mapping[code] = path
    return mapping

def read_codes_list(codes_list_file):
    codes = []
    with open(codes_list_file, 'r', encoding='utf-8') as f:
        for line in f:
            code = line.strip()
            if code:
                codes.append(code)
    return codes

def read_work_dirs(work_file):
    dirs = []
    if os.path.isfile(work_file):
        with open(work_file, 'r', encoding='utf-8') as f:
            for line in f:
                d = line.strip()
                if d and os.path.isdir(d):
                    dirs.append(os.path.abspath(d))
    return dirs

def resolve_file_paths(input_paths, base_dirs):
    resolved = []
    for p in input_paths:
        if os.path.isabs(p) and os.path.isfile(p):
            resolved.append(p)
            continue

        found = None
        for base_dir in base_dirs:
            candidate = os.path.abspath(os.path.join(base_dir, p))
            if os.path.isfile(candidate):
                found = candidate
                break
            if not os.path.splitext(p)[1]:
                candidate_txt = candidate + ".txt"
                if os.path.isfile(candidate_txt):
                    found = candidate_txt
                    break

        if found is None:
            abs_path = os.path.abspath(p)
            if not os.path.splitext(p)[1] and os.path.isfile(abs_path + ".txt"):
                found = abs_path + ".txt"
            else:
                found = abs_path
        resolved.append(found)
    return resolved

def find_request_file(initial_request, input_dir, work_dirs):
    if input_dir:
        candidate = os.path.join(input_dir, "request.txt")
        if os.path.isfile(candidate):
            return candidate
    if initial_request:
        found = resolve_file_paths([initial_request], base_dirs=work_dirs)[0]
        if os.path.isfile(found):
            return found
    for d in work_dirs:
        candidate = os.path.join(d, "request.txt")
        if os.path.isfile(candidate):
            return candidate
    return None

def find_work_file(initial_work, input_dir, script_dir):
    if input_dir:
        candidate = os.path.join(input_dir, "work.txt")
        if os.path.isfile(candidate):
            return candidate
    if initial_work and os.path.isfile(initial_work):
        return initial_work
    candidate = os.path.join(script_dir, "work.txt")
    if os.path.isfile(candidate):
        return candidate
    return initial_work

def main():
    parser = argparse.ArgumentParser(
        description="Combine text files into one with structured separators."
    )
    parser.add_argument('-p', '--paths', nargs='+', help="Files and/or directory paths")
    parser.add_argument('-i', '--input-dir', nargs='?', help="Directory with working files: files.txt, header.txt, request")
    parser.add_argument('-c', '--codes', nargs='?', help="File containing list of codes to map to file paths")
    parser.add_argument('-m', '--mapping', default=None, help=f"Codes mapping file (default: {DEFAULT_CODES_MAPPING_FILE})")
    parser.add_argument('-o', '--output', default=DEFAULT_OUTPUT_FILE, help=f"Output filename (default: {DEFAULT_OUTPUT_FILE})")
    parser.add_argument('-r', '--request', nargs='?', const=None, default=None, help="Request file to prepend")
    parser.add_argument('-w', '--work', default=DEFAULT_WORK_FILE, help=f"File containing list of root directories (default: {DEFAULT_WORK_FILE})")
    parser.add_argument('-rh', '--header', default=None, help="Optional request header content or file to prepend")
    parser.add_argument('-e', '--error', action='store_true', help="Append predefined error string to request.txt section")
    args = parser.parse_args()

    work_dirs = []
    input_dir_abs = None
    if args.input_dir:
        input_dir_abs = os.path.abspath(args.input_dir)
        if os.path.isdir(input_dir_abs):
            args.codes = os.path.join(input_dir_abs, "files.txt")
            args.header = os.path.join(input_dir_abs, "header.txt")
        else:
            print(f"Error: input directory '{args.input_dir}' not found.")
            sys.exit(1)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    args.work = find_work_file(args.work, input_dir_abs, script_dir)

    if not args.paths and not args.codes:
        print("Error: You must specify either -p (paths), -i (input-dir), or -c (codes).")
        sys.exit(1)

    work_dirs = read_work_dirs(args.work)
    if not work_dirs:
        print(f"Warning: No valid directories found in '{args.work}', using current directory only.")
        work_dirs = [os.getcwd()]

    request_file_path = find_request_file(args.request, input_dir_abs, work_dirs)
    if not request_file_path:
        print("Warning: No request.txt file found in input-dir or work directories.")

    input_files = []

    if args.codes:
        codes_list_path = resolve_file_paths([args.codes], base_dirs=work_dirs)[0]
        if not os.path.isfile(codes_list_path):
            print(f"Error: codes list file '{args.codes}' not found in work directories.")
            sys.exit(1)
        codes = read_codes_list(codes_list_path)

        mapping_file = args.mapping or DEFAULT_CODES_MAPPING_FILE
        mapping_path = resolve_file_paths([mapping_file], base_dirs=work_dirs)[0]
        if not os.path.isfile(mapping_path):
            print(f"Error: mapping file '{mapping_file}' not found in work directories.")
            sys.exit(1)
        mapping = read_codes_mapping(mapping_path)

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

    output_path = os.path.join(script_dir, args.output)

    combine_files(
        input_files,
        output_path,
        request_file_path=request_file_path,
        request_header=args.header,
        append_error=args.error
    )
    print(f"Successfully created {output_path} from {len(input_files)} files.")

if __name__ == "__main__":
    main()
