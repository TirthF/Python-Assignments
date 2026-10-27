"""
Multi-Threaded Job Scheduler Implementation
"""
import threading
import heapq

class Job:
    def __init__(self, arrival, job_id, priority, duration, resources, order):
        self.arrival = arrival
        self.job_id = job_id
        self.priority = priority
        self.duration = duration
        self.resources = resources
        self.order = order

    def __lt__(self, other):
        if self.priority != other.priority:
            return self.priority > other.priority
        return self.order < other.order


def get_w_n_input():
    """Helper function to get workers and number of jobs securely."""
    while True:
        try:
            line = input("Enter number of workers (w) and number of jobs (n): ").strip()
            w, n = map(int, line.split())
            if w <= 0 or n < 0:
                print("Error: Workers must be > 0 and jobs cannot be negative.")
                continue
            return w, n
        except ValueError:
            print("Error: Please enter exactly two integers.")


def get_jobs_input(n):
    """Helper function to read job details."""
    jobs = []
    if n > 0:
        print(f"Enter the {n} jobs (arrival job_id priority duration resources):")
        
    for i in range(n):
        while True:
            try:
                line = input(f"Job {i+1}: ").strip()
                arrival, job_id, priority, duration, resources = line.split()
                
                job = Job(
                    int(arrival),
                    job_id,
                    int(priority),
                    int(duration),
                    int(resources),
                    i
                )
                jobs.append(job)
                break
            except ValueError:
                print("Error: Invalid job format. Please try again.")
    return jobs


def main():
    w, n = get_w_n_input()
    jobs = get_jobs_input(n)

    # 1. Sort jobs by arrival time
    jobs.sort(key=lambda x: x.arrival)

    workers = [0] * w
    worker_lock = threading.Lock()
    results = []
    waiting_times = []


    def execute_job(job, worker_id, start_time):
        """Thread worker function to execute a job."""
        finish_time = start_time + job.duration

        with worker_lock:
            results.append(
                (job.job_id, worker_id, start_time, finish_time)
            )
            waiting_times.append(start_time - job.arrival)

        return finish_time

    # 2. Schedule jobs
    current_time = 0
    index = 0
    queue = []

    while index < n or queue:

        # Fast forward time if no jobs are in queue and workers are idle
        if not queue and index < n:
            current_time = max(current_time, jobs[index].arrival)

        # Add newly arrived jobs to the queue
        while index < n and jobs[index].arrival <= current_time:
            heapq.heappush(queue, jobs[index])
            index += 1

        available_workers = []

        # Find workers that are free at current_time
        for i in range(w):
            if workers[i] <= current_time:
                available_workers.append(i)

        # Assign queued jobs to available workers
        while queue and available_workers:
            job = heapq.heappop(queue)
            worker_id = available_workers.pop(0)

            start_time = max(current_time, workers[worker_id])

            thread = threading.Thread(
                target=execute_job,
                args=(job, worker_id + 1, start_time)
            )

            thread.start()
            thread.join()

            workers[worker_id] = start_time + job.duration

        # Advance current time to the earliest worker becoming free or next job arrival
        if queue:
            current_time = min(workers)
        elif index < n:
            current_time = max(current_time, jobs[index].arrival)

    # 3. Output results
    results.sort(key=lambda x: x[2])

    print("\n--- Execution Results ---")
    for job_id, worker_id, start, finish in results:
        print(job_id, "W" + str(worker_id), start, finish)

    if waiting_times:
        average_wait = sum(waiting_times) / len(waiting_times)
    else:
        average_wait = 0

    print("AVG_WAIT", f"{average_wait:.2f}")

if __name__ == "__main__":
    main()
