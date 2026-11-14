from collection import deque
processes = []
with open("sched_basic.txt", "r", encoding="utf-8") as A:
  for line in A:
    line = line.strip()
    if not line or line.startswith("#"):
      continue
    fields = line.split(",")
    pid = fields[0].strip()
    arrive = int(fields[1].strip())
    burst = int(fields[2].strip())
    processes.append((pid, arrive, burst))
print(processes)
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
  completed_procs = []
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
        gantt.append(('idle', current_time, remaining_jobs[0][1]))
        current_time = remaining_jobs[0][1]
        continue

    ready_queue.sort(key=lambda x: (x[2], x[0]))
    pid, arrive, burst = ready_queue.pop(0)[:3]

    start_time = current_time
    finish_time = start_time + burst
    turnaround_time = finish_time - arrive
    waiting_time = turnaround_time - burst
    response_time = start_time - arrive

    completed_procs.append({
        'pid': pid,
        'arrive': arrive,
        'burst': burst,
        'start': start_time,
        'finish': finish_time,
        'turnaround': turnaround_time,
        'waiting': waiting_time,
        'response': response_time
    })
    gantt.append((pid, start_time, finish_time))
    current_time = finish_time
  return(gantt)
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

        chosen = min(candidates, key=lambda x: (x["rem"], x["pid"]))
        run_time = min(time_slice, chosen["rem"])

        gantt.append((chosen["pid"], current_time, current_time + run_time))
        chosen["rem"] -= run_time
        current_time += run_time

    return gantt
