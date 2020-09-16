"""Defines Visitor and VisitorPattern for STIX or TC Objects.

Visitor and Visitor producer should be used when parsing isn't a simple mapping from the source
format to the target format, and instead needs to modify the result of other parsers. For example,
A STIX Relationship object defines and association between two other objects.
"""
# standard library
from typing import Iterable, List, Union


class Visitor:
    """Visitors receive the final generator of parsed data from StixModel and can modify members.

    StixModel -[]-[]-[]-[]--> |VISITOR A| -[X]-[]-[X]--> |VISITOR B| -[XY]-[Y]-[X]--> Caller
    """

    def visit(self, data: Iterable[dict]) -> Iterable[dict]:  # pylint: disable=no-self-use
        """Receive the final generator of parsed data from StixModel, and optionally modify it.

        Args:
            data:  All of the parsed data.

        Returns:
            Generator of data, with any modifications.
        """
        yield from data


class VisitorProducer:
    """Creates and returns a visitor."""

    def consume(
        self, stix_data: Union[List[dict], dict]
    ) -> Iterable[Visitor]:  # pylint: disable=no-self-use
        """Parse STIX data and return a Visitor.

        Args:
            stix_data: One or more STIX objects to parse.

        Returns:
            A visitor that will apply the data parsed from the STIX objects to final parsed objects
            generator.
        """

    def produce(
        self, tc_data: Union[List[dict], dict]
    ) -> Iterable[Visitor]:  # pylint: disable=no-self-use
        """Parse ThreatConnect data and return a Visitor.

        Args:
            tc_data: One or more ThreatConnect objects to parse.

        Returns:
            A visitor that will apply the data parsed from the ThreatConnect object(s) to final
            parsed objects generator.
        """
