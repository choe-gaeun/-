import argparse
import sys
from collections import dequeue

def parse_references(raw_text):
  wjdfl = raw_text.replace(","," ").strip()
  if not wjdfl:
    print("[Error] 참조열이 비어있음.")
    sys.exit(1)
  return wjdfl.split() if " " in wjdfl else list(wjdfl)

def load_references_from_file(filename):
  try:
    with open(filename, "r", encoding = "utf-8") as f:
      lines = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
  except FileNotFoundError:
    print(f"[Error] 파일을 찾을 수 없음: {filename}")
    sys.exit(1)
  return parse_references(" ".join(lines))
  
def run_fifo(references, frames_count):
  frames = []
  page_faults = 0
  note = []
  for page in references:
    if page in frames:
      note.append((page, list(frames), "S"))
    else:
      page_faults += 1
      if len(frames) == frames_count :
        frames.pop(0)
      frames.append(page)
      note.append((page, list(frames), "F"))
  return page_faults, note

def run_lru(references, frames_count):
  frames = []
  page_faults = 0
  note = []
  for page in references:
    if page in frames:
      frames.remove(page)
      frames.append(page)
      note.append((page, list(frames), "S"))
    else:
      page_faults += 1
      if len(frames) == frames_count :
        frames.pop(0)
      frames.append(page)
      note.append((page, list(frames), "F"))
  return page_faults, note

def run_opt(references, frames_count):
  frames = []
  page_faults = 0
  note = []
  for i, page in enumerate(references):
    if page in frames:
      note.append((page, list(frames), "S"))
    else:
      page_faults += 1
      if len(frames) == frames_count:
        remaining = references[i+1:]
        naga = frames[0]
        max_dist = -1
        for f in frames:
          if f not in remaining:
            dist = float("inf")
          else:
            dist = remaining.index(f)
          if dist > max_dist:
            max_dist = dist
            naga = f
        frames.remove(naga)
      frames.append(page)
      note.append((page, list(frames), "F"))
  return page_faults, note
      
