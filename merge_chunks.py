#post-processing script. will merge into pdf_extractor\text_extractor.py's logic in a future commit
#!/usr/bin/env python3
import sys
import re
import textwrap
import argparse
from pathlib import Path

def merge_with_overlap(paths, max_check=500):
    """
    Read each file in sorted order, detect and strip overlapping
    text between the end of the accumulated text and the start of
    the new chunk.
    """
    merged = ""
    for p in sorted(paths):
        text = p.read_text(encoding='utf-8', errors='ignore')
        if not merged:
            merged = text
            continue

        tail = merged[-max_check:]
        head = text[:max_check]

        # find longest overlap
        for i in range(len(head), 0, -1):
            if tail.endswith(head[:i]):
                text = text[i:]
                break

        merged += text

    return merged

def trim_hyphens(text):
    """
    1) Remove hyphens (“-”) or PDF “¬” at end-of-line, joining broken words.
    2) Remove any leftover “¬” plus following spaces.
    """
    # join broken words
    text = re.sub(r'[-¬]\n', '', text)
    # strip stray PDF continuation marks
    return re.sub(r'¬\s*', '', text)

def add_header_spacing(text: str) -> str:
    """
    Ensure each `--- Page N ---` marker is followed by a blank line,
    so paragraph reflow treats it as its own paragraph.
    """
    # Match flexible page headers (e.g. '--' or '---') and an optional
    # newline, and replace it with the header and a double newline.
    # This correctly separates headers from text on the same line and
    # ensures a proper paragraph break for reflow.
    return re.sub(
        r'^(--- Page \d+ --+)(\r?\n)?',
        r'\1\n\n',
        text,
        flags=re.MULTILINE
    )


def reflow_paragraphs(text, width=9999):
    """
    Split on blank lines, collapse each paragraph's internal
    whitespace to single spaces, then join lines to the given width.
    """
    paras = re.split(r'\n\s*\n', text.strip())
    out = []
    for p in paras:
        single = ' '.join(p.split())
        out.append(textwrap.fill(single, width=width))
    return "\n\n".join(out)

def main():
    parser = argparse.ArgumentParser(
        description="Merge text chunks with overlap detection, hyphen-trim, and paragraph reflow"
    )
    parser.add_argument(
        'files', nargs='+',
        help="Input text chunk files (e.g. part*.txt)"
    )
    parser.add_argument(
        '--max-check', type=int, default=500,
        help="Max chars to check for overlap (default: 500)"
    )
    parser.add_argument(
        '--width', type=int, default=9999,
        help="Reflow width for paragraphs (default: 9999)"
    )
    parser.add_argument(
        '-o', '--output', type=Path,
        help="Write result to this file (default: stdout)"
    )
    args = parser.parse_args()

    paths   = [Path(f) for f in args.files]
    merged  = merge_with_overlap(paths, max_check=args.max_check)
    trimmed = trim_hyphens(merged)
    spaced  = add_header_spacing(trimmed)
    final   = reflow_paragraphs(spaced, width=args.width)

    if args.output:
        args.output.write_text(final, encoding='utf-8')
    else:
        # write UTF-8 bytes directly to avoid Windows CP1252 errors
        sys.stdout.buffer.write(final.encode('utf-8'))

if __name__ == "__main__":
    main()
