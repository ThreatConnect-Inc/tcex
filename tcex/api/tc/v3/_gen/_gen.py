"""TcEx Framework Module"""

# standard library
import os
from enum import Enum
from pathlib import Path

# third-party
import typer

# first-party
from tcex.api.tc.v3._gen._gen_args_abc import GenerateArgsABC
from tcex.api.tc.v3._gen._gen_filter_abc import GenerateFilterABC
from tcex.api.tc.v3._gen._gen_model_abc import GenerateModelABC
from tcex.api.tc.v3._gen._gen_object_abc import GenerateObjectABC
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.util import Util
from tcex.util.code_operation import CodeOperation
from tcex.util.render.render import Render
from tcex.util.string_operation import SnakeString

# initialize Util module
util = Util()


def log_server():
    """Log server."""
    _api_server = os.getenv('TC_API_PATH')
    Render.panel.info(f'Using server {_api_server}')


class GenerateArgs(GenerateArgsABC):
    """Generate Models for TC API Types"""


class GenerateFilter(GenerateFilterABC):
    """Generate Models for TC API Types"""

    def __init__(self, type_: SnakeString):
        """Initialize instance properties."""
        super().__init__(type_)

        # properties
        _api_endpoint = getattr(ApiEndpoints, type_.upper()).value
        self.api_url = f'{self._api_server}{_api_endpoint}'


class GenerateModel(GenerateModelABC):
    """Generate Models for TC API Types"""

    def __init__(self, type_: SnakeString):
        """Initialize instance properties."""
        super().__init__(type_)

        # properties
        _api_endpoint = getattr(ApiEndpoints, type_.upper()).value
        self.api_url = f'{self._api_server}{_api_endpoint}'


class GenerateObject(GenerateObjectABC):
    """Generate Models for TC API Types"""

    def __init__(self, type_: SnakeString):
        """Initialize instance properties."""
        super().__init__(type_)

        # properties
        _api_endpoint = getattr(ApiEndpoints, type_.upper()).value
        self.api_url = f'{self._api_server}{_api_endpoint}'


def gen_args(type_: SnakeString, indent_blocks: int):
    """Generate args code."""
    # get instance of doc generator
    gen = GenerateArgs(type_)

    # run model code first so that requirements can be determined
    i1 = ' ' * (4 * indent_blocks)
    i2 = i1 + ' ' * 4
    print(gen.gen_args(i1=i1, i2=i2))


def gen_filter(type_: SnakeString):
    """Generate the filter code."""
    # get instance of filter generator
    gen = GenerateFilter(type_)

    # set the output filename using the appropriate tcex api path
    out_path = gen.tap(type_).split('.') + [type_, f'{type_.singular()}_filter.py']
    out_file = Path(os.path.join(*out_path))

    if not out_file.is_file():
        out_file.write_text('')

    # generate class methods first so requirements can be updated
    class_methods = gen.gen_class_methods()

    _code = gen.gen_doc_string()
    _code += gen.gen_requirements()
    _code += gen.gen_class()
    _code += class_methods
    _code += ''  # newline at the end of the file

    with out_file.open(mode='w') as fh:
        fh.write(CodeOperation.format_code(_code))

    Render.panel.success(f'Successfully wrote {out_file}.')

    for msg in gen.messages:
        Render.panel.warning(msg)


def gen_model(type_: SnakeString):
    """Generate model code."""
    # get instance of model generator
    gen = GenerateModel(type_)

    # set the output filename using the appropriate tcex api path
    out_path = gen.tap(type_).split('.') + [type_, f'{type_.singular()}_model.py']
    out_file = Path(os.path.join(*out_path))

    if not out_file.is_file():
        out_file.write_text('')

    # generate model fields code first so that requirements can be determined
    container_private_attrs = gen.gen_container_private_attrs()
    model_fields = gen.gen_model_fields()
    model_private_attrs = gen.gen_model_private_attrs()
    validator_methods = gen.gen_validator_methods()

    _code = gen.gen_doc_string()
    _code += gen.gen_requirements()
    # add generated model class (ArtifactModel, CaseModel, etc.)
    _code += gen.gen_model_class()
    _code += model_private_attrs
    _code += model_fields
    # add validators to model class
    _code += validator_methods
    # add generated "data" model class (ArtifactDataModel, CaseDataModel, etc.)
    _code += gen.gen_data_class()
    _code += gen.gen_data_fields()
    # add generated container model class (ArtifactsModel, CasesModel, etc.)
    _code += gen.gen_container_class()
    _code += container_private_attrs
    _code += gen.gen_container_fields()
    # add forward reference requirements
    _code += gen.gen_requirements_first_party_forward_reference()
    # add forward references
    _code += gen.gen_forward_reference()

    with out_file.open(mode='w') as fh:
        fh.write(CodeOperation.format_code(_code))

    Render.panel.success(f'Successfully wrote {out_file}.')

    for msg in gen.messages:
        Render.panel.warning(msg)


def gen_object(type_: SnakeString):
    """Generate object code."""
    # get instance of filter generator
    gen = GenerateObject(type_)

    # set the output filename using the appropriate tcex api path
    out_path = gen.tap(type_).split('.') + [type_, f'{type_.singular()}.py']
    out_file = Path(os.path.join(*out_path))

    if not out_file.is_file():
        out_file.write_text('')

    # generate class method code first so that requirements can be determined
    container_methods = gen.gen_container_methods()
    object_methods = gen.gen_object_methods()

    _code = gen.gen_doc_string()
    _code += gen.gen_requirements()
    # add generated class (Artifact, Case, etc.)
    _code += gen.gen_object_class()
    _code += object_methods
    # add generated container class (Artifacts, Cases, etc.)
    _code += gen.gen_container_class()
    _code += container_methods

    with out_file.open(mode='w') as fh:
        fh.write(CodeOperation.format_code(_code))

    Render.panel.success(f'Successfully wrote {out_file}.')

    for msg in gen.messages:
        Render.panel.warning(msg)


#
# CLI
#


class ObjectTypes(str, Enum):
    """Object Types"""

    # shared
    tags = 'tags'

    # case management
    artifacts = 'artifacts'
    artifact_types = 'artifact_types'
    cases = 'cases'
    case_attributes = 'case_attributes'
    notes = 'notes'
    tasks = 'tasks'
    workflow_events = 'workflow_events'
    workflow_templates = 'workflow_templates'

    # intel requirements
    intel_requirements = 'intel_requirements'
    categories = 'categories'
    results = 'results'
    subtypes = 'subtypes'

    # security
    owner_roles = 'owner_roles'
    owners = 'owners'
    users = 'users'
    user_groups = 'user_groups'
    system_roles = 'system_roles'

    # threat intelligence
    attribute_types = 'attribute_types'
    group_attributes = 'group_attributes'
    groups = 'groups'
    indicator_attributes = 'indicator_attributes'
    indicators = 'indicators'
    security_labels = 'security_labels'
    victims = 'victims'
    victim_assets = 'victim_assets'
    victim_attributes = 'victim_attributes'


class GenTypes(str, Enum):
    """Object Types"""

    all = 'all'
    filter = 'filter'
    model = 'model'
    object = 'object'


app = typer.Typer()


@app.command()
def all(  # pylint: disable=redefined-builtin
    gen_type: GenTypes = typer.Option(
        'all', '--gen_type', help='Generate filter, model, or object file.'
    ),
):
    """Generate Args."""
    log_server()
    gen_type_ = gen_type.value.lower()
    for type_ in ObjectTypes:
        type_ = util.snake_string(type_.value)

        if gen_type_ in ['all', 'model']:
            gen_model(type_)
        if gen_type_ in ['all', 'filter']:
            gen_filter(type_)
        if gen_type_ in ['all', 'object']:
            gen_object(type_)


@app.command()
def args(
    type_: ObjectTypes = typer.Option(
        ..., '--type', help='Generate Args for the provided object type.'
    ),
    indent_blocks: int = typer.Option(
        1, help='The number of four space blocks to indent the args.'
    ),
):
    """Generate Args."""
    log_server()
    gen_args(util.snake_string(type_.value), indent_blocks)


@app.command()
def code(
    type_: ObjectTypes = typer.Option(
        ..., '--type', help='Generate filter, model, and object files for the provided type.'
    ),
):
    """Generate Args."""
    log_server()
    tv = util.snake_string(type_.value)
    gen_filter(tv)
    gen_model(tv)
    gen_object(tv)


@app.command()
def filter(  # pylint: disable=redefined-builtin
    type_: ObjectTypes = typer.Option(
        ..., '--type', help='Generate filter object file for the provided type.'
    ),
):
    """Generate the filter code."""
    log_server()
    gen_filter(util.snake_string(type_.value))


@app.command()
def model(
    type_: ObjectTypes = typer.Option(
        ..., '--type', help='Generate model file for the provided type.'
    ),
):
    """Generate the model"""
    log_server()
    gen_model(util.snake_string(type_.value))


@app.command()
def object(  # pylint: disable=redefined-builtin
    type_: ObjectTypes = typer.Option(
        ..., '--type', help='Generate object file for the provided type.'
    ),
):
    """Generate the filter class"""
    log_server()
    gen_object(util.snake_string(type_.value))


if __name__ == '__main__':
    app()
