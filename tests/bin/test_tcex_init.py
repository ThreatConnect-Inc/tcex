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


@pytest.mark.run(order=2)
@pytest.mark.xfail(reason='To many request to github will cause this to fail.')
class TestTcexCliInit:
    """Tcex CLI Testing."""

    # def setup_method(self, monkeypatch):
    #     """Configure teardown before all tests."""
    #     tcex_test_dir = os.getenv('TCEX_TEST_DIR')
    #     self.app_dir = Path(os.path.join(tcex_test_dir, 'bin', 'app', 'tcpb', 'app_init'))
    #     self.app_dir.mkdir(exist_ok=True, parents=True)

    #     # return to project directory
    #     monkeypatch.chdir(self.app_dir)

    # def teardown_method(self):
    #     """Configure teardown before all tests."""
    #     # return to project directory
    #     # os.chdir(self.project_dir)

    #     # clean up temp app directory
    #     shutil.rmtree(self.app_dir)

    @staticmethod
    def _run_command(args: List[str], monkeypatch, request) -> str:
        """Test Case"""
        working_dir = Path(os.path.join(request.fspath.dirname, 'app', 'tcpb', 'app_init'))

        # create working directory
        working_dir.mkdir(exist_ok=True, parents=True)

        # change to testing directory
        monkeypatch.chdir(working_dir)

        result = runner.invoke(app, args)
        return result

    # TODO: [med] update this once template is done
    # def test_tcex_init_external_api_service(self) -> None:
    #     """Test Case"""
    #     result = self._run_command(['init', '--type', 'api_service', '--template', 'basic'])
    #     assert result.exit_code == 0, result.stdout

    #     # spot check a few template files
    #     assert os.path.isfile('api_service_app.py')
    #     assert os.path.isfile('app.py')
    #     assert os.path.isfile('install.json')
    #     assert os.path.isfile('tcex.json')

    # TODO: [med] update this once template is done
    # def test_tcex_init_external_basic(self) -> None:
    #     """Test Case"""
    #     result = self._run_command(['init', '--type', 'external', '--template', 'basic'])
    #     assert result.exit_code == 0, result.stdout

    #     # spot check a few template files
    #     assert os.path.isfile('app.py')
    #     assert os.path.isfile('external_app.py')

    def test_tcex_init_organization_basic(
        self, monkeypatch: 'pytest.Monkeypatch', request: 'pytest.FixtureRequest'
    ) -> None:
        """Test Case"""
        result = self._run_command(
            ['init', '--type', 'organization', '--template', 'basic', '--force'],
            monkeypatch,
            request,
        )
        assert result.exit_code == 0, result.stdout

        # spot check a few template files
        assert os.path.isfile('app.py')
        assert os.path.isfile('install.json')
        assert os.path.isfile('job_app.py')
        assert os.path.isfile('tcex.json')

        # cleanup
        shutil.rmtree(os.getcwd())

    def test_tcex_init_playbook_basic(
        self, monkeypatch: 'pytest.Monkeypatch', request: 'pytest.FixtureRequest'
    ) -> None:
        """Test Case"""
        result = self._run_command(
            ['init', '--type', 'playbook', '--template', 'basic'], monkeypatch, request
        )
        assert result.exit_code == 0, result.stdout

        # spot check a few template files
        assert os.path.isfile('app.py')
        assert os.path.isfile('install.json')
        assert os.path.isfile('playbook_app.py')
        assert os.path.isfile('tcex.json')

        # cleanup
        shutil.rmtree(os.getcwd())

    # TODO: [med] update this once template is done
    # def test_tcex_init_trigger_basic(
    #     self, monkeypatch: 'pytest.Monkeypatch', request: 'pytest.FixtureRequest'
    # ) -> None:
    #     """Test Case"""
    #     result = self._run_command(
    #         ['init', '--type', 'trigger_service', '--template', 'basic'], monkeypatch, request
    #     )
    #     assert result.exit_code == 0, result.stdout

    #     # spot check a few template files
    #     assert os.path.isfile('app.py')
    #     assert os.path.isfile('install.json')
    #     assert os.path.isfile('service_app.py')
    #     assert os.path.isfile('tcex.json')

    #     # cleanup
    #     shutil.rmtree(os.getcwd())

    # TODO: [med] update this once template is done
    # def test_tcex_init_webhook_trigger_basic(
    #     self, monkeypatch: 'pytest.Monkeypatch', request: 'pytest.FixtureRequest'
    # ) -> None:
    #     """Test Case"""
    #     result = self._run_command(
    #         ['init', '--type', 'webhook_trigger_service', '--template', 'basic'],
    #         monkeypatch,
    #         request,
    #     )
    #     assert result.exit_code == 0, result.stdout

    #     # spot check a few template files
    #     assert os.path.isfile('app.py')
    #     assert os.path.isfile('install.json')
    #     assert os.path.isfile('service_app.py')
    #     assert os.path.isfile('tcex.json')

    #     # cleanup
    #     shutil.rmtree(os.getcwd())
