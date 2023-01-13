from unittest.mock import MagicMock

from data_hub_api.utils.cache import (
    SingleObjectInMemoryCache
)


class TestSingleObjectInMemoryCache:
    def test_should_get_none_if_not_initialized(self):
        cache = SingleObjectInMemoryCache()
        assert cache.get() is None

    def test_should_get_loaded_value(self):
        cache = SingleObjectInMemoryCache()
        result = cache.get_or_load(load_fn=lambda: 'value_1')
        assert result == 'value_1'

    def test_should_not_call__load_function_multiple_times(self):
        cache = SingleObjectInMemoryCache()
        load_fn = MagicMock(name='load_fn')
        load_fn.return_value = 'value_1'
        cache.get_or_load(load_fn=load_fn)
        result = cache.get_or_load(load_fn=load_fn)
        assert result == 'value_1'
        assert load_fn.call_count == 1
