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

def print_page_result(algo_name, references, frames_count, page_faults, note):
    print(f"\n==================== [{algo_name}] (프레임 수: {frames_count}) ====================")
    frame_headers = " | ".join([f"F{i+1}" for i in range(frames_count)])
    print(f"{'참조':<4} | {frame_headers} | 상태")
    print("-" * (18 + frames_count * 5))

    for page, frames, status in note:
        padded = [f"{frames[i]:<2}" if i < len(frames) else "- " for i in range(frames_count)]
        frames_str = " | ".join(padded)
        print(f"{page:<4} | {frames_str} | {status}")

    total_refs = len(references)
    fault_rate = (page_faults / total_refs) * 100
    print("-" * (18 + frames_count * 5))
    print(f"총 참조 수: {total_refs} | 페이지 부재(F): {page_faults}회 | 부재율: {fault_rate:.1f}%")


def print_page_summary(results, total_refs):
    print("\n==================== [Part B 요약 비교표] ====================")
    print(f"{'알고리즘':<10} | {'부재 횟수(F)':<12} | {'부재율(%)':<10}")
    print("-" * 40)
    for algo_name, faults in results:
        rate = (faults / total_refs) * 100
        print(f"{algo_name:<10} | {faults:<12} | {rate:.1f}%")


def main():
    parser = argparse.ArgumentParser(description="OS Simulator")
    parser.add_argument("--mode", required=True, choices=["sched", "page"])
    parser.add_argument("--algo", default="ALL")
    parser.add_argument("--input")
    parser.add_argument("--slice", type=int, default=4)
    parser.add_argument("--frames", type=int)
    parser.add_argument("--ref")
    parser.add_argument("--ref-file")

    args = parser.parse_args()

    if args.mode == "sched":
        if not args.input:
            print("[Error] --input 파일을 지정해야 합니다.")
            sys.exit(1)
        processes = load_processes(args.input)
        sched_algos = {
            "FCFS": run_fcfs,
            "SJF": run_sjf,
            "SRT": run_srt,
            "RR": lambda procs: run_rr(procs, args.slice),
        }
        algo_upper = args.algo.upper()
        if algo_upper == "ALL":
            targets = ["FCFS", "SJF", "SRT", "RR"]
        elif algo_upper in sched_algos:
            targets = [algo_upper]
        else:
            print(f"[Error] 지원하지 않는 알고리즘입니다: {args.algo}")
            sys.exit(1)

        summary = []
        for name in targets:
            res, gantt = sched_algos[name](processes)
            print_sched_result(name, res, gantt)
            summary.append((name, res))

        if len(targets) > 1:
            print_sched_summary(summary)

    elif args.mode == "page":
        if not args.frames or args.frames <= 0:
            print("[Error] --frames는 1 이상의 정수여야 합니다.")
            sys.exit(1)

        if args.ref:
            references = parse_refs(args.ref)
        elif args.ref_file:
            references = load_refs_from_file(args.ref_file)
        else:
            print("[Error] --ref 또는 --ref-file 중 하나를 입력해야 합니다.")
            sys.exit(1)

        page_algos = {
            "FIFO": run_fifo,
            "LRU": run_lru,
            "OPT": run_opt,
        }

        algo_upper = args.algo.upper()
        if algo_upper == "ALL":
            targets = ["FIFO", "LRU", "OPT"]
        elif algo_upper in page_algos:
            targets = [algo_upper]
        else:
            print(f"[Error] 지원하지 않는 알고리즘입니다: {args.algo}")
            sys.exit(1)

        summary = []
        for name in targets:
            faults, note = page_algos[name](references, args.frames)
            print_page_result(name, references, args.frames, faults, note)
            summary.append((name, faults))

        if len(targets) > 1:
            print_page_summary(summary, len(references))


if __name__ == "__main__":
    main()
