"""Generate Models for ThreatConnect V3 API"""
# standard library
import os
from enum import Enum
from pathlib import Path
from typing import Any

# third-party
import typer

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3._gen_doc_abc import GenerateDocABC
from tcex.api.tc.v3._gen_filter_abc import GenerateFilterABC
from tcex.api.tc.v3._gen_model_abc import GenerateModelABC


class GenerateDoc(GenerateDocABC):
    """Generate Models for TC API Types"""

    def _import_model(self) -> Any:
        """Import the appropriate model."""
        if self.type_ == 'artifact':
            # first-party
            from tcex.api.tc.v3.case_management.models.artifact_model import ArtifactModel as Model
        elif self.type_ == 'artifact_type':
            # first-party
            from tcex.api.tc.v3.case_management.models.artifact_type_model import (
                ArtifactTypeModel as Model,
            )
        elif self.type_ == 'case':
            # first-party
            from tcex.api.tc.v3.case_management.models.case_model import CaseModel as Model
        elif self.type_ == 'note':
            # first-party
            from tcex.api.tc.v3.case_management.models.note_model import NoteModel as Model
        elif self.type_ == 'tag':
            # first-party
            from tcex.api.tc.v3.case_management.models.tag_model import TagModel as Model
        elif self.type_ == 'task':
            # first-party
            from tcex.api.tc.v3.case_management.models.task_model import TaskModel as Model
        elif self.type_ == 'user':
            # first-party
            from tcex.api.tc.v3.security.models.user_model import UserModel as Model
        elif self.type_ == 'user_group':
            # first-party
            from tcex.api.tc.v3.security.models.user_group_model import UserGroupModel as Model
        elif self.type_ == 'workflow_event':
            # first-party
            from tcex.api.tc.v3.case_management.models.workflow_event_model import (
                WorkflowEventModel as Model,
            )
        elif self.type_ == 'workflow_template':
            # first-party
            from tcex.api.tc.v3.case_management.models.workflow_template_model import (
                WorkflowTemplateModel as Model,
            )

        return Model


class GenerateFilter(GenerateFilterABC):
    """Generate Models for TC API Types"""

    def __init__(self, type_: str) -> None:
        """Initialize class properties."""
        super().__init__(type_)

        # properties
        _api_endpoint = getattr(ApiEndpoints, type_.upper()).value
        self.api_url = f'{self._api_server}{_api_endpoint}'


class GenerateModel(GenerateModelABC):
    """Generate Models for TC API Types"""

    def __init__(self, type_: str) -> None:
        """Initialize class properties."""
        super().__init__(type_)

        # properties
        _api_endpoint = getattr(ApiEndpoints, type_.upper()).value
        self.api_url = f'{self._api_server}{_api_endpoint}'


# Update this !!!
class ObjectTypes(str, Enum):
    """Object Types"""

    adversary_assets = 'adversary_assets'
    artifacts = 'artifacts'
    artifact_types = 'artifact_types'
    cases = 'cases'
    groups = 'groups'
    indicators = 'indicators'
    notes = 'notes'
    owners = 'owners'
    owner_roles = 'owner_roles'
    security_labels = 'security_labels'
    system_roles = 'system_roles'
    tags = 'tags'
    tasks = 'tasks'
    users = 'users'
    user_groups = 'user_groups'
    victims = 'victims'
    victim_assets = 'victim_assets'
    workflow_events = 'workflow_events'
    workflow_templates = 'workflow_templates'


app = typer.Typer()


@app.command()
def doc(
    type_: ObjectTypes = typer.Option(
        ..., '--type', help='The ThreatConnect Case Management Type.'
    ),
):
    """Generate the model"""
    gen = GenerateDoc(type_)

    # run model code first so that requirements can be determined
    gen.gen_docs()


@app.command()
def filter(
    type_: ObjectTypes = typer.Option(..., '--type', help='The ThreatConnect Object Type.'),
):
    """Generate the filter class"""
    type_ = type_.value  # get value from enum

    # get instance of model generator
    gen = GenerateFilter(type_)

    # set the output filename using the appropriate tcex api path
    out_path = gen.tap.split('.') + [type_, 'filter.py']
    out_file = Path(os.path.join(*out_path))

    if not out_file.is_file():
        typer.secho(f'\nCould not find file {out_file}.', fg=typer.colors.RED)
        typer.Exit(code=1)

    with out_file.open(mode='w') as fh:
        fh.write(gen.gen_doc_string())
        fh.write(gen.gen_requirements())
        fh.write(gen.gen_class())
        fh.write(gen.gen_class_methods())
        fh.write('')  # newline at the end of the file

    typer.secho(f'Successfully wrote {out_file}.', fg=typer.colors.GREEN)


@app.command()
def model(
    type_: ObjectTypes = typer.Option(..., '--type', help='The ThreatConnect Object Type.'),
):
    """Generate the model"""
    type_ = type_.value  # get value from enum

    # get instance of model generator
    gen = GenerateModel(type_)

    # set the output filename using the appropriate tcex api path
    out_path = gen.tap.split('.') + [type_, 'model.py']
    out_file = Path(os.path.join(*out_path))

    if not out_file.is_file():
        typer.secho(f'\nCould not find file {out_file}.', fg=typer.colors.RED)
        typer.Exit(code=1)

    # generate model fields code first so that requirements can be determined
    model_fields = gen.gen_model_fields()

    with out_file.open(mode='w') as fh:
        fh.write(gen.gen_doc_string())
        fh.write(gen.gen_requirements())
        # add container model
        fh.write(gen.gen_container_class())
        fh.write(gen.gen_container_fields())
        # add data model
        fh.write(gen.gen_data_class())
        fh.write(gen.gen_data_fields())
        # add data model
        fh.write(gen.gen_model_class())
        fh.write(model_fields)
        # add validators
        fh.write(gen.gen_validator_methods())
        # add forward reference requirements
        fh.write(gen.gen_requirements_first_party_forward_reference())
        # add forward references
        fh.write(gen.gen_forward_reference())
        fh.write('')  # newline at the end of the file

    typer.secho(f'Successfully wrote {out_file}.', fg=typer.colors.GREEN)


if __name__ == '__main__':
    app()
