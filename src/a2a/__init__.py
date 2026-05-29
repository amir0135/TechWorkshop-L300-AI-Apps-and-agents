"""Local `a2a` package for the Zava Product Manager app.

This directory is named ``a2a`` to match the workshop docs, but the
installed ``a2a-sdk`` PyPI package is *also* called ``a2a``. Because this
folder is discovered on ``sys.path`` first when running from ``src/``, it
shadows the SDK and imports like ``from a2a.server.apps import ...``
fail with ``ModuleNotFoundError``.

To allow both to coexist, we locate the installed ``a2a-sdk`` package
directory and append it to this package's ``__path__``. Python will then
search both locations when resolving ``a2a.<submodule>``:

* ``a2a.agent`` and ``a2a.api`` resolve from this local folder.
* ``a2a.server``, ``a2a.types``, ``a2a.client``, ... resolve from the
  installed ``a2a-sdk``.
"""

from __future__ import annotations

import os
import site
import sys
from importlib.machinery import PathFinder

_local_dir = os.path.dirname(__file__)


def _candidate_site_dirs() -> list[str]:
    dirs: list[str] = []
    try:
        dirs.extend(site.getsitepackages())
    except (AttributeError, OSError):
        pass
    try:
        user_site = site.getusersitepackages()
        if user_site:
            dirs.append(user_site)
    except (AttributeError, OSError):
        pass
    # Also consider any sys.path entry that looks like a site-packages dir.
    for entry in sys.path:
        if entry and entry.endswith(("site-packages", "dist-packages")):
            dirs.append(entry)
    # De-duplicate while preserving order.
    seen: set[str] = set()
    unique: list[str] = []
    for d in dirs:
        if d and d not in seen:
            seen.add(d)
            unique.append(d)
    return unique


def _find_installed_a2a_sdk() -> str | None:
    for site_dir in _candidate_site_dirs():
        candidate = os.path.join(site_dir, "a2a")
        if (
            os.path.isdir(candidate)
            and os.path.abspath(candidate) != os.path.abspath(_local_dir)
            and os.path.isfile(os.path.join(candidate, "__init__.py"))
            and os.path.isdir(os.path.join(candidate, "server"))
        ):
            return candidate
    return None


_sdk_path = _find_installed_a2a_sdk()
if _sdk_path and _sdk_path not in __path__:
    # Make this package a hybrid: local subpackages + a2a-sdk subpackages.
    __path__.append(_sdk_path)
    # Invalidate any cached negative lookups so the SDK submodules become
    # discoverable in already-running interpreters.
    PathFinder.invalidate_caches()
