"""TcEx Framework Module"""

# standard library
from datetime import datetime

# first-party
from tcex.api.tc.ti_transform.model import GroupTransformModel, IndicatorTransformModel
from tcex.api.tc.ti_transform.transform_abc import (
    NoValidTransformException,
    TransformABC,
    TransformException,
    TransformsABC,
)


class TiTransforms(TransformsABC):
    """Mappings"""

    def process(self):
        """Process the mapping."""
        self.transformed_collection: list[TiTransform] = []
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
        self.log.trace(f'feature=ti-transform-batch, ti-count={len(self.transformed_collection)}')
        for index, t in enumerate(self.transformed_collection):
            if index and index % 1_000 == 0:
                self.log.trace(f'feature=ti-transform-batch, items={index}')

            # batch must be called so that the transform type is selected
            try:
                data = t.batch
            except NoValidTransformException:
                self.log.exception('feature=ti-transforms, event=runtime-error')
                continue
            except TransformException as e:
                self.log.warning(
                    f'feature=ti-transforms, event=transform-error, field="{e.field}", '
                    f'cause="{e.cause}", context="{e.context}"'
                )
                if self.raise_exceptions:
                    raise
                continue
            except Exception:
                self.log.exception('feature=ti-transforms, event=transform-error')
                if self.raise_exceptions:
                    raise
                continue

            # now that batch is called we can identify the ti type
            if isinstance(t.transform, GroupTransformModel):
                batch['group'].append(data)
            elif isinstance(t.transform, IndicatorTransformModel):
                batch['indicator'].append(data)

            # append adhoc groups and indicators
            batch['group'].extend(t.adhoc_groups)
            batch['indicator'].extend(t.adhoc_indicators)
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
        displayed: bool = False,
        pinned: bool = False,
        source: str | None = None,
    ):
        """Add an attribute to the transformed item."""
        if type_ is not None and value is not None:
            attribute_data: dict[str, bool | str] = {
                'type': type_,
                'value': value,
            }

            # displayed is a special case, it only needs to be added if True
            if displayed is True:
                attribute_data['displayed'] = displayed

            # pinned is a special case, it only needs to be added if True
            if pinned is True:
                attribute_data['pinned'] = displayed

            # source is a special case, it only needs to be added if not None
            if source is not None:
                attribute_data['source'] = source

            self.transformed_item.setdefault('attribute', []).append(attribute_data)

    def add_file_occurrence(
        self,
        file_name: str | None = None,
        path: str | None = None,
        date: datetime | None = None,
    ):
        """Abstract method"""
        self.transformed_item.setdefault('fileOccurrence', []).append(
            {
                k: v
                for k, v in {
                    'fileName': file_name,
                    'path': path,
                    'date': date,
                }.items()
                if v
            }
        )

    def add_confidence(self, confidence: int | str | None):
        """Add a rating to the transformed item."""
        if confidence is not None:
            self.transformed_item['confidence'] = int(confidence)

    def add_group(self, group_data: dict):
        """Add a group to the transforms.

        Group data must match the format of the endpoint being used, (e.g., batch format
        for batch endpoints, v3 format for v3 endpoints).
        """
        self.adhoc_groups.append(group_data)

    def add_indicator(self, indicator_data: dict):
        """Add a indicator to the transforms.

        Indicator data must match the format of the endpoint being used, (e.g., batch format
        for batch endpoints, v3 format for v3 endpoints).
        """
        self.adhoc_indicators.append(indicator_data)

    def add_metadata(self, key: str, value: str):
        """Add name to the transformed item."""
        if all([key, value]):
            self.transformed_item[key] = value

    def add_name(self, name: str | None):
        """Add name to the transformed item."""
        if name is not None:
            self.transformed_item['name'] = name

    def add_rating(self, rating: float | int | str | None):
        """Add a rating to the transformed item."""
        if rating is not None:
            self.transformed_item['rating'] = float(rating)

    def add_security_label(
        self, name: str, color: str | None = None, description: str | None = None
    ):
        """Add a tag to the transformed item."""
        if name is not None:
            label_data = {'name': name}

            if color is not None:
                label_data['color'] = color

            if description is not None:
                label_data['description'] = description

            self.transformed_item.setdefault('securityLabel', []).append(label_data)

    def add_summary(self, value: str | None):
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
