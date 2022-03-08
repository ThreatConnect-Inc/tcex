"""Layout JSON Model"""
# pylint: disable=no-self-argument,no-self-use; noqa: N805
# standard library
from collections import OrderedDict
from typing import Dict, List, Optional, Union

# third-party
from pydantic import BaseModel
from pydantic.types import constr

# first-party
from tcex.pleb.none_model import NoneModel

__all__ = ['LayoutJsonModel']


def snake_to_camel(snake_string: str) -> str:
    """Convert snake_case to camelCase"""
    components = snake_string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


class ParametersModel(BaseModel):
    """Model for layout_json.inputs.{}"""

    display: Optional[str]
    name: str

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class InputsModel(BaseModel):
    """Model for layout_json.inputs"""

    parameters: List[ParametersModel]
    sequence: int
    title: constr(min_length=3, max_length=100)

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class OutputsModel(BaseModel):
    """Model for layout_json.outputs"""

    display: Optional[str]
    name: str

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class LayoutJsonModel(BaseModel):
    """Layout JSON Model"""

    inputs: List[InputsModel]
    outputs: Optional[List[OutputsModel]]

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True

    def get_param(self, name: str) -> Union['NoneModel', 'ParametersModel']:
        """Return the param or a None Model."""
        return self.params.get(name) or NoneModel()

    def get_output(self, name: str) -> Union['NoneModel', 'OutputsModel']:
        """Return layout.json outputs in a flattened dict with name param as key."""
        return self.outputs_.get(name) or NoneModel()

    @property
    def outputs_(self) -> Dict[str, 'OutputsModel']:
        """Return layout.json outputs in a flattened dict with name param as key."""
        return {o.name: o for o in self.outputs}

    @property
    def param_names(self) -> list:
        """Return all param names in a single list."""
        return list(self.params.keys())

    @property
    def params(self) -> Dict[str, 'ParametersModel']:
        """Return layout.json params in a flattened dict with name param as key."""
        # return {p.name: p for i in self.inputs for p in i.parameters}

        # order is required for display clauses to be evaluated correctly
        parameters = OrderedDict()  # remove after python 3.7
        for i in self.inputs:
            for p in i.parameters:
                parameters.setdefault(p.name, p)
        return parameters
