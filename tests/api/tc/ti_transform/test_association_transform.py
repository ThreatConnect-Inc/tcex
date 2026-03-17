"""TcEx Framework Module"""

# standard library
import json
from pathlib import Path

# third-party
import deepdiff

# first-party
from tcex import TcEx
from tcex.api.tc.ti_transform.model.transform_model import (
    AssociationTransformModel,
    GroupToGroupAssociation,
    GroupToIndicatorAssociation,
    IndicatorToIndicatorAssociation,
)


def transform(tcex: TcEx) -> IndicatorTransformModel:
    """Create transform for indicator regression test."""
    return AssociationTransformModel(associations=[
        GroupToIndicatorAssociation(xid={'default': '123'}, indicator_value={'default': 'foo.com'}, indicator_type={'default': 'HOST'}),
        GroupToGroupAssociation(xid_1={'default': '123'}, xid_2={'default': '456'}),
        IndicatorToIndicatorAssociation(
            indicator_value_1={'default': 'foo.com'},
            indicator_type_1={'default': 'HOST'},
            indicator_value_2={'default': 'bar.com'},
            indicator_type_2={'default': 'HOST'},
            custom_association_type={'default': 'related-to'},
        ),])


def test_indicators_file_occurrence(tcex: TcEx):
    """Test file occurrence transforms."""
    data = [
        {
            'summary': '032AA7E4C76F747BE6ABFC8345FDDBB2FFB591AF',
            'type': 'File',
            'relations': [
                {'path': '/foo/bar', 'when': 'Jan 12 2002'},
                {'name': 'bad.exe'},
                {'path': '/bash/bang'},
            ],
        }
    ]

    transforms = tcex.api.tc.ti_transforms(data, [transform(tcex)])

    print(json.dumps(transforms.batch, indent=4))

    assert not deepdiff.DeepDiff(
        transforms.batch,
        {
            'group': [],
            'indicator': [],
            'association': [
                {
                    'ref_1': '123',
                    'ref_2': 'foo.com',
                    'type_2': 'HOST'
                },
                {
                    'ref_1': '123',
                    'ref_2': '456'
                },
                {
                    'ref_1': 'foo.com',
                    'type_1': 'HOST',
                    'ref_2': 'bar.com',
                    'type_2': 'HOST',
                    'association_type': 'related-to'
                }
            ]
        },
    )
