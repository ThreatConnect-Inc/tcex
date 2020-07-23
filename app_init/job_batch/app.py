# -*- coding: utf-8 -*-
"""ThreatConnect Job App"""
import csv

# Import default Job Class (Required)
from job_app import JobApp


class App(JobApp):
    """Job App"""

    def __init__(self, _tcex):
        """Initialize class properties."""
        super().__init__(_tcex)

        # properties
        self.batch = self.tcex.batch(self.args.tc_owner)
        self.session = None

    def setup(self):
        """Perform prep/setup logic."""
        # using tcex session_external to get built-in features (e.g., proxy, logging, retries)
        self.session = self.tcex.session_external

        # setting the base url allow for subsequent API call to be made by only
        # providing the API endpoint/path.
        self.session.base_url = 'https://feodotracker.abuse.ch'

    def run(self):
        """Run main App logic."""

        with self.session as s:
            r = s.get('downloads/malware_hashes.csv')

            if r.ok:
                decoded_content = r.content.decode('utf-8').splitlines()

                reader = csv.reader(decoded_content, delimiter=',', quotechar='"')
                for row in reader:
                    # CSV headers
                    # Firstseen,MD5hash,Malware

                    # skip comments
                    if row[0].startswith('#'):
                        continue

                    # create batch entry
                    indicator_value = row[1]
                    file_hash = self.batch.file(indicator_value, rating='4.0', confidence='100')
                    file_hash.tag(row[2])

                    # add occurrence to batch entry
                    occurrence = file_hash.occurrence()
                    occurrence.date = row[0]
                    self.batch.save(file_hash)  # optionally save object to disk
            else:
                self.tcex.exit(1, 'Failed to download CSV data.')

        # submit batch job
        batch_status = self.batch.submit_all()
        print(batch_status)

        self.exit_message = (  # pylint: disable=attribute-defined-outside-init
            'Downloaded data and create batch job.'
        )
