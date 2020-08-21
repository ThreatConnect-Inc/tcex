"""Visitor producer for STIX Relationship Object.

import stix2
from tcex.batch import Batch

see: https://docs.oasis-open.org/cti/stix/v2.1/csprd01/stix-v2.1-csprd01.html#_Toc16070673
"""
# standard library
from typing import Iterable, List, Union

# first-party
from tcex.stix import StixModel
from stix2 import Relationship
from tcex.stix.visitor import Visitor, VisitorProducer


class RelationshipVisitor(Visitor):
    """Visitor that creates associations between ThreatConnect objects based on a STIX Relationship.

    Args:
        target_ref: xid of TC object on one side of the association.
        source_ref: xid of the TC object on the other side of the association.
    """

    def __init__(self, target_ref: str, source_ref: str):
        super().__init__()
        self.target_ref = target_ref
        self.source_ref = source_ref

        self.target = None
        self.source = None

        self.done = False

    def visit(self, data: Iterable[dict]) -> Iterable[dict]:
        """Look for the parsed objects referred to by target_ref and source_ref and associate them.

         Associations an only be group->group or indicator->group.  Indicator-indicator associations
         are not supported.

         Args:
             data: generator of parsed data.

        Yields:
            parsed data with associations added.
         """
        for d in data:
            if self.done:
                yield d  # get out asap if we're done to reduce overhead.
            else:
                if d.get('xid') == self.target_ref:
                    self.target = d
                if d.get('xid') == self.source_ref:
                    self.source = d

                if self.target and self.source:  # if we've already found our targets...
                    if self._is_group(self.target) and self._is_group(self.source):
                        # both are groups:
                        self.target.setdefault('associatedGroupXid', []).append(
                            self.source.get('xid')
                        )
                        self.source.setdefault('associatedGroupXid', []).append(
                            self.target.get('xid')
                        )
                    elif self._is_group(self.target) and not self._is_group(self.source):
                        # source is an indicator, target is a group
                        self.source.setdefault('associatedGroups', []).append(
                            {'groupXid', self.target.get('xid')}
                        )
                    elif self._is_group(self.source) and not self._is_group(self.target):
                        # target is an indicator, source is a group
                        self.target.setdefault('associatedGroups', []).append(
                            {'groupXid', self.source.get('xid')}
                        )
                    else:
                        # TODO handle indicator-to-indicator, we can't do that in TC
                        pass

                    self.done = True

                    yield self.target
                    yield self.source
                else:
                    yield d

    @staticmethod
    def _is_group(d):
        return d.get('name') is not None


class Relationship(VisitorProducer):
    """Visitor producer for STIX Relationship Object.

    see: https://docs.oasis-open.org/cti/stix/v2.1/csprd01/stix-v2.1-csprd01.html#_Toc16070673

    Args:
        model: StixModel instance to register visitor on.
    """

    def consume(self, stix_data: Union[List[dict], dict]) -> Visitor:
        """Register a visitor to create ThreatConnect associations for STIX relationship.

        Args:
            stix_data: One or more STIX Relationship objects.
        """
        if not isinstance(stix_data, list):
            stix_data = [stix_data]

        for data in stix_data:
            return RelationshipVisitor(data.get('target_ref'), data.get('source_ref'))

    def produce(self, tc_data: Union[list, dict]):
        if not isinstance(tc_data, list):
            tc_data = [tc_data]

        for data in tc_data:
            associations = data.pop('associations', [])
            for association in associations:
                yield stix2.Relationship(
                    source_ref=Batch.generate_xid(data.get('summary')),
                    target_ref=Batch.generate_xid(association.get('summary')),
                    relationship_type='uses'
                )

