import ctypes
import ctypes.util
import gc
from time import monotonic
from threading import Lock
from typing import Callable, Optional,  Protocol, TypeVar


T = TypeVar('T')


def _malloc_trim() -> None:
    libc_name = ctypes.util.find_library('c')
    if libc_name:
        try:
            ctypes.CDLL(libc_name).malloc_trim(0)
        except AttributeError:
            pass


class SingleObjectCache(Protocol[T]):
    def get_or_load(self, load_fn: Callable[[], T]) -> T:
        pass


class DummySingleObjectCache(SingleObjectCache[T]):
    def get_or_load(self, load_fn: Callable[[], T]) -> T:
        return load_fn()


class InMemorySingleObjectCache(SingleObjectCache[T]):
    def __init__(
        self,
        max_age_in_seconds: float
    ) -> None:
        self.max_age_in_seconds = max_age_in_seconds
        self._lock = Lock()
        self._value: Optional[T] = None
        self._last_updated_time: Optional[float] = None

    def _is_max_age_reached(self, now: float) -> bool:
        return bool(
            self._last_updated_time is not None
            and (now - self._last_updated_time > self.max_age_in_seconds)
        )

    def get_or_load(self, load_fn: Callable[[], T]) -> T:
        with self._lock:
            now = monotonic()
            result = self._value
            if result is not None and not self._is_max_age_reached(now):
                return result
            self._value = None
            del result
            gc.collect()
            _malloc_trim()
            result = load_fn()
            assert result is not None
            self._value = result
            self._last_updated_time = now
            return result
