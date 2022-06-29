"""Test Module"""
# standard library
import os
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
class TestTcexCliInit:
    """Test Module"""

    @staticmethod
    def _run_command(args: List[str], monkeypatch: 'pytest.MonkeyPatch') -> str:
        """Helper Method"""
        working_dir = Path(os.path.join(os.getcwd(), 'app_init'))

        # create working directory
        working_dir.mkdir(exist_ok=True, parents=True)

        # change to testing directory
        monkeypatch.chdir(working_dir)

        result = runner.invoke(app, args)
        return result

    def test_tcex_init_organization_basic(self, monkeypatch: 'pytest.MonkeyPatch'):
        """Test Case"""
        result = self._run_command(
            ['init', '--type', 'organization', '--template', 'basic', '--force'], monkeypatch
        )
        assert result.exit_code == 0, result.stdout

        # spot check a few template files
        assert os.path.isfile('app.py')
        assert os.path.isfile('install.json')
        assert os.path.isfile('job_app.py')
        assert os.path.isfile('tcex.json')

    def test_tcex_init_playbook_basic(self, monkeypatch: 'pytest.Monkeypatch'):
        """Test Case"""
        result = self._run_command(
            ['init', '--type', 'playbook', '--template', 'basic'], monkeypatch
        )
        assert result.exit_code == 0, result.stdout

        # spot check a few template files
        assert os.path.isfile('app.py')
        assert os.path.isfile('install.json')
        assert os.path.isfile('playbook_app.py')
        assert os.path.isfile('tcex.json')
