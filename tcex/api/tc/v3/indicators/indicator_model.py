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
        read_only=False,
        title='confidence',
    )
    custom_association_name: Optional[str] = Field(
        None,
        description='The custom association name if assigned to this indicator.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='customAssociationName',
    )
    custom_associations: Optional['IndicatorsModel'] = Field(
        None,
        description='A list of indicators with custom associations to this indicator.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='customAssociations',
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
    dns_resolution: Optional[dict] = Field(
        None,
        allow_mutation=False,
        applies_to=['Host', 'Address'],
        conditional_required=['Host', 'Address'],
        description='Dns resolution data for the Host or Address indicator.',
        read_only=True,
        title='dnsResolution',
    )
    enrichment: Optional[dict] = Field(
        None,
        allow_mutation=False,
        description='Enrichment data.',
        read_only=True,
        title='enrichment',
    )
    external_date_added: Optional[datetime] = Field(
        None,
        description='The date and time that the item was first created externally.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='externalDateAdded',
    )
    external_date_expires: Optional[datetime] = Field(
        None,
        description='The date and time the item expires externally.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='externalDateExpires',
    )
    external_last_modified: Optional[datetime] = Field(
        None,
        description='The date and time the item was modified externally.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='externalLastModified',
    )
    false_positive_reported_by_user: bool = Field(
        None,
        allow_mutation=False,
        description='Has a false positive been reported by this user for this indicator today?',
        read_only=True,
        title='falsePositiveReportedByUser',
    )
    false_positives: Optional[int] = Field(
        None,
        allow_mutation=False,
        description='The number of false positives reported for this indicator.',
        read_only=True,
        title='falsePositives',
    )
    file_actions: Optional['FileActionsModel'] = Field(
        None,
        description='The type of file action associated with this indicator.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='fileActions',
    )
    file_occurrences: Optional['FileOccurrencesModel'] = Field(
        None,
        description='A list of file occurrences associated with this indicator.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='fileOccurrences',
    )
    first_seen: Optional[datetime] = Field(
        None,
        description='The date and time that the item was first seen.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='firstSeen',
    )
    geo_location: Optional[dict] = Field(
        None,
        allow_mutation=False,
        applies_to=['Host', 'Address'],
        conditional_required=['Host', 'Address'],
        description='Geographical localization of the Host or Address indicator.',
        read_only=True,
        title='geoLocation',
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
    investigation_links: Optional[dict] = Field(
        None,
        allow_mutation=False,
        description=(
            'Resource links that provide additional information to assist in investigation.'
        ),
        read_only=True,
        title='investigationLinks',
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
    last_seen: Optional[datetime] = Field(
        None,
        description='The date and time that the item was last seen.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='lastSeen',
    )
    legacy_link: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='A link to the legacy ThreatConnect details page for this entity.',
        read_only=True,
        title='legacyLink',
    )
    md5: Optional[str] = Field(
        None,
        applies_to=['File'],
        description='The md5 associated with this indicator (File specific summary field).',
        methods=['POST', 'PUT'],
        read_only=False,
        title='md5',
    )
    mode: Optional[str] = Field(
        None,
        applies_to=['File'],
        description='The operation to perform on the file hashes (delete | merge).',
        methods=['POST', 'PUT'],
        read_only=False,
        title='mode',
    )
    observations: Optional[int] = Field(
        None,
        allow_mutation=False,
        description='The number of times this indicator has been observed.',
        read_only=True,
        title='observations',
    )
    owner_id: Optional[int] = Field(
        None,
        description='The id of the Organization, Community, or Source that the item belongs to.',
        methods=['POST'],
        read_only=False,
        title='ownerId',
    )
    owner_name: Optional[str] = Field(
        None,
        description='The name of the Organization, Community, or Source that the item belongs to.',
        methods=['POST'],
        read_only=False,
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
        methods=['POST', 'PUT'],
        read_only=False,
        title='sha1',
    )
    sha256: Optional[str] = Field(
        None,
        applies_to=['File'],
        description='The sha256 associated with this indicator (File specific summary field).',
        methods=['POST', 'PUT'],
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
    threat_assess_score_false_positive: Optional[int] = Field(
        None,
        allow_mutation=False,
        description='The Threat Assess score for false positives related to this indicator.',
        read_only=True,
        title='threatAssessScoreFalsePositive',
    )
    threat_assess_score_observed: Optional[int] = Field(
        None,
        allow_mutation=False,
        description='The Threat Assess score observed for this indicator.',
        read_only=True,
        title='threatAssessScoreObserved',
    )
    tracked_users: Optional[dict] = Field(
        None,
        allow_mutation=False,
        description='List of tracked users and their observation and false positive stats.',
        read_only=True,
        title='trackedUsers',
    )
    type: Optional[str] = Field(
        None,
        description='The **type** for the Indicator.',
        methods=['POST', 'PUT'],
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
        description='A link to the ThreatConnect details page for this entity.',
        read_only=True,
        title='webLink',
    )
    whois: Optional[dict] = Field(
        None,
        allow_mutation=False,
        applies_to=['Host'],
        conditional_required=['Host'],
        description='The whois data for the indicator.',
        read_only=True,
        title='whois',
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

    @validator('file_actions', always=True)
    def _validate_file_actions(cls, v):
        if not v:
            return FileActionsModel()
        return v

    @validator('file_occurrences', always=True)
    def _validate_file_occurrences(cls, v):
        if not v:
            return FileOccurrencesModel()
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

    @validator('associated_indicators', 'custom_associations', always=True)
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
from tcex.api.tc.v3.file_actions.file_action_model import FileActionsModel
from tcex.api.tc.v3.file_occurrences.file_occurrence_model import FileOccurrencesModel
from tcex.api.tc.v3.groups.group_model import GroupsModel
from tcex.api.tc.v3.indicator_attributes.indicator_attribute_model import IndicatorAttributesModel
from tcex.api.tc.v3.security_labels.security_label_model import SecurityLabelsModel
from tcex.api.tc.v3.tags.tag_model import TagsModel

# add forward references
IndicatorDataModel.update_forward_refs()
IndicatorModel.update_forward_refs()
IndicatorsModel.update_forward_refs()
