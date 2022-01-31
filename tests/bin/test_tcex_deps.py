"""Bin Testing"""
# standard library
import os
import shutil
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path
from typing import List

# third-party
import pytest
from typer.testing import CliRunner

# dynamically load bin/tcex file
spec = spec_from_loader('app', SourceFileLoader('app', 'bin/tcex'))
tcex_cli = module_from_spec(spec)
spec.loader.exec_module(tcex_cli)

# get app from bin/tcex CLI script
app = tcex_cli.app

# get instance of typer CliRunner for test case
runner = CliRunner()


# pylint: disable=no-self-use
@pytest.mark.run(order=2)
@pytest.mark.xdist_group(name='tcex-deps')
class TestTcexCliDeps:
    """Tcex CLI Testing."""

    def teardown_method(self) -> None:
        """Configure teardown before all tests."""
        # cleanup
        for lib_dir in Path('.').glob('lib_*'):
            if lib_dir.is_dir():
                shutil.rmtree(lib_dir)
            elif lib_dir.is_symlink():
                lib_dir.unlink()

    def _run_command(self, args: List[str], monkeypatch, request) -> str:
        """Test Case"""
        # change to testing directory
        monkeypatch.chdir(os.path.join(request.fspath.dirname, 'app', 'tcpb', 'app_1'))

        result = runner.invoke(app, args)
        assert os.path.isdir(os.path.join('lib_latest', 'tcex'))

        return result

    def test_tcex_deps_std(
        self, monkeypatch: 'pytest.Monkeypatch', request: 'pytest.FixtureRequest'
    ) -> None:
        """Test Case"""
        result = self._run_command(['deps'], monkeypatch, request)
        assert result.exit_code == 0

    def test_tcex_deps_branch(
        self, monkeypatch: 'pytest.Monkeypatch', request: 'pytest.FixtureRequest'
    ) -> None:
        """Test Case"""
        branch = 'develop'
        result = self._run_command(['deps', '--branch', branch], monkeypatch, request)
        assert result.exit_code == 0

        # iterate over command output for validations
        for line in result.stdout.split('\n'):
            # validate that the correct branch is being used
            if 'Using Branch' in line:
                assert branch in line

            # validate that the correct branch is being used
            if 'Running' in line:
                assert 'temp-requirements.txt' in line

    def test_tcex_deps_proxy(
        self, monkeypatch: 'pytest.Monkeypatch', request: 'pytest.FixtureRequest'
    ) -> None:
        """Test Case"""
        proxy_host = os.getenv('TC_PROXY_HOST')
        proxy_port = os.getenv('TC_PROXY_PORT')
        proxy_user = os.getenv('TC_PROXY_USERNAME')
        proxy_pass = os.getenv('TC_PROXY_PASSWORD')

        command = ['deps', '--proxy-host', proxy_host, '--proxy-port', proxy_port]
        if proxy_user and proxy_pass:
            command.extend(['--proxy-user', proxy_user, '--proxy-pass', proxy_pass])

        result = self._run_command(command, monkeypatch, request)
        assert result.exit_code == 0

        # iterate over command output for validations
        for line in result.stdout.split('\n'):
            # validate that the correct branch is being used
            if 'Using Proxy Server' in line:
                assert proxy_host in line
                assert proxy_port in line
                break
        else:
            assert False, 'Proxy settings not found'
