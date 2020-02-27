# -*- coding: utf-8 -*-
"""ThreatConnect Job App"""
import csv

# Import default Job Class (Required)
from external_app import ExternalApp


class App(ExternalApp):
    """External App"""

    def __init__(self, _tcex):
        """Initialize class properties."""
        super().__init__(_tcex)
        self.batch = None
        self.url = 'https://feodotracker.abuse.ch/downloads/malware_hashes.csv'

    def run(self):
        """Run main App logic."""
        self.batch = self.tcex.batch(self.args.tc_owner)

        # using tcex requests to get built-in features (e.g., proxy, logging, retries)
        with self.tcex.session_external as s:
            r = s.get(self.url)

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
                    file_hash = self.batch.file(row[1], rating='4.0', confidence='100')
                    file_hash.tag(row[2])
                    occurrence = file_hash.occurrence()
                    occurrence.date = row[0]
                    self.batch.save(file_hash)  # optionally save object to disk
            else:
                self.tcex.exit(1, 'Failed to download CSV data.')

        # submit batch job(s)
        batch_status = self.batch.submit_all()
        self.tcex.log.debug(batch_status)

        # self.exit_message = f'Downloaded and created {self.batch.indicator_len} file hashes.'
