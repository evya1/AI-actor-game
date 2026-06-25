---
name: parallel-processing
description: Implement multiprocessing for CPU-bound tasks and multithreading for I/O-bound tasks with thread safety. Use when optimizing performance or processing data in parallel.
---

# Parallel Processing & Performance

Using multiple processors (multiprocessing) and multiple execution threads (multithreading) is essential for optimal performance of modern software.

## Multiprocessing vs Multithreading

### Multiprocessing (CPU-bound)
Use for CPU-intensive operations:
- Mathematical computations
- Image processing
- Model training

Each process runs in separate memory and utilizes a different CPU core.

### Multithreading (I/O-bound)
Use for I/O-bound operations:
- Network calls
- Database access
- File read/write

Threads allow other operations to proceed while waiting for I/O.

## Thread Safety

Thread safety is critical:

- Protect shared variables with locks
- Use `queue.Queue` for passing information between threads
- Avoid deadlocks
- Use context managers for resource management

```python
import threading
from queue import Queue

lock = threading.Lock()
task_queue = Queue()

def safe_operation(shared_data):
    with lock:
        # Protected critical section
        shared_data.update(...)
```

## Parallel Processing Checklist

### 1. Identify Operations
- [ ] Identify I/O-bound vs CPU-bound operations
- [ ] Choose the right tool (multiprocessing vs multithreading)
- [ ] Evaluate the benefit of parallelization

### 2. Implementation
- [ ] Dynamic number of processes/threads
- [ ] Safe data sharing
- [ ] Proper synchronization

### 3. Resource Management
- [ ] Proper cleanup and shutdown
- [ ] Exception handling in worker threads
- [ ] Prevent memory leaks

### 4. Safety
- [ ] Protect shared variables
- [ ] Prevent race conditions
- [ ] Prevent deadlocks
