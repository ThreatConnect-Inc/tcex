"""Threat Intelligence Transform Module"""
# standard library
import traceback
from typing import Optional

# first-party
from tcex.api.tc.ti_transform.model import GroupTransformModel, IndicatorTransformModel
from tcex.api.tc.ti_transform.transform_abc import TransformABC, TransformsABC


class TiTransforms(TransformsABC):
    """Mappings"""

    def process(self):
        """Process the mapping."""
        for ti_dict in self.ti_dicts:
            self.transformed_collection.append(TiTransform(ti_dict, self.transforms))

    @property
    def batch(self) -> dict:
        """Return the data in batch format."""
        self.process()

        batch = {
            'group': [],
            'indicator': [],
        }
        for t in self.transformed_collection:
            # batch must be called so that the transform type is selected
            try:
                data = t.batch
            except Exception as ex:
                # LOG WARNING
                print(f'feature=ti-transforms, event=transform-error, error="{ex}"')
                print(traceback.format_exc())
                continue

            # now that batch is called we can identify the ti type
            if isinstance(t.transform, GroupTransformModel):
                batch['group'].append(data)
            elif isinstance(t.transform, IndicatorTransformModel):
                batch['indicator'].append(data)
        return batch


class TiTransform(TransformABC):
    """Threat Intelligence Transform Module"""

    def add_associated_group(self, group_xid: str):
        """Add an associated group.

        {
            'associatedGroups': [
                {
                    'groupXid': 'dd78f2b94ac61d3e5a55c1223a7635db00cd0aaa8aba26c5306e36dd6c1662ee'}
        """
        # process type specific data
        if isinstance(self.transform, GroupTransformModel):
            self.transformed_item.setdefault('associatedGroupXid', []).append(group_xid)
        elif isinstance(self.transform, IndicatorTransformModel):
            associated_group = {'groupXid': group_xid}
            self.transformed_item.setdefault('associatedGroups', []).append(associated_group)

    def add_attribute(
        self,
        type_: str,
        value: str,
        displayed: Optional[bool] = False,
        source: Optional[str] = None,
    ):
        """Add an attribute to the transformed item."""
        if type_ is not None and value is not None:
            attribute_data = {
                'type': type_,
                'value': value,
            }

            # displayed is a special case, it only needs to be added if True
            if displayed is True:
                attribute_data['displayed'] = displayed

            # source is a special case, it only needs to be added if not None
            if source is not None:
                attribute_data['source'] = source

            self.transformed_item.setdefault('attribute', []).append(attribute_data)

    def add_confidence(self, confidence: Optional[int]):
        """Add a rating to the transformed item."""
        if confidence is not None:
            self.transformed_item['confidence'] = int(confidence)

    def add_metadata(self, key: str, value: str):
        """Add name to the transformed item."""
        if all([key, value]):
            self.transformed_item[key] = value

    def add_name(self, name: Optional[str]):
        """Add name to the transformed item."""
        if name is not None:
            self.transformed_item['name'] = name

    def add_rating(self, rating: Optional[int]):
        """Add a rating to the transformed item."""
        if rating is not None:
            self.transformed_item['rating'] = float(rating)

    def add_security_label(
        self, name: str, color: Optional[str] = None, description: Optional[str] = None
    ):
        """Add a tag to the transformed item."""
        if name is not None:
            label_data = {'name': name}

            if color is not None:
                label_data['color'] = color

            if description is not None:
                label_data['description'] = description

            self.transformed_item.setdefault('securityLabel', []).append(label_data)

    def add_summary(self, value: Optional[str]):
        """Add value1 to the transformed item."""
        if value is not None:
            self.transformed_item['summary'] = value

    def add_tag(self, name: str):
        """Add a tag to the transformed item."""
        if name is not None:
            self.transformed_item.setdefault('tag', []).append({'name': name})

    @property
    def batch(self) -> dict:
        """Return the data in batch format."""
        self._process()
        return dict(sorted(self.transformed_item.items()))
