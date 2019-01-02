# -*- coding: utf-8 -*-
"""ThreatConnect Playbook App"""

# Import default Playbook Class (Required)
from playbook_app import PlaybookApp


class App(PlaybookApp):
    """Playbook App"""

    def run(self):
        """Run the App main logic.

        This method should contain the core logic of the App.
        """

    def write_output(self):
        """Write the Playbook output variables.

        This method should be overridden with the output variables defined in the install.json
        configuration file.
        """
