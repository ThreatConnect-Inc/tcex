# -*- coding: utf-8 -*-
"""MonkeyPatch Testing Module"""
# pylint: disable=cell-var-from-loop,redefined-outer-name


def monkeypatch(target, call_target=True, tags=None):
    """Register method with the monkeypatch annotation"""

    if tags is None:
        tags = []

    def decorator(fn):
        register_monkeypatch(target=target, patch=fn, call_target=call_target, tags=tags)

        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        return wrapper

    return decorator


__monkeypatches = {}


def register_monkeypatch(target, patch, call_target=True, tags=None):
    """Register all methods with the monkeypatch annotation"""
    if tags is None:
        tags = []
    __monkeypatches[target.__module__ + target.__name__] = (target, patch, call_target, tags)
    # __monkeypatches.append((target, patch, call_target, tags))


def register_monkeypatches(monkeypatch, profile_data):
    """Register all methods with the monkeypatch annotation"""
    if not profile_data.get('monkeypatch'):
        return

    patches = [v for k, v in __monkeypatches.items()]

    if 'tags' in profile_data.get('monkeypatch', {}):
        include_tags = profile_data.get('monkeypatch', {}).get('tags')
        patches = filter(lambda m: set(m[3]).intersection(set(include_tags)), __monkeypatches)

    for p in patches:
        target = p[0]
        patch = p[1]
        call_target = p[2]

        def patched(*args, **kwargs):
            if call_target:
                patch(profile_data, args, kwargs)

                return target(*args, **kwargs)

            return patch(profile_data, args, kwargs)

        monkeypatch.setattr(__import__(target.__module__), target.__name__, patched)
