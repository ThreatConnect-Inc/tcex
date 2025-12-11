"""TcEx Framework Module"""

# standard library
import json


class Association:
    """ThreatConnect Batch Indicator Object"""

    __slots__ = ['association_type', 'id_1', 'id_2', 'ref_1', 'ref_2', 'type_1', 'type_2']

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        self.association_type = kwargs.get('association_type') or kwargs.get('associationType')
        self.ref_1 = kwargs.get('ref_1')
        self.type_1 = kwargs.get('type_1')
        self.id_1 = kwargs.get('id_1')
        self.ref_2 = kwargs.get('ref_2')
        self.type_2 = kwargs.get('type_2')
        self.id_2 = kwargs.get('id_2')

    @property
    def data(self) -> dict:
        """Return Indicator data."""
        # add attributes
        association = {
            'associationType': self.association_type,
            'ref_1': self.ref_1,
            'type_1': self.type_1,
            'id_1': self.id_1,
            'ref_2': self.ref_2,
            'type_2': self.type_2,
            'id_2': self.id_2,
        }
        return {k: v for k, v in association.items() if v is not None}

    def _normalized_data(self) -> dict:
        """Return normalized data for the association."""
        # Combine the ref, type, and id values into tuples
        combined = [(self.ref_1, self.type_1, self.id_1), (self.ref_2, self.type_2, self.id_2)]
        # Sort the combined tuples
        sorted_combined = sorted(combined, key=lambda x: (x[0] is None, x[0], x[1], x[2]))
        # Create the association dictionary using the sorted values
        association = {
            'associationType': self.association_type,
            'ref_1': sorted_combined[0][0],
            'type_1': sorted_combined[0][1],
            'id_1': sorted_combined[0][2],
            'ref_2': sorted_combined[1][0],
            'type_2': sorted_combined[1][1],
            'id_2': sorted_combined[1][2],
        }
        # Remove any None values from the dictionary
        return {k: v for k, v in association.items() if v is not None}

    def __eq__(self, other):
        """Check if two Association objects are equal."""
        if not isinstance(other, Association):
            return NotImplemented
        return self._normalized_data() == other._normalized_data()

    def __hash__(self):
        """Return hash for the object."""
        return hash(tuple(self._normalized_data().items()))

    def __str__(self) -> str:
        """Return string representation of the object."""
        return json.dumps(self.data, indent=4)
