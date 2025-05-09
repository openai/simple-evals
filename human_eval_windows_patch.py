import threading
import contextlib
import human_eval.execution  # Module to be patched
from typing import Any # Only for the print statement type hint, not strictly needed by patch logic

# 1. Define our custom TimeoutException.
# This will be raised by our patched time_limit and will replace
# the original TimeoutException in human_eval.execution
# so that existing `except TimeoutException:` blocks in human_eval continue to work.
class PatchedTimeoutException(Exception):
    """Custom TimeoutException for the patched time_limit function."""
    pass

# 2. Define the new time_limit implementation using threading.Timer.
@contextlib.contextmanager
def patched_time_limit(seconds: float):
    """
    A time_limit context manager compatible with Windows, using threading.Timer.
    Replaces human_eval.execution.time_limit.
    """
    
    # The callback function for threading.Timer.
    # It raises our PatchedTimeoutException.
    def _timer_callback():
        raise PatchedTimeoutException(f"Code execution timed out after {seconds} seconds.")

    # Create and start the timer.
    # threading.Timer will raise appropriate errors if 'seconds' is not a valid number.
    timer = threading.Timer(seconds, _timer_callback)
    timer.start()
    
    try:
        # Yield control to the block within the 'with' statement.
        yield
    finally:
        # This block executes whether the 'try' block succeeded or failed.
        # Crucially, cancel the timer to prevent it from firing if the guarded code finished on time
        # or if an exception other than timeout occurred.
        timer.cancel()

# 3. Apply the monkeypatch.
# This should happen when this patch module is imported.

# Replace the TimeoutException in the human_eval.execution module
# with our PatchedTimeoutException.
human_eval.execution.TimeoutException = PatchedTimeoutException

# Replace the time_limit function in the human_eval.execution module
# with our patched_time_limit function.
human_eval.execution.time_limit = patched_time_limit


# --- Verification (Optional, but helpful for debugging) ---
# You can include these lines to confirm that the patch has been applied
# when this module is imported.
def _confirm_patch():
    patched_module = human_eval.execution
    time_limit_func: Any = getattr(patched_module, 'time_limit', None)
    timeout_exc: Any = getattr(patched_module, 'TimeoutException', None)

    if time_limit_func is patched_time_limit and timeout_exc is PatchedTimeoutException:
        print(f"[human_eval_windows_patch] Successfully patched 'human_eval.execution.time_limit' and 'human_eval.execution.TimeoutException'.")
        print(f"[human_eval_windows_patch] human_eval.execution.time_limit is now: {time_limit_func}")
        print(f"[human_eval_windows_patch] human_eval.execution.TimeoutException is now: {timeout_exc}")
    else:
        print(f"[human_eval_windows_patch] WARNING: Patching human_eval.execution may not have been successful.")
        print(f"    Current time_limit: {time_limit_func}")
        print(f"    Current TimeoutException: {timeout_exc}")

# _confirm_patch() 