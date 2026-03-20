"""Module for various utilities for working with transforms created with Transform Builder."""

# standard library
from collections.abc import Iterable
from typing import Literal

# first-party
from tcex.api.tc.ti_transform.model.transform_model import (
    GroupTransformModel,
    IndicatorTransformModel,
)
from tcex.api.tc.ti_transform.ti_predefined_functions import (
    ProcessingFunctions,
    transform_builder_to_model,
)
from tcex.api.tc.ti_transform.transform_builder.v2.load_transform import LoadTransform


def load(
    transform: dict,
    processing_functions: 'ProcessingFunctions',
) -> IndicatorTransformModel | GroupTransformModel:  # type: ignore
    """Convert a transform from Transform Builder to one of the tcex transform models."""

    match transform:
        case {'transform': dict(), 'type': str()}:  # TB v1
            return transform_builder_to_model(transform, processing_functions, internal_call=True)  # type: ignore
        case {'metadata': {'threatIntelType': str()}}:  # TB v2
            return LoadTransform(processing_functions).load_transform(transform)

    ex_msg = 'Unrecognized transform format.'
    raise ValueError(ex_msg)
