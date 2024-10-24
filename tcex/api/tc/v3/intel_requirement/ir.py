"""TcEx Framework Module"""

# third-party
from requests import Session

# first-party
from tcex.api.tc.v3.intel_requirements.categories.category import Categories, Category
from tcex.api.tc.v3.intel_requirements.intel_requirement import IntelRequirement, IntelRequirements
from tcex.api.tc.v3.intel_requirements.results.result import Result, Results
from tcex.api.tc.v3.intel_requirements.subtypes.subtype import Subtype, Subtypes


class IR:
    """Intel Requirement

    Args:
        session: An configured instance of request.Session with TC API Auth.
    """

    def __init__(self, session: Session):
        """Initialize instance properties."""
        self.session = session

    def categories(self, **kwargs) -> Categories:
        """Return a instance of Categories object."""
        return Categories(session=self.session, **kwargs)

    def category(self, **kwargs) -> Category:
        """Return a instance of Category object."""
        return Category(session=self.session, **kwargs)

    def intel_requirement(self, **kwargs) -> IntelRequirement:
        """Return a instance of Intel Requirement object."""
        return IntelRequirement(session=self.session, **kwargs)

    def intel_requirements(self, **kwargs) -> IntelRequirements:
        """Return a instance of Intel Requirements object."""
        return IntelRequirements(session=self.session, **kwargs)

    def result(self, **kwargs) -> Result:
        """Return a instance of Result object."""
        return Result(session=self.session, **kwargs)

    def results(self, **kwargs) -> Results:
        """Return a instance of Results object."""
        return Results(session=self.session, **kwargs)

    def subtype(self, **kwargs) -> Subtype:
        """Return a instance of Subtype object."""
        return Subtype(session=self.session, **kwargs)

    def subtypes(self, **kwargs) -> Subtypes:
        """Return a instance of Subtypes object."""
        return Subtypes(session=self.session, **kwargs)
