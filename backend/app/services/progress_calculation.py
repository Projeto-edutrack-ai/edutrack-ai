"""Shared pure progress calculation; accepts canonical task status values."""
def calculate_percentage(tasks):
    tasks = list(tasks)
    if not tasks:
        return 0.0
    return round(sum((task.get("status") if isinstance(task, dict) else task.status) == "completed"
                     for task in tasks) / len(tasks) * 100, 1)
