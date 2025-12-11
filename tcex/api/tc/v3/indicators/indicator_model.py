"""TcEx Framework Module"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, PrivateAttr, field_validator

from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class IndicatorModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra='allow',
    title='Indicator Model',
    validate_assignment=True,
):
    """Indicator Model"""

    _associated_type: bool = PrivateAttr(default=True)
    _cm_type: bool = PrivateAttr(default=False)
    _shared_type: bool = PrivateAttr(default=False)
    _staged: bool = PrivateAttr(default=False)

    active: bool | None = Field(
        default=None,
        description='Is the indicator active?',
        title='active',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    active_locked: bool | None = Field(
        default=None,
        description='Lock the indicator active value?',
        title='activeLocked',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    address: str | None = Field(
        default=None,
        description=(
            'The email address associated with this indicator (EmailAddress specific summary '
            'field).'
        ),
        title='address',
        validate_default=True,
        json_schema_extra={
            'applies_to': ['EmailAddress'],
            'conditional_required': ['EmailAddress'],
            'methods': ['POST'],
        },
    )
    associated_artifacts: ArtifactsModel | None = Field(
        default=None,
        description='A list of Artifacts associated with this Indicator.',
        title='associatedArtifacts',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    associated_cases: CasesModel | None = Field(
        default=None,
        description='A list of Cases associated with this Indicator.',
        title='associatedCases',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    associated_groups: GroupsModel | None = Field(
        default=None,
        description='A list of groups that this indicator is associated with.',
        title='associatedGroups',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    associated_indicators: IndicatorsModel | None = Field(
        default=None,
        description='A list of indicators associated with this indicator.',
        title='associatedIndicators',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    attributes: IndicatorAttributesModel | None = Field(
        default=None,
        description='A list of Attributes corresponding to the Indicator.',
        title='attributes',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    cal_score: int | None = Field(
        default=None,
        description='The CAL score for this indicator.',
        frozen=True,
        title='calScore',
        validate_default=True,
    )
    confidence: int | None = Field(
        default=None,
        description='The indicator threat confidence.',
        title='confidence',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    custom_association_names: list[str] | None = Field(
        default=None,
        description='The custom association names assigned to this indicator.',
        title='customAssociationNames',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    custom_associations: IndicatorsModel | None = Field(
        default=None,
        description='A list of indicators with custom associations to this indicator.',
        title='customAssociations',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    date_added: datetime | None = Field(
        default=None,
        description='The date and time that the item was first created.',
        frozen=True,
        title='dateAdded',
        validate_default=True,
    )
    description: str | None = Field(
        default=None,
        description='The indicator description text.',
        frozen=True,
        title='description',
        validate_default=True,
    )
    dns_active: bool | None = Field(
        default=None,
        description='Is dns active for the indicator?',
        title='dnsActive',
        validate_default=True,
        json_schema_extra={'applies_to': ['Host'], 'methods': ['POST', 'PUT']},
    )
    dns_resolution: dict | None = Field(
        default=None,
        description='Dns resolution data for the Host or Address indicator.',
        frozen=True,
        title='dnsResolution',
        validate_default=True,
        json_schema_extra={
            'applies_to': ['Host', 'Address'],
            'conditional_required': ['Host', 'Address'],
        },
    )
    enrichment: dict | None = Field(
        default=None,
        description='Enrichment data.',
        frozen=True,
        title='enrichment',
        validate_default=True,
    )
    external_date_added: datetime | None = Field(
        default=None,
        description='The date and time that the item was first created externally.',
        title='externalDateAdded',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    external_date_expires: datetime | None = Field(
        default=None,
        description='The date and time the item expires externally.',
        title='externalDateExpires',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    external_last_modified: datetime | None = Field(
        default=None,
        description='The date and time the item was modified externally.',
        title='externalLastModified',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    false_positive_flag: bool | None = Field(
        default=None,
        description='Is the indicator a false positive?',
        title='falsePositiveFlag',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    false_positive_reported_by_user: bool | None = Field(
        default=None,
        description='Has a false positive been reported by this user for this indicator today?',
        frozen=True,
        title='falsePositiveReportedByUser',
        validate_default=True,
    )
    false_positives: int | None = Field(
        default=None,
        description='The number of false positives reported for this indicator.',
        frozen=True,
        title='falsePositives',
        validate_default=True,
    )
    file_actions: FileActionsModel | None = Field(
        default=None,
        description='The type of file action associated with this indicator.',
        title='fileActions',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    file_occurrences: FileOccurrencesModel | None = Field(
        default=None,
        description='A list of file occurrences associated with this indicator.',
        title='fileOccurrences',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    first_seen: datetime | None = Field(
        default=None,
        description='The date and time that the item was first seen.',
        title='firstSeen',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    geo_location: dict | None = Field(
        default=None,
        description='Geographical localization of the Host or Address indicator.',
        frozen=True,
        title='geoLocation',
        validate_default=True,
        json_schema_extra={
            'applies_to': ['Host', 'Address'],
            'conditional_required': ['Host', 'Address'],
        },
    )
    host_name: str | None = Field(
        default=None,
        description='The host name of the indicator (Host specific summary field).',
        title='hostName',
        validate_default=True,
        json_schema_extra={
            'applies_to': ['Host'],
            'conditional_required': ['Host'],
            'methods': ['POST'],
        },
    )
    id: int | None = Field(  # type: ignore
        default=None,
        description='The ID of the item.',
        title='id',
        validate_default=True,
    )
    investigation_links: dict | None = Field(
        default=None,
        description=(
            'Resource links that provide additional information to assist in investigation.'
        ),
        frozen=True,
        title='investigationLinks',
        validate_default=True,
    )
    ip: str | None = Field(
        default=None,
        description=(
            'The ip address associated with this indicator (Address specific summary field).'
        ),
        title='ip',
        validate_default=True,
        json_schema_extra={
            'applies_to': ['Address'],
            'conditional_required': ['Address'],
            'methods': ['POST'],
        },
    )
    last_false_positive: datetime | None = Field(
        default=None,
        description='The date and time of the last false positive reported for this indicator.',
        frozen=True,
        title='lastFalsePositive',
        validate_default=True,
    )
    last_modified: datetime | None = Field(
        default=None,
        description='The date and time that the indicator was last modified.',
        frozen=True,
        title='lastModified',
        validate_default=True,
    )
    last_observed: datetime | None = Field(
        default=None,
        description='The date and time that the indicator was last observed.',
        frozen=True,
        title='lastObserved',
        validate_default=True,
    )
    last_seen: datetime | None = Field(
        default=None,
        description='The date and time that the item was last seen.',
        title='lastSeen',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    legacy_link: str | None = Field(
        default=None,
        description='A link to the legacy ThreatConnect details page for this entity.',
        frozen=True,
        title='legacyLink',
        validate_default=True,
    )
    md5: str | None = Field(
        default=None,
        description='The md5 associated with this indicator (File specific summary field).',
        title='md5',
        validate_default=True,
        json_schema_extra={'applies_to': ['File'], 'methods': ['POST', 'PUT']},
    )
    mode: str | None = Field(
        default=None,
        description='The operation to perform on the file hashes (delete | merge).',
        title='mode',
        validate_default=True,
        json_schema_extra={'applies_to': ['File'], 'methods': ['POST', 'PUT']},
    )
    observations: int | None = Field(
        default=None,
        description='The number of times this indicator has been observed.',
        title='observations',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    owner_id: int | None = Field(
        default=None,
        description='The id of the Organization, Community, or Source that the item belongs to.',
        title='ownerId',
        validate_default=True,
        json_schema_extra={'methods': ['POST']},
    )
    owner_name: str | None = Field(
        default=None,
        description='The name of the Organization, Community, or Source that the item belongs to.',
        title='ownerName',
        validate_default=True,
        json_schema_extra={'conditional_read_only': ['Victim'], 'methods': ['POST']},
    )
    private_flag: bool | None = Field(
        default=None,
        description='Is this indicator private?',
        title='privateFlag',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    rating: int | None = Field(
        default=None,
        description='The indicator threat rating.',
        title='rating',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    security_labels: SecurityLabelsModel | None = Field(
        default=None,
        description=(
            'A list of Security Labels corresponding to the Intel item (NOTE: Setting this '
            'parameter will replace any existing tag(s) with the one(s) specified).'
        ),
        title='securityLabels',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    sha1: str | None = Field(
        default=None,
        description='The sha1 associated with this indicator (File specific summary field).',
        title='sha1',
        validate_default=True,
        json_schema_extra={'applies_to': ['File'], 'methods': ['POST', 'PUT']},
    )
    sha256: str | None = Field(
        default=None,
        description='The sha256 associated with this indicator (File specific summary field).',
        title='sha256',
        validate_default=True,
        json_schema_extra={'applies_to': ['File'], 'methods': ['POST', 'PUT']},
    )
    size: int | None = Field(
        default=None,
        description='The size of the file.',
        title='size',
        validate_default=True,
        json_schema_extra={'applies_to': ['File'], 'methods': ['POST', 'PUT']},
    )
    source: str | None = Field(
        default=None,
        description='The source for this indicator.',
        frozen=True,
        title='source',
        validate_default=True,
    )
    summary: str | None = Field(
        default=None,
        description='The indicator summary.',
        frozen=True,
        title='summary',
        validate_default=True,
    )
    tags: TagsModel | None = Field(
        default=None,
        description=(
            'A list of Tags corresponding to the item (NOTE: Setting this parameter will replace '
            'any existing tag(s) with the one(s) specified).'
        ),
        title='tags',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    text: str | None = Field(
        default=None,
        description='The url text value of the indicator (Url specific summary field).',
        title='text',
        validate_default=True,
        json_schema_extra={
            'applies_to': ['URL'],
            'conditional_required': ['URL'],
            'methods': ['POST'],
        },
    )
    threat_assess_confidence: float | None = Field(
        default=None,
        description='The Threat Assess confidence for this indicator.',
        frozen=True,
        title='threatAssessConfidence',
        validate_default=True,
    )
    threat_assess_rating: float | None = Field(
        default=None,
        description='The Threat Assess rating for this indicator.',
        frozen=True,
        title='threatAssessRating',
        validate_default=True,
    )
    threat_assess_score: int | None = Field(
        default=None,
        description='The Threat Assess score for this indicator.',
        frozen=True,
        title='threatAssessScore',
        validate_default=True,
    )
    threat_assess_score_false_positive: int | None = Field(
        default=None,
        description='The Threat Assess score for false positives related to this indicator.',
        frozen=True,
        title='threatAssessScoreFalsePositive',
        validate_default=True,
    )
    threat_assess_score_observed: int | None = Field(
        default=None,
        description='The Threat Assess score observed for this indicator.',
        frozen=True,
        title='threatAssessScoreObserved',
        validate_default=True,
    )
    tracked_users: dict | None = Field(
        default=None,
        description='List of tracked users and their observation and false positive stats.',
        frozen=True,
        title='trackedUsers',
        validate_default=True,
    )
    type: str | None = Field(
        default=None,
        description='The **type** for the Indicator.',
        title='type',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    value1: str | None = Field(
        default=None,
        description='Custom Indicator summary field value1.',
        title='value1',
        validate_default=True,
        json_schema_extra={'methods': ['POST']},
    )
    value2: str | None = Field(
        default=None,
        description='Custom Indicator summary field value2.',
        title='value2',
        validate_default=True,
        json_schema_extra={'methods': ['POST']},
    )
    value3: str | None = Field(
        default=None,
        description='Custom Indicator summary field value3.',
        title='value3',
        validate_default=True,
        json_schema_extra={'methods': ['POST']},
    )
    web_link: str | None = Field(
        default=None,
        description='A link to the ThreatConnect details page for this entity.',
        frozen=True,
        title='webLink',
        validate_default=True,
    )
    whois: dict | None = Field(
        default=None,
        description='The whois data for the indicator.',
        frozen=True,
        title='whois',
        validate_default=True,
        json_schema_extra={'applies_to': ['Host'], 'conditional_required': ['Host']},
    )
    whois_active: bool | None = Field(
        default=None,
        description='Is whois active for the indicator?',
        title='whoisActive',
        validate_default=True,
        json_schema_extra={'applies_to': ['Host'], 'methods': ['POST', 'PUT']},
    )

    @field_validator('associated_artifacts', mode='before')
    @classmethod
    def _validate_artifacts(cls, v):
        if not v:
            return ArtifactsModel()  # type: ignore
        return v

    @field_validator('associated_cases', mode='before')
    @classmethod
    def _validate_cases(cls, v):
        if not v:
            return CasesModel()  # type: ignore
        return v

    @field_validator('file_actions', mode='before')
    @classmethod
    def _validate_file_actions(cls, v):
        if not v:
            return FileActionsModel()  # type: ignore
        return v

    @field_validator('file_occurrences', mode='before')
    @classmethod
    def _validate_file_occurrences(cls, v):
        if not v:
            return FileOccurrencesModel()  # type: ignore
        return v

    @field_validator('associated_groups', mode='before')
    @classmethod
    def _validate_groups(cls, v):
        if not v:
            return GroupsModel()  # type: ignore
        return v

    @field_validator('attributes', mode='before')
    @classmethod
    def _validate_indicator_attributes(cls, v):
        if not v:
            return IndicatorAttributesModel()  # type: ignore
        return v

    @field_validator('associated_indicators', 'custom_associations', mode='before')
    @classmethod
    def _validate_indicators(cls, v):
        if not v:
            return IndicatorsModel()  # type: ignore
        return v

    @field_validator('security_labels', mode='before')
    @classmethod
    def _validate_security_labels(cls, v):
        if not v:
            return SecurityLabelsModel()  # type: ignore
        return v

    @field_validator('tags', mode='before')
    @classmethod
    def _validate_tags(cls, v):
        if not v:
            return TagsModel()  # type: ignore
        return v


class IndicatorDataModel(
    BaseModel,
    title='Indicator Data Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Indicators Data Model"""

    data: list[IndicatorModel] | None = Field(
        [],
        description='The data for the Indicators.',
        title='data',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


class IndicatorsModel(
    BaseModel,
    title='Indicators Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Indicators Model"""

    _mode_support: bool = PrivateAttr(default=True)

    data: list[IndicatorModel] | None = Field(
        [],
        description='The data for the Indicators.',
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        title='append',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


from tcex.api.tc.v3.artifacts.artifact_model import ArtifactsModel
from tcex.api.tc.v3.cases.case_model import CasesModel
from tcex.api.tc.v3.file_actions.file_action_model import FileActionsModel
from tcex.api.tc.v3.file_occurrences.file_occurrence_model import FileOccurrencesModel
from tcex.api.tc.v3.groups.group_model import GroupsModel
from tcex.api.tc.v3.indicator_attributes.indicator_attribute_model import IndicatorAttributesModel
from tcex.api.tc.v3.security_labels.security_label_model import SecurityLabelsModel
from tcex.api.tc.v3.tags.tag_model import TagsModel
