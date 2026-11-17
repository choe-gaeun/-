import argparse
import sys
from collections import deque

def load_processes(filename):
    processes = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                fields = [x.strip() for x in line.split(",")]
                if len(fields) < 3:
                    raise ValueError("항목 개수가 부족함.")
                pid, arrive, burst = fields[0], int(fields[1]), int(fields[2])
                if not pid or arrive < 0 or burst <= 0:
                    raise ValueError("잘못된 값임")
                processes.append((pid, arrive, burst))
    except Exception as e:
        print(f"[Error] 파일 읽기 실패: {e}")
        sys.exit(1)
    if not processes:
        print("[Error] 프로세스 데이터 없음.")
        sys.exit(1)
    return processes

def run_fcfs(list_processes):
    sorted_procs = sorted(list_processes, key=lambda x: (x[1], x[0]))
    current_time = 0
    gantt = []
    for proc in sorted_procs:
        pid, arrive, burst = proc[:3]
        if current_time < arrive:
            gantt.append(("idle", current_time, arrive))
            current_time = arrive
        start_time = current_time
        finish_time = start_time + burst
        gantt.append((pid, start_time, finish_time))
        current_time = finish_time
    return gantt

def run_sjf(list_processes):
    sorted_procs = sorted(list_processes, key=lambda x: (x[1], x[0]))
    current_time = 0
    ready_queue = []
    gantt = []
    remaining_jobs = list(sorted_procs)
    while remaining_jobs or ready_queue:
        arrived = [job for job in remaining_jobs if job[1] <= current_time]
        for job in arrived:
            ready_queue.append(job)
            remaining_jobs.remove(job)

        if not ready_queue:
            if remaining_jobs:
                gantt.append(("idle", current_time, remaining_jobs[0][1]))
                current_time = remaining_jobs[0][1]
                continue

        ready_queue.sort(key=lambda x: (x[2], x[0]))
        pid, arrive, burst = ready_queue.pop(0)[:3]

        start_time = current_time
        finish_time = start_time + burst
        gantt.append((pid, start_time, finish_time))
        current_time = finish_time
    return gantt

def run_srt(list_processes, time_slice=10):
    tasks = []
    for proc in list_processes:
        pid, arrive, burst = proc[:3]
        tasks.append({"pid": pid, "arrive": arrive, "burst": burst, "rem": burst})
    tasks.sort(key=lambda x: (x["arrive"], x["pid"]))
    current_time = 0
    gantt = []
    while any(t["rem"] > 0 for t in tasks):
        candidates = [t for t in tasks if t["arrive"] <= current_time and t["rem"] > 0]
        if not candidates:
            next_arrive = min(t["arrive"] for t in tasks if t["rem"] > 0)
            gantt.append(("idle", current_time, next_arrive))
            current_time = next_arrive
            continue
        decision = min(candidates, key=lambda x: (x["rem"], x["pid"]))
        run_time = min(time_slice, decision["rem"])
        gantt.append((decision["pid"], current_time, current_time + run_time))
        decision["rem"] -= run_time
        current_time += run_time
    return gantt

def run_rr(list_processes, time_slice=10):
    tasks = []
    for proc in list_processes:
        pid, arrive, burst = proc[:3]
        tasks.append({"pid": pid, "arrive": arrive, "burst": burst, "rem": burst})
    tasks.sort(key=lambda x: (x["arrive"], x["pid"]))
    current_time = 0
    gantt = []
    ready_queue = deque()
    idx = 0
    n = len(tasks)
    while idx < n or ready_queue:
        if not ready_queue:
            if current_time < tasks[idx]["arrive"]:
                gantt.append(("idle", current_time, tasks[idx]["arrive"]))
                current_time = tasks[idx]["arrive"]
            while idx < n and tasks[idx]["arrive"] <= current_time:
                ready_queue.append(tasks[idx])
                idx += 1
        decision = ready_queue.popleft()
        run_time = min(time_slice, decision["rem"])
        gantt.append((decision["pid"], current_time, current_time + run_time))
        decision["rem"] -= run_time
        current_time += run_time
        while idx < n and tasks[idx]["arrive"] <= current_time:
            ready_queue.append(tasks[idx])
            idx += 1
        if decision["rem"] > 0:
            ready_queue.append(decision)
    return gantt

def print_scheduling_results(algo_name, list_processes, gantt, time_slice=None):
    gantt_str = "".join(f"|{pid}({start}-{end})" for pid, start, end in gantt) + "|"

    first_start = {}
    finish = {}
    for pid, start, end in gantt:
        if pid == "idle":
            continue
        if pid not in first_start:
            first_start[pid] = start
        finish[pid] = end

    results = []
    for proc in sorted(list_processes, key=lambda x: x[0]):
        pid, arrive, burst = proc[:3]
        turnaround = finish[pid] - arrive
        waiting = turnaround - burst
        response = first_start[pid] - arrive

        results.append({
            "pid": pid,
            "arrive": arrive,
            "burst": burst,
            "waiting": waiting,
            "turnaround": turnaround,
            "response": response,
        })

    total_time = gantt[-1][2] if gantt else 0
    idle_time = sum(end - start for pid, start, end in gantt if pid == "idle")
    if total_time > 0:
        cpu_util = ((total_time - idle_time) / total_time) * 100
    else:
        cpu_util = 0.0

    active_pids = [pid for pid, _, _ in gantt if pid != "idle"]
    context_switches = 0
    for i in range(1, len(active_pids)):
        if active_pids[i] != active_pids[i - 1]:
            context_switches += 1

    if time_slice is not None:
        print(f"=== [{algo_name}] (time_slice={time_slice}) ===")
    else:
        print(f"=== [{algo_name}] ===")

    print(f"Gantt: {gantt_str}\n")
    print(f"{'PID':<6}{'Arrive':>8}{'Burst':>8}{'Waiting':>10}{'Turnaround':>12}{'Response':>10}")
    print("-" * 54)
    for r in results:
        print(f"{r['pid']:<6}{r['arrive']:>8}{r['burst']:>8}{r['waiting']:>10}{r['turnaround']:>12}{r['response']:>10}")

    n = len(results)
    avg_wait = sum(r["waiting"] for r in results) / n
    avg_turn = sum(r["turnaround"] for r in results) / n
    avg_resp = sum(r["response"] for r in results) / n
    throughput = n / total_time if total_time > 0 else 0.0

    print("-" * 54)
    print(f"Average Waiting Time   : {avg_wait:.2f}")
    print(f"Average Turnaround Time: {avg_turn:.2f}")
    print(f"Average Response Time  : {avg_resp:.2f}")
    print(f"CPU Utilization        : {cpu_util:.2f}%")
    print(f"Throughput             : {throughput:.4f} processes/unit time")
    print(f"Context Switches       : {context_switches}\n")

    return {
        "algo": algo_name,
        "avg_wait": avg_wait,
        "avg_turn": avg_turn,
        "avg_resp": avg_resp,
        "cpu_util": cpu_util,
        "throughput": throughput,
        "cs": context_switches,
    }

def print_summary_table(summary_list):
    print("=== [SUMMARY COMPARISON] ===")
    print(f"{'Algorithm':<10}{'Avg Wait':>10}{'Avg Turn':>10}{'Avg Resp':>10}{'CPU(%)':>10}{'Throughput':>12}{'CS':>6}")
    print("-" * 68)
    for s in summary_list:
        print(
            f"{s['algo']:<10}{s['avg_wait']:>10.2f}{s['avg_turn']:>10.2f}"
            f"{s['avg_resp']:>10.2f}{s['cpu_util']:>10.2f}{s['throughput']:>12.4f}{s['cs']:>6}"
        )
    print()

def parse_references(raw_text):
    wjdfl = raw_text.replace(",", " ").strip()
    if not wjdfl:
        print("[Error] 참조열이 비어있음.")
        sys.exit(1)
    return wjdfl.split() if " " in wjdfl else list(wjdfl)

def load_references_from_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
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
            if len(frames) == frames_count:
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
            if len(frames) == frames_count:
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
                remaining = references[i + 1:]
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
    parser.add_argument("--slice", type=int, default=10)
    parser.add_argument("--frames", type=int)
    parser.add_argument("--ref")
    parser.add_argument("--ref-file")

    args = parser.parse_args()

    if args.mode == "sched":
        if not args.input:
            print("[Error] --input 파일을 지정해야 합니다.")
            sys.exit(1)
        if args.slice <= 0:
            print("[Error] --slice 값은 1 이상의 정수여야 합니다.")
            sys.exit(1)

        processes = load_processes(args.input)
        algo = args.algo.upper()

        if algo == "FCFS":
            print_scheduling_results("FCFS", processes, run_fcfs(processes))
        elif algo == "SJF":
            print_scheduling_results("SJF", processes, run_sjf(processes))
        elif algo == "SRT":
            print_scheduling_results("SRT", processes, run_srt(processes, args.slice), args.slice)
        elif algo == "RR":
            print_scheduling_results("RR", processes, run_rr(processes, args.slice), args.slice)
        elif algo == "ALL":
            summaries = [
                print_scheduling_results("FCFS", processes, run_fcfs(processes)),
                print_scheduling_results("SJF", processes, run_sjf(processes)),
                print_scheduling_results("SRT", processes, run_srt(processes, args.slice), args.slice),
                print_scheduling_results("RR", processes, run_rr(processes, args.slice), args.slice),
            ]
            print_summary_table(summaries)
        else:
            print(f"[Error] 지원하지 않는 스케줄링 알고리즘입니다: {args.algo}")
            sys.exit(1)

    elif args.mode == "page":
        if not args.frames or args.frames <= 0:
            print("[Error] --frames는 1 이상의 정수여야 합니다.")
            sys.exit(1)

        if args.ref:
            references = parse_references(args.ref)
        elif args.ref_file:
            references = load_references_from_file(args.ref_file)
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
            print(f"[Error] 지원하지 않는 페이지 교체 알고리즘입니다: {args.algo}")
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
