"""Windows: py scripts/calculate_progress.py --tasks '[{"status":"completed"}]'

Without --tasks, reads a JSON list from standard input. Stdout is JSON only.
"""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.services.progress_calculation import calculate_percentage


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", help="JSON array of tasks")
    args = parser.parse_args()
    try:
        tasks = json.loads(args.tasks if args.tasks is not None else sys.stdin.read())
        if not isinstance(tasks, list) or any(not isinstance(t, dict) or t.get("status") not in
                {"pending", "in_progress", "completed"} for t in tasks):
            raise ValueError("Use uma lista de tarefas com status pending/in_progress/completed.")
        print(json.dumps({"percentage": calculate_percentage(tasks)}))
    except (ValueError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
