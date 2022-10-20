"""API -> TC"""
# standard library
from typing import TYPE_CHECKING, Dict, List, Union

# first-party
from tcex.api.tc.ti_transform import TiTransform, TiTransforms
from tcex.api.tc.ti_transform.model import GroupTransformModel, IndicatorTransformModel
from tcex.api.tc.v2.v2 import V2
from tcex.api.tc.v3.v3 import V3
from tcex.backports import cached_property

if TYPE_CHECKING:
    # third-party
    from requests import Session

    # first-party
    from tcex.input.input import Input


class TC:
    """API -> TC

    Args:
        inputs: An instance of the Input class.
        session_tc: An configured instance of request.Session with TC API Auth.
    """

    def __init__(self, inputs: 'Input', session_tc: 'Session'):
        """Initialize Class properties."""
        self.inputs = inputs
        self.session_tc = session_tc

    @staticmethod
    def group_transform(transform: Dict) -> 'GroupTransformModel':
        """Return a group transform model."""
        return GroupTransformModel(**transform)

    @staticmethod
    def indicator_transform(transform: Dict) -> 'IndicatorTransformModel':
        """Return a indicator transform model."""
        return IndicatorTransformModel(**transform)

    @staticmethod
    def ti_transform(
        ti_dict: dict,
        transforms: List[Union['GroupTransformModel', 'IndicatorTransformModel']],
    ) -> 'TiTransform':
        """Return an instance of TI Transform class."""
        return TiTransform(ti_dict, transforms)

    @staticmethod
    def ti_transforms(
        ti_dict: List[dict],
        transforms: List[Union['GroupTransformModel', 'IndicatorTransformModel']],
    ) -> 'TiTransform':
        """Return an instance of TI Transforms class."""
        return TiTransforms(ti_dict, transforms)

    @cached_property
    def v2(self) -> 'V2':
        """Return a case management instance."""
        return V2(self.inputs, self.session_tc)

    @cached_property
    def v3(self) -> 'V3':
        """Return a case management instance."""
        return V3(self.session_tc)
