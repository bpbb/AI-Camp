#!/usr/bin/env python3
"""
Build the student version of this project into ../student/, next to
this solution/ folder.

    python3 scripts/make_student.py

The full (teacher) code is the only source. Parts students write
themselves are marked in it like this:

    // STUDENT-BEGIN
    // TODO(student) 1/4 -- what to do, with hints   <- kept
    // STUDENT-STUB: float left = 0.0f;              <- becomes code
    float left = lin - ang * WHEEL_BASE / 2.0f;      <- removed
    // STUDENT-END

Same with # for Python. Markdown sections between
<!-- TEACHER-ONLY --> and <!-- /TEACHER-ONLY --> are left out.

Fix things in the full code, then run this again; never edit ../student/
by hand, it is overwritten every time.
"""
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent      # solution/
OUT = ROOT.parent / 'student'                      # next to it

# Never copied: build output and this script.
SKIP_DIRS = {'.pio', 'build', 'install', 'log', '__pycache__'}

# Students read the Thai docs: docs-th/ becomes their docs/, and the
# English docs/ (the teacher's) is not copied.
STUDENT_DOCS = 'docs-th'
SKIP_FILES = {'make_student.py'}
SOURCE_EXT = {'.h', '.hpp', '.c', '.cpp', '.py'}

# In Markdown, whole sections can be left out of the student copy:
#   <!-- TEACHER-ONLY --> ... <!-- /TEACHER-ONLY -->
TEACHER_ONLY = re.compile(
    r'^<!-- TEACHER-ONLY -->\n.*?^<!-- /TEACHER-ONLY -->\n', re.S | re.M)

BEGIN = re.compile(r'^\s*(//|#)\s*STUDENT-BEGIN\s*$')
END = re.compile(r'^\s*(//|#)\s*STUDENT-END\s*$')
STUB = re.compile(r'^(\s*)(//|#)\s*STUDENT-STUB:\s?(.*)$')
COMMENT = re.compile(r'^\s*(//|#)')

# The docs here use the teacher's own path; students keep the project
# in their home folder.
TEACHER_PATH = '~/Documents/AI-Camp/solution'
STUDENT_PATH = '~/AI-Camp'

# config.h ships with blanks, not the teacher's WiFi and IP.
CONFIG_BLANKS = {
    'WIFI_SSID': '"MyNetwork"',
    'WIFI_PASSWORD': '"changeme"',
    'ROBOT_ID': '"robot1"',
    'AGENT_IP': '"192.168.1.100"',
    'ROS_DOMAIN_ID': '0',
}


def strip_solutions(text, path):
    out, inside, blocks = [], False, 0
    for n, line in enumerate(text.splitlines(keepends=True), 1):
        if BEGIN.match(line):
            if inside:
                raise SystemExit(f'{path}:{n}: STUDENT-BEGIN inside a block')
            inside, blocks = True, blocks + 1
            continue
        if END.match(line):
            if not inside:
                raise SystemExit(f'{path}:{n}: STUDENT-END without BEGIN')
            inside = False
            continue
        if not inside:
            out.append(line)
            continue
        stub = STUB.match(line)
        if stub:
            out.append(stub.group(1) + stub.group(3).rstrip() + '\n')
        elif COMMENT.match(line) or not line.strip():
            out.append(line)        # hints stay
        # anything else is the solution: dropped
    if inside:
        raise SystemExit(f'{path}: STUDENT-BEGIN never closed')
    return ''.join(out), blocks


def blank_config(text):
    for name, value in CONFIG_BLANKS.items():
        text = re.sub(rf'^(#define\s+{name}\s+)\S+',
                      lambda m: m.group(1) + value, text, flags=re.M)
    return text


def main():
    if OUT.exists():
        shutil.rmtree(OUT)

    total = 0
    for src in sorted(ROOT.rglob('*')):
        rel = src.relative_to(ROOT)
        if rel.parts and rel.parts[0] == 'docs' and (ROOT / STUDENT_DOCS).is_dir():
            continue
        if rel.parts and rel.parts[0] == STUDENT_DOCS:
            rel = Path('docs', *rel.parts[1:])
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if src.is_dir() or src.name in SKIP_FILES:
            continue
        dst = OUT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)

        if src.suffix in SOURCE_EXT:
            text = src.read_text()
            text, blocks = strip_solutions(text, rel)
            if rel.as_posix() == 'firmware/include/config.h':
                text = blank_config(text)
            dst.write_text(text)
            if blocks:
                total += blocks
                print(f'  {rel}: {blocks} to fill in')
        elif src.suffix == '.md':
            text = TEACHER_ONLY.sub('', src.read_text())
            dst.write_text(text.replace(TEACHER_PATH, STUDENT_PATH))
        else:
            shutil.copy2(src, dst)
        shutil.copymode(src, dst)

    # The .gitignore lives one level up, covering solution/ and student/.
    # Students get their own copy for when student/ is their whole repo.
    gitignore = ROOT.parent / '.gitignore'
    if gitignore.exists():
        shutil.copy2(gitignore, OUT / '.gitignore')

    print(f'student version written to {OUT}/ '
          f'({total} parts to fill in)')


if __name__ == '__main__':
    main()
