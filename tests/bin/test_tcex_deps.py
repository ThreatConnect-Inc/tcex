"""Bin Testing"""
# standard library
import os
import shutil
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path

# third-party
import pytest
from _pytest.fixtures import FixtureRequest
from click.testing import Result
from typer.testing import CliRunner

# dynamically load bin/tcex file
spec = spec_from_loader('app', SourceFileLoader('app', 'bin/tcex'))
tcex_cli = module_from_spec(spec)  # type: ignore
spec.loader.exec_module(tcex_cli)  # type: ignore

# get app from bin/tcex CLI script
app = tcex_cli.app

# get instance of typer CliRunner for test case
runner = CliRunner()


@pytest.mark.run(order=2)
class TestTcexCliDeps:
    """Tcex CLI Testing."""

    def teardown_method(self):
        """Configure teardown before all tests."""
        # cleanup
        for lib_dir in Path('.').glob('lib_*'):
            if lib_dir.is_dir():
                shutil.rmtree(lib_dir)
            elif lib_dir.is_symlink():
                lib_dir.unlink()

    def _run_command(
        self,
        args: list[str],
        new_app_dir: str,
        monkeypatch: pytest.MonkeyPatch,
        request: FixtureRequest,
    ) -> Result:
        """Test Case"""
        app_path = os.path.join(request.fspath.dirname, 'app', 'tcpb', 'app_1')  # type: ignore
        new_app_path = os.path.join(os.getcwd(), 'app', 'tcpb', new_app_dir)
        shutil.copytree(app_path, new_app_path)

        # change to testing directory
        monkeypatch.chdir(new_app_path)

        try:
            result = runner.invoke(app, args)
            assert os.path.isdir(os.path.join('lib_latest', 'tcex'))
        finally:
            # clean up
            shutil.rmtree(new_app_path)

        return result

    def test_tcex_deps_std(self, monkeypatch: pytest.MonkeyPatch, request: FixtureRequest):
        """Test Case"""
        result = self._run_command(['deps'], 'app_std', monkeypatch, request)
        assert result.exit_code == 0

    def test_tcex_deps_branch(self, monkeypatch: pytest.MonkeyPatch, request: FixtureRequest):
        """Test Case"""
        branch = 'develop'
        result = self._run_command(['deps', '--branch', branch], 'app_branch', monkeypatch, request)
        assert result.exit_code == 0

        # iterate over command output for validations
        for line in result.stdout.split('\n'):
            # validate that the correct branch is being used
            if 'Using Branch' in line:
                assert branch in line

            # validate that the correct branch is being used
            if 'Running' in line:
                assert 'temp-requirements.txt' in line

    def test_tcex_deps_proxy(self, monkeypatch: pytest.MonkeyPatch, request: FixtureRequest):
        """Test Case"""
        proxy_host = os.getenv('TC_PROXY_HOST')
        proxy_port = os.getenv('TC_PROXY_PORT')
        proxy_user = os.getenv('TC_PROXY_USERNAME')
        proxy_pass = os.getenv('TC_PROXY_PASSWORD')

        command = ['deps', '--proxy-host', proxy_host, '--proxy-port', proxy_port]
        if proxy_user and proxy_pass:
            command.extend(['--proxy-user', proxy_user, '--proxy-pass', proxy_pass])

        result = self._run_command(command, 'app_proxy', monkeypatch, request)
        assert result.exit_code == 0

        # iterate over command output for validations
        for line in result.stdout.split('\n'):
            # validate that the correct branch is being used
            if 'Using Proxy Server' in line:
                assert proxy_host in line  # type: ignore
                assert proxy_port in line  # type: ignore
                break
        else:
            assert False, 'Proxy settings not found'
