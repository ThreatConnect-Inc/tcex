# -*- coding: utf-8 -*-
""" ThreatConnect Job App """

# Import default Job Class (Required)
from job_app import JobApp


class App(JobApp):
    """ Job App """

    # def __init__(self, _tcex):
    #     """ Initialize class properties.

    #     This method can be OPTIONALLY overridden.
    #     """
    #     super(App, self).__init__(_tcex)
    #     self.indicator_count = 0
    #     self.group_count = 0

    # def parse_args(self):
    #     """ Parse CLI args.

    #     This method can be OPTIONALLY overridden, but using the args.py file is best practice.
    #     """
    #     tcex.parser.add_argument('--tc_owner', required=True)
    #     tcex.parser.add_argument('--count_groups', action='store_true', default=False)
    #     self.args = self.tcex.args

    def count_indicators(self):
        """Count the indicators in the owner."""
        self.tcex.log.info('Counting indicators')

        resource = self.tcex.resource('Indicator')
        resource.owner = self.args.tc_owner
        for results in resource:
            if results.get('status') == 'Success':
                self.indicator_count += len(results.get('data'))
            else:
                message = 'Failed retrieving result during pagination.'
                self.tcex.log.error(message)

        self.tcex.log.info('Found {} indicators'.format(self.indicator_count))

    def count_groups(self):
        """Count the groups in the owner."""
        self.tcex.log.info('Counting groups')

        resource = self.tcex.resource('Group')
        resource.owner = self.args.tc_owner
        for results in resource:
            if results.get('status') == 'Success':
                self.group_count += len(results.get('data'))
            else:
                message = 'Failed retrieving result during pagination.'
                self.tcex.log.error(message)

        self.tcex.log.info('Found {} groups'.format(self.group_count))

    def run(self):
        """  Run the App main logic.

        This method should contain the core logic of the App.
        """
        self.tcex.log.info('Counting indicators in: {}'.format(self.args.tc_owner))

        # initialize the counts
        self.indicator_count = 0
        self.group_count = 0

        # count indicators
        self.count_indicators()

        # count the groups if appropriate
        if self.args.count_groups:
            self.count_groups()

        # output the results
        if self.args.count_groups:
            message = 'Found {} indicators and {} groups in {}'.format(self.indicator_count,
                                                                       self.group_count,
                                                                       self.args.tc_owner)
        else:
            message = 'Found {} indicators in {}'.format(self.indicator_count, self.args.tc_owner)

        self.exit_message = message
