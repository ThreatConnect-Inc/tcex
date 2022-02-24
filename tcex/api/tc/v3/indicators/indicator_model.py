"""Indicator / Indicators Model"""
# pylint: disable=no-member,no-self-argument,no-self-use,wrong-import-position
# standard library
from datetime import datetime
from typing import List, Optional

# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr, validator

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.utils import Utils


class IndicatorsModel(
    BaseModel,
    title='Indicators Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Indicators Model"""

    _mode_support = PrivateAttr(True)

    data: Optional[List['IndicatorModel']] = Field(
        [],
        description='The data for the Indicators.',
        methods=['POST', 'PUT'],
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        methods=['POST', 'PUT'],
        title='append',
    )


class IndicatorDataModel(
    BaseModel,
    title='Indicator Data Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Indicators Data Model"""

    data: Optional[List['IndicatorModel']] = Field(
        [],
        description='The data for the Indicators.',
        methods=['POST', 'PUT'],
        title='data',
    )


class IndicatorModel(
    V3ModelABC,
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    title='Indicator Model',
    validate_assignment=True,
):
    """Indicator Model"""

    _associated_type = PrivateAttr(True)
    _cm_type = PrivateAttr(False)
    _shared_type = PrivateAttr(False)
    _staged = PrivateAttr(False)

    active: bool = Field(
        None,
        description='Is the indicator active?',
        methods=['POST', 'PUT'],
        read_only=False,
        title='active',
    )
    active_locked: bool = Field(
        None,
        description='Lock the indicator active value?',
        methods=['POST', 'PUT'],
        read_only=False,
        title='activeLocked',
    )
    address: Optional[str] = Field(
        None,
        applies_to=['EmailAddress'],
        conditional_required=['EmailAddress'],
        description=(
            'The email address associated with this indicator (EmailAddress specific summary '
            'field).'
        ),
        methods=['POST'],
        read_only=False,
        title='address',
    )
    associated_artifacts: Optional['ArtifactsModel'] = Field(
        None,
        description='A list of Artifacts associated with this Indicator.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='associatedArtifacts',
    )
    associated_cases: Optional['CasesModel'] = Field(
        None,
        description='A list of Cases associated with this Indicator.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='associatedCases',
    )
    associated_groups: Optional['GroupsModel'] = Field(
        None,
        description='A list of groups that this indicator is associated with.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='associatedGroups',
    )
    associated_indicators: Optional['IndicatorsModel'] = Field(
        None,
        description='A list of indicators associated with this indicator.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='associatedIndicators',
    )
    attributes: Optional['IndicatorAttributesModel'] = Field(
        None,
        description='A list of Attributes corresponding to the Indicator.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='attributes',
    )
    confidence: Optional[int] = Field(
        None,
        description='The indicator threat confidence.',
        methods=['POST', 'PUT'],
        maximum=100,
        minimum=0,
        read_only=False,
        title='confidence',
    )
    date_added: Optional[datetime] = Field(
        None,
        allow_mutation=False,
        description='The date and time that the item was first created.',
        read_only=True,
        title='dateAdded',
    )
    description: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The indicator description text.',
        read_only=True,
        title='description',
    )
    dns_active: bool = Field(
        None,
        applies_to=['Host'],
        description='Is dns active for the indicator?',
        methods=['POST', 'PUT'],
        read_only=False,
        title='dnsActive',
    )
    false_positives: Optional[int] = Field(
        None,
        allow_mutation=False,
        description='The number of false positives reported for this indicator.',
        read_only=True,
        title='falsePositives',
    )
    host_name: Optional[str] = Field(
        None,
        applies_to=['Host'],
        conditional_required=['Host'],
        description='The host name of the indicator (Host specific summary field).',
        methods=['POST'],
        read_only=False,
        title='hostName',
    )
    id: Optional[int] = Field(
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    ip: Optional[str] = Field(
        None,
        applies_to=['Address'],
        conditional_required=['Address'],
        description=(
            'The ip address associated with this indicator (Address specific summary field).'
        ),
        methods=['POST'],
        read_only=False,
        title='ip',
    )
    last_false_positive: Optional[datetime] = Field(
        None,
        allow_mutation=False,
        description='The date and time of the last false positive reported for this indicator.',
        read_only=True,
        title='lastFalsePositive',
    )
    last_modified: Optional[datetime] = Field(
        None,
        allow_mutation=False,
        description='The date and time that the indicator was last modified.',
        read_only=True,
        title='lastModified',
    )
    last_observed: Optional[datetime] = Field(
        None,
        allow_mutation=False,
        description='The date and time that the indicator was last observed.',
        read_only=True,
        title='lastObserved',
    )
    md5: Optional[str] = Field(
        None,
        applies_to=['File'],
        description='The md5 associated with this indicator (File specific summary field).',
        methods=['POST'],
        read_only=False,
        title='md5',
    )
    observations: Optional[int] = Field(
        None,
        allow_mutation=False,
        description='The number of times this indicator has been observed.',
        read_only=True,
        title='observations',
    )
    owner_name: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The name of the Organization, Community, or Source that the item belongs to.',
        read_only=True,
        title='ownerName',
    )
    private_flag: bool = Field(
        None,
        description='Is this indicator private?',
        methods=['POST', 'PUT'],
        read_only=False,
        title='privateFlag',
    )
    rating: Optional[int] = Field(
        None,
        description='The indicator threat rating.',
        methods=['POST', 'PUT'],
        maximum=5,
        minimum=0,
        read_only=False,
        title='rating',
    )
    security_labels: Optional['SecurityLabelsModel'] = Field(
        None,
        description=(
            'A list of Security Labels corresponding to the Intel item (NOTE: Setting this '
            'parameter will replace any existing tag(s) with the one(s) specified).'
        ),
        methods=['POST', 'PUT'],
        read_only=False,
        title='securityLabels',
    )
    sha1: Optional[str] = Field(
        None,
        applies_to=['File'],
        description='The sha1 associated with this indicator (File specific summary field).',
        methods=['POST'],
        read_only=False,
        title='sha1',
    )
    sha256: Optional[str] = Field(
        None,
        applies_to=['File'],
        description='The sha256 associated with this indicator (File specific summary field).',
        methods=['POST'],
        read_only=False,
        title='sha256',
    )
    size: Optional[int] = Field(
        None,
        applies_to=['File'],
        description='The size of the file.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='size',
    )
    source: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The source for this indicator.',
        read_only=True,
        title='source',
    )
    summary: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The indicator summary.',
        read_only=True,
        title='summary',
    )
    tags: Optional['TagsModel'] = Field(
        None,
        description=(
            'A list of Tags corresponding to the item (NOTE: Setting this parameter will replace '
            'any existing tag(s) with the one(s) specified).'
        ),
        methods=['POST', 'PUT'],
        read_only=False,
        title='tags',
    )
    text: Optional[str] = Field(
        None,
        applies_to=['URL'],
        conditional_required=['URL'],
        description='The url text value of the indicator (Url specific summary field).',
        methods=['POST'],
        read_only=False,
        title='text',
    )
    threat_assess_confidence: Optional[float] = Field(
        None,
        allow_mutation=False,
        description='The Threat Assess confidence for this indicator.',
        read_only=True,
        title='threatAssessConfidence',
    )
    threat_assess_rating: Optional[float] = Field(
        None,
        allow_mutation=False,
        description='The Threat Assess rating for this indicator.',
        read_only=True,
        title='threatAssessRating',
    )
    threat_assess_score: Optional[int] = Field(
        None,
        allow_mutation=False,
        description='The Threat Assess score for this indicator.',
        read_only=True,
        title='threatAssessScore',
    )
    type: Optional[str] = Field(
        None,
        description='The **type** for the Indicator.',
        methods=['POST', 'PUT'],
        min_length=1,
        read_only=False,
        title='type',
    )
    value1: Optional[str] = Field(
        None,
        description='Custom Indicator summary field value1.',
        methods=['POST'],
        read_only=False,
        title='value1',
    )
    value2: Optional[str] = Field(
        None,
        description='Custom Indicator summary field value2.',
        methods=['POST'],
        read_only=False,
        title='value2',
    )
    value3: Optional[str] = Field(
        None,
        description='Custom Indicator summary field value3.',
        methods=['POST'],
        read_only=False,
        title='value3',
    )
    web_link: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The object link.',
        read_only=True,
        title='webLink',
    )
    whois_active: bool = Field(
        None,
        applies_to=['Host'],
        description='Is whois active for the indicator?',
        methods=['POST', 'PUT'],
        read_only=False,
        title='whoisActive',
    )

    @validator('associated_artifacts', always=True)
    def _validate_artifacts(cls, v):
        if not v:
            return ArtifactsModel()
        return v

    @validator('associated_cases', always=True)
    def _validate_cases(cls, v):
        if not v:
            return CasesModel()
        return v

    @validator('associated_groups', always=True)
    def _validate_groups(cls, v):
        if not v:
            return GroupsModel()
        return v

    @validator('attributes', always=True)
    def _validate_indicator_attributes(cls, v):
        if not v:
            return IndicatorAttributesModel()
        return v

    @validator('associated_indicators', always=True)
    def _validate_indicators(cls, v):
        if not v:
            return IndicatorsModel()
        return v

    @validator('security_labels', always=True)
    def _validate_security_labels(cls, v):
        if not v:
            return SecurityLabelsModel()
        return v

    @validator('tags', always=True)
    def _validate_tags(cls, v):
        if not v:
            return TagsModel()
        return v


# first-party
from tcex.api.tc.v3.artifacts.artifact_model import ArtifactsModel
from tcex.api.tc.v3.cases.case_model import CasesModel
from tcex.api.tc.v3.groups.group_model import GroupsModel
from tcex.api.tc.v3.indicator_attributes.indicator_attribute_model import IndicatorAttributesModel
from tcex.api.tc.v3.security_labels.security_label_model import SecurityLabelsModel
from tcex.api.tc.v3.tags.tag_model import TagsModel

# add forward references
IndicatorDataModel.update_forward_refs()
IndicatorModel.update_forward_refs()
IndicatorsModel.update_forward_refs()
