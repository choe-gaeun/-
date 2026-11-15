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
  
def run_fifo(refs, frames_count):
  frames = []
  page_faults = 0
  history = []
  for page in refs:
    if page in frames:
      history.append(
      
