# Copyright 2025 Open Source Robotics Foundation, Inc.
# Licensed under the Apache License, Version 2.0

from pathlib import Path
import platform
import sys
from unittest.mock import patch

from colcon_library_path.environment.library_path import LibraryPathEnvironment
import pytest

skip_unless_windows = pytest.mark.skipif(
    sys.platform != 'win32',
    reason='Test is only applicable to Windows systems')

skip_unless_darwin = pytest.mark.skipif(
   platform.system() != 'Darwin',
   reason='Test is only applicable to Darwin systems')

skip_if_darwin_or_windows = pytest.mark.skipif(
    sys.platform == 'win32' or platform.system() == 'Darwin',
    reason='Test is not applicable to Darwin or Windows systems')


@pytest.fixture(scope='module', autouse=True)
def env_hook_patch():
    with patch(
        'colcon_core.shell.create_environment_hook',
        return_value=['/some/hook', '/other/hook']
    ):
        yield


@pytest.mark.parametrize('search_path', [
    pytest.param('lib/libfoo.so', marks=skip_if_darwin_or_windows),
    pytest.param('lib64/libfoo.so', marks=skip_if_darwin_or_windows),
    pytest.param('lib/libfoo.dylib', marks=skip_unless_darwin),
    pytest.param('bin/foo.dll', marks=skip_unless_windows),
])
def test_library_path(tmpdir, search_path):
    extension = LibraryPathEnvironment()
    prefix_path = Path(tmpdir)
    library = prefix_path / search_path

    # no libraries or directories
    hooks = extension.create_environment_hooks(prefix_path, 'pkg_name')
    assert len(hooks) == 0

    # library directory exists but is empty
    library.parent.mkdir(parents=True)
    hooks = extension.create_environment_hooks(prefix_path, 'pkg_name')
    assert len(hooks) == 0

    # subdirectories named similarly to library
    # TODO: This should probably be fixed
    # library.with_name('dir_' + library.name).mkdir(parents=True)
    # hooks = extension.create_environment_hooks(prefix_path, 'pkg_name')
    # assert len(hooks) == 0

    # library exists
    library.touch()
    hooks = extension.create_environment_hooks(prefix_path, 'pkg_name')
    assert len(hooks) > 0
