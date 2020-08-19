from typing import Union, Iterable

from tcex.stix import StixModel


class Visitor:
    def visit(self, data: Iterable[dict]):
        """Loop over all data and perform any modifications.

        Args:
            data:  All of the parsed data.

        Returns:
            Generator of data, with any modifications.
        """
        for d in data:
            yield d


class RelationshipVisitor(Visitor):
    def __init__(self, target_id: str, source_id: str):
        super().__init__()
        self.target_id = target_id
        self.source_id = source_id

        self.target = None
        self.source = None

        self.done = False

    def visit(self, data: Iterable[dict]):
        for d in data:
            if self.done:
                yield d  # get out asap if we're done to reduce overhead.
            else:
                if d.get('xid') == self.target_id:
                    self.target = d
                if d.get('xid') == self.source_id:
                    self.source = d

                if self.target and self.source:  # if we've already found our targets...
                    if self._is_group(self.target) and self._is_group(self.source):
                        # both are groups:
                        self.target.setdefault('associatedGroupXid', []).append(self.source.get('xid'))
                        self.source.setdefault('associatedGroupXid', []).append(self.target.get('xid'))
                    elif self._is_group(self.target) and not self._is_group(self.source):
                        # source is an indicator, target is a group
                        self.source.setdefault('associatedGroups', []).append({'groupXid', self.target.get('xid')})
                    elif self._is_group(self.source) and not self._is_group(self.target):
                        # target is an indicator, source is a group
                        self.target.setdefault('associatedGroups', []).append({'groupXid', self.source.get('xid')})
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


class Relationship(StixModel):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def consume(self, stix_data: Union[list, dict]):
        if not isinstance(stix_data, list):
            stix_data = [stix_data]

        for data in stix_data:
            relationship = RelationshipVisitor(data.get('target_ref'), data.get('source_ref'))
            self.model.register_visitor(relationship)

