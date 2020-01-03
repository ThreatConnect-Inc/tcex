# -*- coding: utf-8 -*-
"""Case Management PyTest Helper Method"""
from random import randint


class CMHelper:
    """Case Management Helper Module

    Args:
        cm (tcex.CaseManagement): A instantiated TC CaseManagement Object
    """

    def __init__(self, cm):
        """Initialize Class Properties"""
        self.cm = cm

        # cleanup values
        self.cases = []

    def create_case(self, **kwargs):
        """Create an case.

        If a case_name is not provide a dynamic case name will be used.

        Args:
            case_name (str, kwargs): Optional case name.
            case_severity (str, kwargs): Optional case severity.
            case_status (str, kwargs): Optional case status.
            case_xid (str, kwargs): Optional case XID.

        Returns:
            CaseManagement.Case: A CM case object.
        """
        name = kwargs.get('case_name') or f'Dummy-{randint(0,10_000)}'
        severity = kwargs.get('case_severity') or 'Low'
        status = kwargs.get('case_status') or 'Open'
        xid = kwargs.get('case_xid') or f'cm-xid-{randint(0,1_000_000)}'

        # create case
        case = self.cm.case(name=name, severity=severity, status=status, xid=xid)
        case.add_tag(name='pytest')
        case.submit()

        # store case id for cleanup
        self.cases.append(case)

        return case

    def create_artifact(self, **kwargs):
        """Create an artifact (and optional case)

        If case_id is provided the ID will be used, otherwise a case_name will be dynamically
        created in the create_case method.

        Args:
            artifact_intel_type (str, kwargs): Required artifact intel type field.
            artifact_summary (str, kwargs): Required artifact summary.
            artifact_type (str, kwargs): Required artifact type.
            case_id (str, kwargs): Optional case ID.
            case_name (str, kwargs): Optional case name.
            case_xid (str, kwargs): Optional case XID.

        Returns:
            CaseManagement.Artifact: A CM artifact object.
        """
        if kwargs.get('case_id'):
            case_id = kwargs.get('case_id')
        else:
            case = self.create_case(**kwargs)
            case_id = case.id

        intel_type = kwargs.get('artifact_intel_type')
        summary = kwargs.get('artifact_summary')
        type_ = kwargs.get('artifact_type')

        # create the artifact
        artifact = self.cm.artifact(
            case_id=case_id, intel_type=intel_type, summary=summary, type=type_
        )
        artifact.submit()

        return artifact

    def cleanup(self):
        """Remove all cases and child data."""
        for case in self.cases:
            case.delete()
