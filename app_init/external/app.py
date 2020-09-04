"""ThreatConnect External App"""

# first-party
from external_app import ExternalApp  # Import default External App Class (Required)


class App(ExternalApp):
    """External App"""

    def run(self) -> None:
        """Run the App main logic.

        This method should contain the core logic of the App.
        """
