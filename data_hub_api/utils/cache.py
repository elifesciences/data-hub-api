from typing import Callable, Optional,  Protocol, TypeVar


T = TypeVar('T')


class SingleObjectCache(Protocol[T]):
    def get(self) -> Optional[T]:
        pass

    def get_or_load(self, load_fn: Callable[[], T]) -> T:
        pass


class SingleObjectInMemoryCache(SingleObjectCache[T]):

    def __init__(self, initial_value: Optional[T] = None) -> None:
        self._value = initial_value

    def get(self) -> Optional[T]:
        return self._value

    def get_or_load(self, load_fn: Callable[[], T]) -> T:
        result = self.get()
        if result is not None:
            return result
        result = load_fn()
        assert result is not None
        self._value = result
        return result
