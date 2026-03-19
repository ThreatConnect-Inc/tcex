"""Module for various utilities for working with transforms created with Transform Builder."""

from collections.abc import Iterable
from typing import Literal

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
    ti_type: Literal['indicator', 'group'] | None = None,
) -> IndicatorTransformModel | GroupTransformModel:
    """Convert a transform from Transform Builder to one of the tcex transform models."""

    match transform:
        case {'transform': dict(), 'type': str()} as tb_v1:  # TB v1
            return transform_builder_to_model(tb_v1, processing_functions)  # type: ignore
        case _:  # TB v2
            match ti_type:
                case None:
                    msg = 'ti_type is required for Transform Builder v2 transforms'
                    raise ValueError(msg)
                case _:
                    return LoadTransform(processing_functions).load_transform(transform, ti_type)
