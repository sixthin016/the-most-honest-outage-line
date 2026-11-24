#!/usr/bin/env python3
"""The Most Honest Outage Line.

Writes one line to ``entry.txt``: a status-page message during a
total outage, written in first person, plain about what is down and
honest about what is not yet known. "Everything is down" names the
whole outage in three words. "I do not know why yet, and I will not
pretend otherwise" refuses the usual spin -- no "some users", no
"degraded performance", no cause invented to fill the silence. "We
are looking, and I will update this page the moment I know more" is
the only promise made, and it is one the author can keep. The entry
is the status message itself -- no title, no explanation outside it.

The program is deliberately boring: standard library only, no network,
no randomness, no model calls. It checks the line against the
competition gate (UTF-8, one line, at most 160 characters) and writes
exactly those bytes, with no trailing newline, so the byte count the
judge's tie-break reads is the line itself.

Output destination, in order:
  1. the first command-line argument, when given;
  2. ``$MAKEFUN_OUTPUT_DIR/entry.txt`` when the variable is set;
  3. ``/output/entry.txt``.
"""

import os
import sys

# The status message: everything down, cause unknown and admitted,
# one promise kept.
LINE = (
    "Everything is down. I do not know why yet, and I will not "
    "pretend otherwise. We are looking, and I will update this page "
    "the moment I know more."
)

MAX_CHARS = 160
MIN_CHARS = 1
DEFAULT_PATH = "/output/entry.txt"
FILE_NAME = "entry.txt"


def validate(line):
    """Check *line* against the competition gate; return problems."""
    problems = []
    if not isinstance(line, str):
        return ["entry is not text"]
    if len(line) < MIN_CHARS:
        problems.append("entry is empty")
    if len(line) > MAX_CHARS:
        problems.append(
            "entry is %d characters, over the %d-character limit"
            % (len(line), MAX_CHARS)
        )
    if line.strip() == "":
        problems.append("entry is only whitespace")
    # Honest, no spin: the status message must not hide behind the
    # usual hedges ("some users", "degraded performance").
    for hedge in ("some users", "degraded performance"):
        if hedge in line.lower():
            problems.append("entry hides behind %r" % hedge)
    if "\n" in line or "\r" in line:
        problems.append("entry spans more than one line")
    try:
        line.encode("utf-8")
    except UnicodeEncodeError:
        problems.append("entry is not valid UTF-8")
    return problems


def destination(argv):
    """Resolve the output path from argv, the environment, or the default."""
    if len(argv) > 1 and argv[1]:
        return argv[1]
    env_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env_dir:
        return os.path.join(env_dir, FILE_NAME)
    return DEFAULT_PATH


def save(path, line):
    """Write *line* as exact UTF-8 bytes (no trailing newline)."""
    problems = validate(line)
    if problems:
        for problem in problems:
            print("error: " + problem, file=sys.stderr)
        return 1
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    data = line.encode("utf-8")
    with open(path, "wb") as handle:
        handle.write(data)
    print(line)
    print("wrote %d bytes to %s" % (len(data), path))
    return 0


def main(argv):
    return save(destination(argv), LINE)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
