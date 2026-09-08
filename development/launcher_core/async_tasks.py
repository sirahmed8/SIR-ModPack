"""
async_tasks.py — Managed Asynchronous Task Worker Pool & UI Event Dispatcher.
Provides non-blocking async execution, task registry tracking, and PyWebView custom event emission.
"""
from __future__ import annotations

import concurrent.futures
import json
import threading
import time
import uuid
from typing import Any, Callable, Dict, List, Optional


class AsyncTask:
    """Represents a discrete tracked asynchronous task."""

    def __init__(self, task_id: str, name: str, cancel_event: threading.Event):
        self.task_id = task_id
        self.name = name
        self.status = "running"
        self.progress = 0
        self.message = ""
        self.result: Any = None
        self.error: Optional[str] = None
        self.created_at = time.time()
        self.finished_at: Optional[float] = None
        self.cancel_event = cancel_event

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "status": self.status,
            "progress": self.progress,
            "message": self.message,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "finished_at": self.finished_at,
        }


class AsyncTaskManager:
    """Centralized background task registry and thread pool manager for the launcher."""

    _instance: Optional[AsyncTaskManager] = None
    _lock = threading.Lock()

    def __init__(self, max_workers: int = 8):
        self.max_workers = max_workers
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="SIR_AsyncWorker",
        )
        self.tasks: Dict[str, AsyncTask] = {}
        self.window: Any = None
        self._tasks_lock = threading.Lock()

    @classmethod
    def get_instance(cls, max_workers: int = 8) -> AsyncTaskManager:
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(max_workers=max_workers)
            return cls._instance

    def set_window(self, window: Any) -> None:
        """Attaches active pywebview window for asynchronous event dispatches."""
        self.window = window

    def emit_event(self, event_name: str, payload: Dict[str, Any]) -> None:
        """Pushes structured JSON events to frontend DOM listeners asynchronously."""
        if not self.window:
            return
        def _eval():
            try:
                js_code = (
                    f"window.dispatchEvent(new CustomEvent('{event_name}', "
                    f"{{ detail: {json.dumps(payload)} }}));"
                )
                self.window.evaluate_js(js_code)
            except Exception:
                pass
        threading.Thread(target=_eval, daemon=True).start()

    def submit_task(
        self,
        name: str,
        func: Callable[..., Any],
        *args: Any,
        task_id: Optional[str] = None,
        callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        **kwargs: Any,
    ) -> str:
        """Submits a function to the thread pool and tracks its lifecycle."""
        tid = task_id or f"task_{uuid.uuid4().hex[:8]}"
        cancel_event = threading.Event()
        task = AsyncTask(tid, name, cancel_event)

        with self._tasks_lock:
            self.tasks[tid] = task

        self.emit_event(
            "task_started",
            {"task_id": tid, "name": name, "timestamp": task.created_at},
        )

        def _worker_wrapper() -> Any:
            try:
                # Inspect func args to see if progress_cb or cancel_event are supported
                import inspect
                sig = inspect.signature(func)
                call_kwargs = dict(kwargs)
                
                if "progress_cb" in sig.parameters and "progress_cb" not in call_kwargs:
                    def _pcb(pct: int, msg: str = ""):
                        self.update_task_progress(tid, pct, msg)
                    call_kwargs["progress_cb"] = _pcb

                if "cancel_event" in sig.parameters and "cancel_event" not in call_kwargs:
                    call_kwargs["cancel_event"] = cancel_event

                res = func(*args, **call_kwargs)

                if cancel_event.is_set():
                    task.status = "cancelled"
                else:
                    task.status = "completed"
                    task.progress = 100
                    task.result = res

                fin_time = time.time()
                task.finished_at = fin_time

                self.emit_event(
                    "task_completed" if task.status == "completed" else "task_cancelled",
                    {
                        "task_id": tid,
                        "name": name,
                        "status": task.status,
                        "result": res,
                        "timestamp": fin_time,
                    },
                )
                if callback:
                    try:
                        callback(task.to_dict())
                    except Exception:
                        pass
                return res
            except Exception as ex:
                fin_time = time.time()
                task.status = "failed"
                task.error = str(ex)
                task.finished_at = fin_time

                self.emit_event(
                    "task_failed",
                    {
                        "task_id": tid,
                        "name": name,
                        "error": str(ex),
                        "timestamp": fin_time,
                    },
                )
                if callback:
                    try:
                        callback(task.to_dict())
                    except Exception:
                        pass
                return {"success": False, "error": str(ex)}

        self.executor.submit(_worker_wrapper)
        return tid

    def update_task_progress(self, task_id: str, progress: int, message: str = "") -> None:
        """Updates task progress and emits event."""
        with self._tasks_lock:
            task = self.tasks.get(task_id)
            if task:
                task.progress = max(0, min(100, progress))
                if message:
                    task.message = message

        self.emit_event(
            "task_progress",
            {
                "task_id": task_id,
                "progress": progress,
                "message": message,
            },
        )

    def cancel_task(self, task_id: str) -> bool:
        """Signals cancellation to a running task."""
        with self._tasks_lock:
            task = self.tasks.get(task_id)
            if task and task.status == "running":
                task.cancel_event.set()
                task.status = "cancelled"
                task.finished_at = time.time()
                self.emit_event("task_cancelled", {"task_id": task_id, "name": task.name})
                return True
        return False

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        with self._tasks_lock:
            task = self.tasks.get(task_id)
            return task.to_dict() if task else None

    def list_tasks(self, active_only: bool = False, limit: int = 50) -> List[Dict[str, Any]]:
        with self._tasks_lock:
            tasks_list = [
                t.to_dict()
                for t in self.tasks.values()
                if not active_only or t.status == "running"
            ]
        tasks_list.sort(key=lambda x: x["created_at"], reverse=True)
        return tasks_list[:limit]


class AsyncBridgeExecutor:
    """Convenience singleton proxy for backward compatibility and clean bridge integration."""

    @classmethod
    def get_instance(cls) -> AsyncTaskManager:
        return AsyncTaskManager.get_instance()
