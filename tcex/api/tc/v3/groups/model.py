"""Group / Groups Model"""
# standard library
from datetime import datetime
from typing import Optional, List

# third-party
from pydantic import BaseModel, Extra, Field, validator

# first-party
from tcex.utils import Utils


class GroupsModel(
    BaseModel,
    title='Groups Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Groups Model"""

    data: Optional[List['GroupModel']] = Field(
        [],
        description='The data for the Groups.',
        methods=['POST', 'PUT'],
        title='data',
    )


class GroupDataModel(
    BaseModel,
    title='Group Data Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Groups Data Model"""

    data: Optional[List['GroupModel']] = Field(
        [],
        description='The data for the Groups.',
        methods=['POST', 'PUT'],
        title='data',
    )


class GroupModel(
    BaseModel,
    title='Group Model',
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    validate_assignment=True,
):
    """Group Model"""

    associated_groups: Optional['GroupsModel'] = Field(
        None,
        description='A list of groups associated with this group.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='associatedGroups',
    )
    associated_indicators: Optional['IndicatorsModel'] = Field(
        None,
        description='A list of indicators associated with this group.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='associatedIndicators',
    )
    attributes: Optional['AttributesModel'] = Field(
        None,
        description='A list of Attributes corresponding to the Group.',
        methods=['POST', 'PUT'],
        max_size=1000,
        read_only=False,
        title='attributes',
    )
    body: Optional[str] = Field(
        None,
        description='The email Body.',
        methods=['POST', 'PUT'],
        max_length=65535,
        min_length=0,
        read_only=False,
        title='body',
    )
    created_by: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **created by** for the Group.',
        read_only=True,
        title='createdBy',
    )
    date_added: Optional[datetime] = Field(
        None,
        allow_mutation=False,
        description='The date and time that the item was first created.',
        read_only=True,
        title='dateAdded',
    )
    document_date_added: Optional[datetime] = Field(
        None,
        description='The date and time that the document was first created.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='documentDateAdded',
    )
    document_type: Optional[str] = Field(
        None,
        description='The document type.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='documentType',
    )
    email_date: Optional[datetime] = Field(
        None,
        description='The date and time that the email was first created.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='emailDate',
    )
    event_date: Optional[datetime] = Field(
        None,
        description='The date and time that the incident or event was first created.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='eventDate',
    )
    file_name: Optional[str] = Field(
        None,
        description='The document or signature file name.',
        methods=['POST', 'PUT'],
        max_length=100,
        min_length=0,
        read_only=False,
        title='fileName',
    )
    file_size: Optional[int] = Field(
        None,
        description='The document file size.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='fileSize',
    )
    file_text: Optional[str] = Field(
        None,
        description='The signature file text.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='fileText',
    )
    file_type: Optional[str] = Field(
        None,
        description='The signature file type.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='fileType',
    )
    first_seen: Optional[datetime] = Field(
        None,
        description='The date and time that the campaign was first created.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='firstSeen',
    )
    from_: Optional[str] = Field(
        None,
        alias='from',
        description='The email From field.',
        methods=['POST', 'PUT'],
        max_length=100,
        min_length=0,
        read_only=False,
        title='from_',
    )
    handles: Optional['AdversaryAssetsModel'] = Field(
        None,
        description=(
            'A list of handle adversary assets associated with this group (Adversary specific).'
        ),
        methods=['POST', 'PUT'],
        read_only=False,
        title='handles',
    )
    header: Optional[str] = Field(
        None,
        description='The email Header field.',
        methods=['POST', 'PUT'],
        max_length=65535,
        min_length=0,
        read_only=False,
        title='header',
    )
    id: Optional[int] = Field(
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    malware: bool = Field(
        None,
        description='Is the document malware?.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='malware',
    )
    name: Optional[str] = Field(
        None,
        description='The name of the group.',
        methods=['POST', 'PUT'],
        max_length=100,
        min_length=0,
        read_only=False,
        title='name',
    )
    password: Optional[str] = Field(
        None,
        description='The password associated with the docuement.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='password',
    )
    phone_numbers: Optional['AdversaryAssetsModel'] = Field(
        None,
        description=(
            'A list of phone number adversary assets associated with this group (Adversary '
            'specific).'
        ),
        methods=['POST', 'PUT'],
        read_only=False,
        title='phoneNumbers',
    )
    publish_date: Optional[datetime] = Field(
        None,
        description='The date and time that the report was first created.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='publishDate',
    )
    published_file_name: Optional[str] = Field(
        None,
        description='The document published file name.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='publishedFileName',
    )
    score: Optional[int] = Field(
        None,
        description='The score value for this email.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='score',
    )
    score_breakdown: Optional[str] = Field(
        None,
        description='The email score breakdown.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='scoreBreakdown',
    )
    score_includes_body: bool = Field(
        None,
        description='Is the Body included in the email score?.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='scoreIncludesBody',
    )
    security_labels: Optional['SecurityLabelsModel'] = Field(
        None,
        description=(
            'A list of Security Labels corresponding to the Intel item (NOTE: Setting this '
            'parameter will replace any existing tag(s) with the one(s) specified).'
        ),
        methods=['POST', 'PUT'],
        max_size=1000,
        read_only=False,
        title='securityLabels',
    )
    signature_date_added: Optional[datetime] = Field(
        None,
        description='The date and time that the signature was first created.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='signatureDateAdded',
    )
    status: Optional[str] = Field(
        None,
        description='The status associated with this document, event, or incident.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='status',
    )
    subject: Optional[str] = Field(
        None,
        description='The email Subject section.',
        methods=['POST', 'PUT'],
        max_length=255,
        min_length=0,
        read_only=False,
        title='subject',
    )
    tags: Optional['TagsModel'] = Field(
        None,
        description=(
            'A list of Tags corresponding to the item (NOTE: Setting this parameter will replace '
            'any existing tag(s) with the one(s) specified).'
        ),
        methods=['POST', 'PUT'],
        max_size=1000,
        read_only=False,
        title='tags',
    )
    to: Optional[str] = Field(
        None,
        description='The email To field .',
        methods=['POST', 'PUT'],
        read_only=False,
        title='to',
    )
    type: Optional[str] = Field(
        None,
        description='The **type** for the Group.',
        methods=['POST', 'PUT'],
        min_length=1,
        read_only=False,
        title='type',
    )
    urls: Optional['AdversaryAssetsModel'] = Field(
        None,
        description=(
            'A list of url adversary assets associated with this group (Adversary specific).'
        ),
        methods=['POST', 'PUT'],
        read_only=False,
        title='urls',
    )

    @validator('urls', always=True)
    def _validate_urls(cls, v):
        if not v:
            return AdversaryAssetsModel()
        return v

    @validator('attributes', always=True)
    def _validate_attributes(cls, v):
        if not v:
            return AttributesModel()
        return v

    @validator('associated_groups', always=True)
    def _validate_associated_groups(cls, v):
        if not v:
            return GroupsModel()
        return v

    @validator('associated_indicators', always=True)
    def _validate_associated_indicators(cls, v):
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
from tcex.api.tc.v3.adversary_assets.model import AdversaryAssetsModel
from tcex.api.tc.v3.case_management.models.attribute_model import AttributesModel
from tcex.api.tc.v3.indicators.model import IndicatorsModel
from tcex.api.tc.v3.security_labels.model import SecurityLabelsModel
from tcex.api.tc.v3.tags.model import TagsModel

# add forward references
GroupDataModel.update_forward_refs()
GroupModel.update_forward_refs()
GroupsModel.update_forward_refs()
