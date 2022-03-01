"""App Spec Model"""
# pylint: disable=no-self-argument,no-self-use
# standard library
from copy import deepcopy
from typing import List, Optional

# third-party
from pydantic import BaseModel, Field, validator
from semantic_version import Version

# first-party
from tcex.app_config.models.install_json_model import (
    FeedsModel,
    InstallJsonCommonModel,
    InstallJsonOrganizationModel,
    OutputVariablesModel,
    ParamsModel,
    RetryModel,
    TypeEnum,
    snake_to_camel,
)
from tcex.app_config.models.job_json_model import JobJsonCommonModel
from tcex.pleb.none_model import NoneModel

__all__ = ['AppSpecYmlModel']


class FeedsSpecModel(FeedsModel):
    """Model for app_spec.organization.feeds."""

    job: Optional[JobJsonCommonModel] = Field(None, description='')


class NotesPerActionModel(BaseModel):
    """Model for app_spec.notes_per_action."""

    action: str = Field(..., description='The action name.')
    note: str = Field(..., description='The note describing the action.')

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class OrganizationModel(InstallJsonOrganizationModel):
    """Model for app_spec.organization."""

    feeds: Optional[List[FeedsSpecModel]] = Field(None, description='')

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class OutputVariablesSpecModel(OutputVariablesModel):
    """Model for app_spec.outputs.output_variables."""

    disabled: Optional[bool] = Field(
        False,
        description='If True, the output will not be included in ij/lj files.',
    )
    type: str = Field(
        'String',
        description='The output variable type (e.g., String, TCEntity, etc).',
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class OutputDataModel(BaseModel):
    """Model for app_spec.output_data."""

    display: Optional[str] = Field(
        None,
        description='The display clause that controls visibility of the output.',
    )
    output_variables: List[OutputVariablesSpecModel] = Field(
        ...,
        description='An array of output variables.',
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class ParamsSpecModel(ParamsModel):
    """Model for app_spec.params."""

    display: Optional[str] = Field(
        None,
        description='The display clause from the layout.json file.',
    )
    disabled: Optional[bool] = Field(
        False,
        description='If True, the parameter will not be included in ij/lj files.',
    )
    type: TypeEnum = Field(
        TypeEnum.String,
        description='',
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        smart_union = True
        use_enum_values = True
        validate_assignment = True


class PlaybookSpecModel(BaseModel):
    """Model for app_spec.playbook."""

    retry: Optional[RetryModel] = Field(
        None,
        description='',
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class ReleaseNoteModel(BaseModel):
    """Model for app_spec.releaseNotes."""

    notes: List[str] = Field(
        ...,
        description='One or more notes for the release.',
    )
    version: str = Field(
        ...,
        description='The version of the release.',
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class SectionsModel(BaseModel):
    """Model for app_spec.sections."""

    section_name: str = Field(
        ...,
        description='The name of the section.',
    )
    params: List[ParamsSpecModel] = Field(
        ...,
        description='A list of input parameter data.',
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class AppSpecYmlModel(InstallJsonCommonModel):
    """Model for the app_spec.yml file."""

    # app_name: str = Field(
    #     None,
    #     description='The package name for the App.',
    # )
    category: str = Field(
        ...,
        description='The category of the App. Also playbook.type for playbook Apps.',
    )
    note_per_action: Optional[List[NotesPerActionModel]] = Field(
        None,
        description='',
    )
    organization: Optional[OrganizationModel] = Field(
        None,
        description='A section for settings related to the organization (job) Apps.',
    )
    playbook: Optional[PlaybookSpecModel] = Field(
        None,
        description='The playbook section of the install.json.',
    )
    release_notes: List[ReleaseNoteModel] = Field(
        ...,
        description='The release notes for the App.',
    )
    schema_version: str = Field(
        '1.0.0',
        description='The version of the App Spec schema.',
    )
    sections: List[SectionsModel] = Field(
        ...,
        description='Layout sections for an App including params.',
    )
    output_data: Optional[List[OutputDataModel]] = Field(
        None,
        description='The outputs data for Playbook and Service Apps.',
    )

    # @validator('sections', pre=True)
    # def _sections(cls, v: str, values: dict) -> dict:
    #     """Return a version object for "version" fields."""
    #     # set defaults for playbook apps
    #     # params are formatted as camelCase
    #     # values comes in with snake_case
    #     for section in v:
    #         for param in section.get('params'):
    #             # update playbook data types
    #             if values.get('runtime_level').lower() == 'playbook':
    #                 # by rule any input of type String must have String and playbookDataType
    #                 if param.get('type', 'String') == 'String' and not param.get(
    #                     'playbookDataType'
    #                 ):
    #                     param['playbookDataType'] = ['String']

    #             # update valid values in params
    #             if (
    #                 param.get('type', 'String') == 'String'
    #                 and not param.get('validValues')
    #                 and (
    #                     'String' in param.get('playbookDataType', [])
    #                     or values.get('runtime_level').lower() == 'organization'
    #                 )
    #             ):
    #                 param['validValues'] = ['${TEXT}']
    #                 if param.get('encrypt') is True:
    #                     param['validValues'] = ['${KEYCHAIN}']
    #     return v  # pragma: no cover

    @validator('schema_version')
    def _version(cls, v: str):
        """Return a version object for "version" fields."""
        if v is not None:
            return Version(v)
        return v  # pragma: no cover

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True

    @property
    def inputs(self) -> list:
        """Return lj.inputs."""
        _inputs = []
        for sequence, section in enumerate(self.sections, start=1):
            # don't include section with no params
            if not [sp for sp in section.params if sp.disabled is False]:
                continue

            # build params
            parameters = []
            for p in section.params:
                if p.disabled is True:
                    continue

                param = {'name': p.name}
                if p.display:
                    param['display'] = p.display

                parameters.append(param)

            # append section
            _inputs.append(
                {
                    'parameters': parameters,
                    'sequence': sequence,
                    'title': section.section_name,
                }
            )
        return _inputs

    def get_note_per_action(self, action: str) -> 'NotesPerActionModel':
        """Return the note_per_action for the provided action."""
        for npa in self.note_per_action:
            if npa.action == action:
                return npa
        return NoneModel()

    @property
    def note_per_action_formatted(self) -> List[str]:
        """Return formatted note_per_action."""
        _note_per_action = ['\n\nThe following actions are included:']
        _note_per_action.extend(
            [f'- **{npa.action}** - {npa.note}' for npa in self.note_per_action]
        )
        return _note_per_action

    @property
    def outputs(self) -> List[OutputVariablesModel]:
        """Return lj.outputs."""
        _outputs = []
        for output_data in self.output_data:
            for output_variable in output_data.output_variables:
                if output_variable.disabled is True:
                    continue

                _outputs.append(
                    {
                        'display': output_data.display,
                        'name': output_variable.name,
                    }
                )
        return _outputs

    @property
    def output_variables(self) -> List[OutputVariablesModel]:
        """Return ij.playbook.outputVariables."""
        return [
            ov
            for output in self.output_data
            for ov in output.output_variables
            if ov.disabled is False
        ]

    @property
    def params(self) -> List[ParamsModel]:
        """Return ij.params."""
        _params = []
        sequence = 1
        for section in deepcopy(self.sections):
            for param in section.params:
                if param.disabled is True:
                    continue

                # set default playbookDataType for String type params
                self._set_default_playbook_data_type(param)

                # set default validValues for String type params
                self._set_default_valid_values(param)

                # remove the disabled field (not supported in install.json)
                param.disabled = None

                # remove the display field (not supported in install.json)
                param.display = None

                # add the sequence number
                param.sequence = sequence

                _params.append(param)

                # increment sequence
                sequence += 1
        return _params

    @property
    def release_notes_formatted(self) -> List[str]:
        """Return readme_md.releaseNotes."""
        _release_notes = ['## Release Notes']
        _release_notes.append('')
        for release_note in self.release_notes:
            _release_notes.append(f'### {release_note.version}')
            _release_notes.append('')
            _release_notes.extend([f'* {rn}' for rn in release_note.notes])
            _release_notes.append('')
        return _release_notes

    @property
    def requires_layout(self):
        """Return True if App requires a layout.json file."""
        if self.runtime_level.lower() == 'organization':
            return False

        for section in self.sections:
            for param in section.params:
                if param.display:
                    return True

        for output_data in self.output_data:
            if output_data.display not in [None, '1', '']:
                return True

        return False

    def _set_default_playbook_data_type(self, param: 'ParamsSpecModel'):
        """Set default playbookDataType for String type params.

        Playbook Data Types rule:
          * Input type is "String"
          * No "playbookDataType" values are provided
        """
        if self.runtime_level.lower() == 'playbook':
            # by rule any input of type String must have String and playbookDataType
            if param.type == 'String' and not param.playbook_data_type:
                param.playbook_data_type = ['String']

    def _set_default_valid_values(self, param: 'ParamsSpecModel'):
        """Set default playbookDataType for String type params.

        Valid Values rule:
          * Input type is "String"
          * No "validValues" values are provided
          * The playbookDataType supports String
        """
        if (
            param.type == 'String'
            and not param.valid_values
            and (
                'String' in param.playbook_data_type
                or self.runtime_level.lower()
                in ['organization', 'triggerservice', 'webhooktriggerservice']
            )
        ):
            param.valid_values = ['${TEXT}']
            if param.encrypt is True:
                param.valid_values = ['${KEYCHAIN}']
