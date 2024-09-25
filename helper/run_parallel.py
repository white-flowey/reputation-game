from pathos.multiprocessing import ProcessingPool as Pool
from itertools import islice

def launch_parallel(tasks: list, task_fn) -> list:
    """Launch tasks in parallel using multiple cores.

    Args:
        tasks (list): A list of tasks to be processed.
        task_fn: A function that defines the task to be executed on each item.

    Returns:
        list: A list of results from the processed tasks.
    """
    n_cores = int(Pool().ncpus)
    batch_size = max(1, len(tasks) // (n_cores * 2))
    batches = batch_tasks(tasks, batch_size)
    
    return run_parallel(batches, task_fn, n_cores)

def batch_tasks(tasks: list, batch_size: int) -> list[list]:
    """Divide tasks into batches of specified size.

    Args:
        tasks (list): A list of tasks to be batched.
        batch_size (int): The maximum size of each batch.

    Returns:
        list[list]: A list of batches, where each batch is a list of tasks.
    """
    it = iter(tasks)
    return [list(islice(it, batch_size)) for _ in range(0, len(tasks), batch_size)]

def run_parallel(batches: list, task_fn, n_cores: int) -> list:
    """Execute batches of tasks in parallel.

    Args:
        batches (list): A list of batches, each containing tasks.
        task_fn: A function that defines the task to be executed on each item.
        n_cores (int): The number of CPU cores to use for parallel processing.

    Returns:
        list: A flattened list of results from all processed batches.
    """
    with Pool(n_cores) as pool:
        results = pool.map(process_batch, batches, [task_fn] * len(batches))
    return [item for sublist in results for item in sublist]

def process_batch(batch: list, task_fn) -> list:
    """Process a single batch of tasks using the specified function. Feed multiple tasks at once to a core.

    Args:
        batch (list): A list of tasks to be processed in this batch.
        task_fn: A function that defines the task to be executed on each item.

    Returns:
        list: A list of results from processing the batch.
    """
    return [task_fn(item) for item in batch]
