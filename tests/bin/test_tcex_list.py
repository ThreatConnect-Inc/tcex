"""Bin Testing"""
# standard library
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
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
class TestTcexCliList:
    """Tcex CLI Testing."""

    def setup_method(self):
        """Configure teardown before all tests."""

    def teardown_method(self):
        """Configure teardown before all tests."""

    @staticmethod
    def _run_command(args: List[str]) -> str:
        """Test Case"""
        result = runner.invoke(app, args)
        return result

    def test_tcex_list(self) -> None:
        """Test Case"""
        result = self._run_command(['list'])
        assert result.exit_code == 0, result.stdout

        # spot check a few lines of outputs
        assert 'Organization Templates' in result.stdout
        assert 'Playbook Templates' in result.stdout

        # TODO: [med] update this once template is done
        # assert 'API Service Templates' in result.stdout
        # assert 'Trigger Service Templates' in result.stdout
        # assert 'Webhook Trigger Service Templates' in result.stdout

    # TODO: [med] update this once template is done
    # def test_tcex_list_external_api_service(self) -> None:
    #     """Test Case"""
    #     result = self._run_command(['list', '--type', 'api_service'])
    #     assert result.exit_code == 0, result.stdout

    #     # spot check a few lines of outputs
    #     assert 'basic' in result.stdout

    # TODO: [med] update this once template is done
    # def test_tcex_list_external_basic(self) -> None:
    #     """Test Case"""
    #     result = self._run_command(['list', '--type', 'external'])
    #     assert result.exit_code == 0, result.stdout

    #     # spot check a few lines of outputs
    #     assert 'basic' in result.stdout

    def test_tcex_list_organization_basic(self) -> None:
        """Test Case"""
        result = self._run_command(['list', '--type', 'organization'])
        assert result.exit_code == 0, result.stdout

        # spot check a few lines of outputs
        assert 'basic' in result.stdout

    def test_tcex_list_playbook_basic(self) -> None:
        """Test Case"""
        result = self._run_command(['list', '--type', 'playbook'])
        assert result.exit_code == 0, f'{result.stdout}'

        # spot check a few lines of outputs
        assert 'basic' in result.stdout

    # TODO: [med] update this once template is done
    # def test_tcex_list_trigger_basic(self) -> None:
    #     """Test Case"""
    #     result = self._run_command(['list', '--type', 'trigger_service'])
    #     assert result.exit_code == 0, result.stdout

    #     # spot check a few lines of outputs
    #     assert 'basic' in result.stdout

    # TODO: [med] update this once template is done
    # def test_tcex_list_webhook_trigger_basic(self) -> None:
    #     """Test Case"""
    #     result = self._run_command(['list', '--type', 'webhook_trigger_service'])
    #     assert result.exit_code == 0, result.stdout

    #     # spot check a few lines of outputs
    #     assert 'basic' in result.stdout
