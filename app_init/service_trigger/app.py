"""ThreatConnect Trigger Service App"""

# first-party
from service_app import ServiceApp  # Import default Service App Class (Required)


# pylint: disable=unused-argument
from tcex.playbooks import Playbooks


class App(ServiceApp):
    """Service App Template."""

    def run(self) -> None:
        """Run the trigger logic."""
        while self.tcex.service.loop_forever(sleep=30):
            # args defined in install.json/args.py with serviceConfig
            # are available in self.args namespace
            self.tcex.log.debug(f'Server configuration service_input {self.args.service_input}')

            # any "extra" args passed to fire_event will be
            # available in kwargs in the callback method
            self.tcex.service.fire_event(self.trigger_callback, my_data='data')

    def trigger_callback(
        self, playbook: Playbooks, trigger_id: int, config: dict, **kwargs
    ) -> None:
        """Execute trigger callback for all current configs.

        Args:
            playbook: An instance of Playbooks used to write output
                variables to be used in downstream Apps.
            trigger_id: The ID of the Playbook Trigger.
            config: The trigger input configuration data.

        Returns:
            bool: True if playbook should trigger, False if not.
        """
        # "extra" args passed to the fire_event method are available in kwargs
        my_data: str = kwargs.get('my_data')
        self.tcex.log.debug(f'my_data: {my_data}')

        # args defined in install.json with serviceConfig set to False are available in config
        self.tcex.log.debug(f"Playbook configuration playbook_input {config.get('playbook_input')}")

        # write output variable
        playbook.create_output('example.service_input', self.args.service_input)
        playbook.create_output('example.playbook_input', config.get('playbook_input'))
        return True
