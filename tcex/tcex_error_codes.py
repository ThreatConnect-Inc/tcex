# -*- coding: utf-8 -*-
""" TcEx Error Codes """

class TcExErrorCodes(object):
    """TcEx Framework Error Codes."""

    @property
    def errors(self):
        """TcEx defined error codes and messages.

        .. note:: RuntimeErrors with a code of >= 1000 are considered critical.  Those < 1000
            are considered warning or errors and are up to the developer to determine the appropriate
            behavior.
        """
        return {
            # tcex general errors
            100: 'Generic error. See log for more details ({}).',
            105: 'Required Module is not installed ({}).',
            200: 'Failed retrieving Custom Indicator Associations types from API ({}).',
            210: 'Failure during token renewal ({}).',
            215: 'HMAC authorization requires a PreparedRequest Object.',
            220: 'Failed retrieving indicator types from API ({}).',
            # tcex resource
            300: 'Failed retrieving Bulk JSON ({}).',
            305: 'An invalid action/association name ({}) was provided.',
            350: 'Data Store request failed. API status code: {}, API message: {}.',
            # batch v2: 500-600
            520: 'File Occurrences can only be added to a File. Current type: {}.',
            540: 'Failed polling batch status ({}).',
            545: 'Failed polling batch status. API status code: {}, API message: {}.',
            550: 'Batch status check reached timeout ({} seconds).',
            560: 'Failed retrieving batch errors ({}).',
            580: 'Failed posting file data ({}).',
            585: 'Failed posting file data. API status code: {}, API message: {}.',
            590: 'No hash values provided.',
            # metrics
            700: 'Failed to create metric. API status code: {}, API message: {}.',
            705: 'Error while finding metric by name. API status code: {}, API message: {}.',
            710: 'Failed to add metric data. API status code: {}, API message: {}.',
            715: 'No metric ID found for "{}".',
            # batch v2 critical: 1500-1600
            1500: 'Critical batch error ({}).',
            1505: 'Failed submitting batch job requests ({}).',
            1510: 'Failed submitting batch job requests. API status code: {}, API message: {}.',
            1520: 'Failed submitting batch data ({}).',
            1525: 'Failed submitting batch data. API status code: {}, API message: {}.',
        }

    def message(self, code):
        """Return the error message.

        Args:
            code (integer): The error code integer.

        Returns:
            (string): The error message.
        """
        return self.errors.get(code)
