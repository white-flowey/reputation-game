import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from itertools import islice

def launch_parallel(tasks: list, task_fn) -> list:
    n_cores = multiprocessing.cpu_count()
    batch_size = max(1, len(tasks) // n_cores)
    batches = batch_tasks(tasks, batch_size)
    
    return run_parallel(batches, task_fn, n_cores)

def batch_tasks(tasks: list, batch_size: int) -> list[list]:
    it = iter(tasks)
    return [list(islice(it, batch_size)) for _ in range(0, len(tasks), batch_size)]

def run_parallel(batches, task_fn, n_cores):
    with ProcessPoolExecutor(max_workers=n_cores) as executor:
        results = list(executor.map(process_batch, batches, [task_fn]*len(batches)))
    
    return [item for sublist in results for item in sublist]

def process_batch(batch: list, task_fn) -> list:
    return [task_fn(item) for item in batch]
