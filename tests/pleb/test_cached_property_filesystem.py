"""Tests for tcex.pleb.cached_property_filesystem."""

import pickle
import tempfile
import time
from collections.abc import Generator
from pathlib import Path
from unittest.mock import patch

import pytest
from _pytest.monkeypatch import MonkeyPatch

from tcex.pleb.cached_property_filesystem import cached_property_filesystem


# ---------------------------------------------------------------------------
# Test helper classes
# ---------------------------------------------------------------------------
class Counter:
    """Simple class that tracks how many times ``value`` is computed."""

    def __init__(self) -> None:
        self.call_count: int = 0

    @cached_property_filesystem(ttl=86_400)
    def value(self) -> dict:
        """Return a dict and increment the call counter."""
        self.call_count += 1
        return {'result': self.call_count}


class MultiProp:
    """Class with two independent cached properties."""

    def __init__(self) -> None:
        self.alpha_calls: int = 0
        self.beta_calls: int = 0

    @cached_property_filesystem(ttl=86_400)
    def alpha(self) -> str:
        """First cached property."""
        self.alpha_calls += 1
        return f'alpha-{self.alpha_calls}'

    @cached_property_filesystem(ttl=86_400)
    def beta(self) -> str:
        """Second cached property."""
        self.beta_calls += 1
        return f'beta-{self.beta_calls}'


class ShortTTL:
    """Class with a very short TTL for expiration tests."""

    def __init__(self) -> None:
        self.call_count: int = 0

    @cached_property_filesystem(ttl=1)
    def value(self) -> int:
        """Return incrementing counter with 1-second TTL."""
        self.call_count += 1
        return self.call_count


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def _isolate_cache(tmp_path: Path, monkeypatch: MonkeyPatch) -> Generator[None, None, None]:
    """Isolate each test with a private temp directory and clean caches.

    Args:
        tmp_path: Pytest ``tmp_path`` fixture providing a unique temporary directory.
        monkeypatch: Pytest ``monkeypatch`` fixture for safe attribute patching.
    """
    monkeypatch.setattr(tempfile, 'tempdir', str(tmp_path))
    cached_property_filesystem._reset()
    yield  # type: ignore[misc]
    cached_property_filesystem._reset()


# ---------------------------------------------------------------------------
# Basic caching behavior
# ---------------------------------------------------------------------------
class TestBasicCaching:
    """Verify the core cache-on-first-access contract."""

    def test_first_access_computes_value(self) -> None:
        """First property access should call the underlying function."""
        obj = Counter()
        result: dict = obj.value
        assert result == {'result': 1}
        assert obj.call_count == 1

    def test_second_access_returns_cached_value(self) -> None:
        """Repeated access should return the cached value without recomputing."""
        obj = Counter()
        first: dict = obj.value
        second: dict = obj.value
        assert first == second
        assert obj.call_count == 1

    def test_different_instances_share_filesystem_cache(self) -> None:
        """A second instance should get the filesystem-cached value from the first."""
        a = Counter()
        b = Counter()
        _ = a.value
        assert a.call_count == 1

        # b hits the filesystem cache written by a, so no recompute
        result_b: dict = b.value
        assert b.call_count == 0
        assert result_b == {'result': 1}

    def test_different_classes_have_independent_caches(self) -> None:
        """Instances of different classes should not share cache files."""
        counter = Counter()
        short = ShortTTL()
        _ = counter.value
        _ = short.value
        assert counter.call_count == 1
        assert short.call_count == 1


# ---------------------------------------------------------------------------
# Descriptor protocol
# ---------------------------------------------------------------------------
class TestDescriptorProtocol:
    """Verify Python descriptor behavior (property-style access)."""

    def test_class_level_access_returns_descriptor(self) -> None:
        """Accessing on the class (not an instance) should return the descriptor."""
        descriptor = Counter.value
        assert isinstance(descriptor, cached_property_filesystem)

    def test_property_style_access_no_parentheses(self) -> None:
        """Value should be accessible as ``obj.value``, not ``obj.value()``."""
        obj = Counter()
        result = obj.value
        assert isinstance(result, dict)

    def test_docstring_is_preserved(self) -> None:
        """The wrapped function's docstring should be preserved on the descriptor."""
        assert Counter.value.__doc__ == 'Return a dict and increment the call counter.'


# ---------------------------------------------------------------------------
# Multiple properties
# ---------------------------------------------------------------------------
class TestMultipleProperties:
    """Verify independent caching when a class has multiple decorated properties."""

    def test_properties_are_independent(self) -> None:
        """Accessing one property should not affect the other."""
        obj = MultiProp()
        assert obj.alpha == 'alpha-1'
        assert obj.beta == 'beta-1'
        assert obj.alpha_calls == 1
        assert obj.beta_calls == 1

    def test_each_property_caches_separately(self) -> None:
        """Repeated access to each property should return its own cached value."""
        obj = MultiProp()
        _ = obj.alpha
        _ = obj.beta
        _ = obj.alpha
        _ = obj.beta
        assert obj.alpha_calls == 1
        assert obj.beta_calls == 1


# ---------------------------------------------------------------------------
# Memory cache layer
# ---------------------------------------------------------------------------
class TestMemoryCache:
    """Verify the in-memory (layer 1) cache."""

    def test_memory_cache_key_is_stored_on_instance(self) -> None:
        """After first access, a ``__cache_fs_*`` key should exist in instance __dict__."""
        obj = Counter()
        _ = obj.value
        cache_key = '__cache_fs_value'
        assert cache_key in obj.__dict__
        timestamp, value = obj.__dict__[cache_key]
        assert isinstance(timestamp, float)
        assert value == {'result': 1}

    def test_memory_cache_hit_avoids_filesystem_read(self) -> None:
        """When the memory cache is valid, no filesystem I/O should occur."""
        obj = Counter()
        _ = obj.value

        with patch.object(
            cached_property_filesystem, '_read_fs_cache', return_value=None
        ) as mock_read:
            _ = obj.value
            mock_read.assert_not_called()


# ---------------------------------------------------------------------------
# Filesystem cache layer
# ---------------------------------------------------------------------------
class TestFilesystemCache:
    """Verify the filesystem (layer 2) cache."""

    def test_cache_file_is_created(self, tmp_path: Path) -> None:
        """A ``.pkl`` cache file should be written after first access.

        Args:
            tmp_path: Pytest ``tmp_path`` fixture providing a unique temporary directory.
        """
        obj = Counter()
        _ = obj.value
        cache_dir: Path = tmp_path / 'tcex_cache'
        pkl_files: list[Path] = list(cache_dir.glob('Counter_value.pkl'))
        assert len(pkl_files) == 1

    def test_cache_file_contains_valid_pickle(self, tmp_path: Path) -> None:
        """The cache file should contain a dict with 'timestamp' and 'value' keys.

        Args:
            tmp_path: Pytest ``tmp_path`` fixture providing a unique temporary directory.
        """
        obj = Counter()
        _ = obj.value
        cache_file: Path = tmp_path / 'tcex_cache' / 'Counter_value.pkl'
        raw: dict = pickle.loads(cache_file.read_bytes())
        assert 'timestamp' in raw
        assert 'value' in raw
        assert raw['value'] == {'result': 1}

    def test_filesystem_cache_survives_memory_cache_clear(self, tmp_path: Path) -> None:
        """Clearing the memory cache should still allow a filesystem cache hit.

        Args:
            tmp_path: Pytest ``tmp_path`` fixture providing a unique temporary directory.
        """
        obj = Counter()
        _ = obj.value
        assert obj.call_count == 1

        # clear only the memory cache (not filesystem)
        for key in list(obj.__dict__):
            if key.startswith('__cache_fs_'):
                del obj.__dict__[key]

        # access should hit the filesystem cache, not recompute
        result: dict = obj.value
        assert result == {'result': 1}
        assert obj.call_count == 1

    def test_corrupted_cache_file_triggers_recompute(self, tmp_path: Path) -> None:
        """A corrupted cache file should be treated as a cache miss.

        Args:
            tmp_path: Pytest ``tmp_path`` fixture providing a unique temporary directory.
        """
        obj = Counter()
        _ = obj.value
        assert obj.call_count == 1

        # corrupt the cache file
        cache_file: Path = tmp_path / 'tcex_cache' / 'Counter_value.pkl'
        cache_file.write_bytes(b'corrupted data')

        # clear memory cache to force filesystem read
        for key in list(obj.__dict__):
            if key.startswith('__cache_fs_'):
                del obj.__dict__[key]

        result: dict = obj.value
        assert result == {'result': 2}
        assert obj.call_count == 2


# ---------------------------------------------------------------------------
# TTL expiration
# ---------------------------------------------------------------------------
class TestTTLExpiration:
    """Verify that cached values expire after the configured TTL."""

    def test_memory_cache_expires_after_ttl(self) -> None:
        """After TTL elapses, the memory cache should be stale and recompute."""
        obj = ShortTTL()
        first: int = obj.value
        assert first == 1

        time.sleep(1.1)

        second: int = obj.value
        assert second == 2
        assert obj.call_count == 2

    def test_filesystem_cache_expires_after_ttl(self, tmp_path: Path) -> None:
        """After TTL elapses, even the filesystem cache should be stale.

        Args:
            tmp_path: Pytest ``tmp_path`` fixture providing a unique temporary directory.
        """
        obj = ShortTTL()
        _ = obj.value
        assert obj.call_count == 1

        # clear memory cache and wait for TTL
        for key in list(obj.__dict__):
            if key.startswith('__cache_fs_'):
                del obj.__dict__[key]
        time.sleep(1.1)

        result: int = obj.value
        assert result == 2
        assert obj.call_count == 2


# ---------------------------------------------------------------------------
# Reset
# ---------------------------------------------------------------------------
class TestReset:
    """Verify the ``_reset`` class method."""

    def test_reset_clears_memory_cache(self) -> None:
        """After _reset, the next access should recompute."""
        obj = Counter()
        _ = obj.value
        assert obj.call_count == 1

        cached_property_filesystem._reset()

        result: dict = obj.value
        assert result == {'result': 2}
        assert obj.call_count == 2

    def test_reset_removes_filesystem_cache_files(self, tmp_path: Path) -> None:
        """After _reset, all .pkl files should be removed from the cache directory.

        Args:
            tmp_path: Pytest ``tmp_path`` fixture providing a unique temporary directory.
        """
        obj = Counter()
        _ = obj.value
        cache_dir: Path = tmp_path / 'tcex_cache'
        assert len(list(cache_dir.glob('*.pkl'))) == 1

        cached_property_filesystem._reset()

        assert len(list(cache_dir.glob('*.pkl'))) == 0

    def test_reset_clears_instances_weak_set(self) -> None:
        """After _reset, the instances weak set should be empty."""
        obj = Counter()
        _ = obj.value
        assert len(cached_property_filesystem.instances) > 0

        cached_property_filesystem._reset()

        assert len(cached_property_filesystem.instances) == 0


# ---------------------------------------------------------------------------
# Cache path
# ---------------------------------------------------------------------------
class TestCachePath:
    """Verify cache file path construction."""

    def test_cache_path_uses_class_name_and_attr_name(self, tmp_path: Path) -> None:
        """Cache path should be ``<tempdir>/tcex_cache/<ClassName>_<attr_name>.pkl``.

        Args:
            tmp_path: Pytest ``tmp_path`` fixture providing a unique temporary directory.
        """
        obj = Counter()
        path: Path = cached_property_filesystem._cache_path(obj, 'value')
        assert path == tmp_path / 'tcex_cache' / 'Counter_value.pkl'

    def test_different_classes_get_different_cache_paths(self, tmp_path: Path) -> None:
        """Two different classes with the same attr name should have different paths.

        Args:
            tmp_path: Pytest ``tmp_path`` fixture providing a unique temporary directory.
        """
        counter = Counter()
        short = ShortTTL()
        path_counter: Path = cached_property_filesystem._cache_path(counter, 'value')
        path_short: Path = cached_property_filesystem._cache_path(short, 'value')
        assert path_counter != path_short
        assert 'Counter_' in str(path_counter)
        assert 'ShortTTL_' in str(path_short)


# ---------------------------------------------------------------------------
# Edge cases and error handling
# ---------------------------------------------------------------------------
class TestErrorHandling:
    """Verify graceful handling of filesystem errors."""

    def test_unwritable_cache_dir_still_computes(self, tmp_path: Path) -> None:
        """If the cache dir is not writable, the value should still be computed.

        Args:
            tmp_path: Pytest ``tmp_path`` fixture providing a unique temporary directory.
        """
        cache_dir: Path = tmp_path / 'tcex_cache'
        cache_dir.mkdir(parents=True)
        # read+execute (searchable) but not writable
        cache_dir.chmod(0o555)

        try:
            obj = Counter()
            result: dict = obj.value
            assert result == {'result': 1}
        finally:
            cache_dir.chmod(0o755)

    def test_instance_tracked_in_weak_set(self) -> None:
        """After first access, the instance should appear in the instances weak set."""
        obj = Counter()
        _ = obj.value
        assert obj in cached_property_filesystem.instances

    def test_empty_cache_file_triggers_recompute(self, tmp_path: Path) -> None:
        """An empty cache file should be treated as a cache miss.

        Args:
            tmp_path: Pytest ``tmp_path`` fixture providing a unique temporary directory.
        """
        obj = Counter()
        _ = obj.value

        # overwrite with empty file
        cache_file: Path = tmp_path / 'tcex_cache' / 'Counter_value.pkl'
        cache_file.write_bytes(b'')

        # clear memory cache
        for key in list(obj.__dict__):
            if key.startswith('__cache_fs_'):
                del obj.__dict__[key]

        result: dict = obj.value
        assert result == {'result': 2}

    def test_truncated_pickle_triggers_recompute(self, tmp_path: Path) -> None:
        """A truncated pickle file should be treated as a cache miss.

        Args:
            tmp_path: Pytest ``tmp_path`` fixture providing a unique temporary directory.
        """
        obj = Counter()
        _ = obj.value

        # truncate the file
        cache_file: Path = tmp_path / 'tcex_cache' / 'Counter_value.pkl'
        data: bytes = cache_file.read_bytes()
        cache_file.write_bytes(data[:10])

        # clear memory cache
        for key in list(obj.__dict__):
            if key.startswith('__cache_fs_'):
                del obj.__dict__[key]

        result: dict = obj.value
        assert result == {'result': 2}


# ---------------------------------------------------------------------------
# Wrapt integration
# ---------------------------------------------------------------------------
class TestWraptIntegration:
    """Verify that the wrapt-based wrapper behaves correctly."""

    def test_wrapper_preserves_function_name(self) -> None:
        """The wrapt wrapper should preserve the original function's __name__."""
        descriptor: cached_property_filesystem = Counter.__dict__['value']
        assert descriptor._wrapper.__name__ == 'value'

    def test_wrapper_preserves_function_qualname(self) -> None:
        """The wrapt wrapper should preserve the original function's __qualname__."""
        descriptor: cached_property_filesystem = Counter.__dict__['value']
        assert 'Counter' in descriptor._wrapper.__qualname__
        assert 'value' in descriptor._wrapper.__qualname__

    def test_wrapper_is_callable(self) -> None:
        """The internal wrapper should be a callable (wrapt FunctionWrapper)."""
        descriptor: cached_property_filesystem = Counter.__dict__['value']
        assert callable(descriptor._wrapper)

    def test_wrapper_can_be_bound_to_instance(self) -> None:
        """The wrapper should support the descriptor protocol for method binding."""
        obj = Counter()
        descriptor: cached_property_filesystem = Counter.__dict__['value']
        bound = descriptor._wrapper.__get__(obj, Counter)
        assert callable(bound)
        result = bound()
        assert result == {'result': 1}
