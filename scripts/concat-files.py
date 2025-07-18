#!/usr/bin/env python3
import os
import argparse

def combine_files(input_files, output_file, start_sep, end_sep):
    """
    Combine predefined text files into one, adding separators around each file's content.
    """
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for file_path in input_files:
            display_name = os.path.basename(file_path)
            outfile.write(f"{start_sep} {display_name}\n")
            with open(file_path, 'r', encoding='utf-8') as infile:
                outfile.write(infile.read())
            outfile.write(f"\n{end_sep} {display_name}\n\n")

def main():
    # === CONFIGURE YOUR INPUTS HERE ===
    # List exactly the files to combine:
    input_files = [
        "../0-request.txt",
        "../1-resume.txt",
        "../2-not-know.txt",
        "../3-first-word.txt",
        "../4-cover-letter.txt",
        "../5-vacancy.txt",
    ]
    # ==================================

    parser = argparse.ArgumentParser(
        description="Combine predefined text files into one with separators."
    )
    parser.add_argument(
        '-o', '--output',
        default='../combined-request.txt',
        help="Output filename (default: ../combined-request.txt)"
    )
    parser.add_argument(
        '--start-sep',
        default='<<<FILE_START>>>',
        help="Marker before each file (default: <<<FILE_START>>>)"
    )
    parser.add_argument(
        '--end-sep',
        default='<<<FILE_END>>>',
        help="Marker after each file (default: <<<FILE_END>>>)"
    )
    args = parser.parse_args()

    # Ensure all input files actually exist
    missing = [f for f in input_files if not os.path.isfile(f)]
    if missing:
        print("Error: the following input files are missing:")
        for m in missing:
            print(f"  - {m}")
        exit(1)

    combine_files(
        input_files=input_files,
        output_file=args.output,
        start_sep=args.start_sep,
        end_sep=args.end_sep
    )
    print(f"Successfully created {args.output} from {len(input_files)} files.")

if __name__ == "__main__":
    main()
