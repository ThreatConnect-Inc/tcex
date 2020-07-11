# -*- coding: utf-8 -*-
"""TcEx Error Codes"""


class TcExErrorCodes:
    """TcEx Framework Error Codes."""

    @property
    def errors(self):
        """Return TcEx defined error codes and messages.

        .. note:: RuntimeErrors with a code of >= 10000 are considered critical.  Those < 10000
            are considered warning or errors and are up to the developer to determine the
            appropriate behavior.
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
            # threat intelligence
            600: 'Failed adding group type "{}" with name "{}" ({}).',
            605: 'Failed adding attribute type "{}" with value "{}" to group id "{}" ({}).',
            610: 'Failed adding label "{}" to group id "{}" ({}).',
            615: 'Failed adding tag "{}" to group id "{}" ({}).',
            650: 'Failed adding label "{}" to attribute id "{}" ({}).',
            # metrics
            700: 'Failed to create metric. API status code: {}, API message: {}.',
            705: 'Error while finding metric by name. API status code: {}, API message: {}.',
            710: 'Failed to add metric data. API status code: {}, API message: {}.',
            715: 'No metric ID found for "{}".',
            # notifications
            750: 'Failed to send notification. API status code: {}, API message: {}.',
            # datastore
            800: 'Failed to create index. API status code: {}, API message: {}.',
            805: 'Failed to {} record data. API status code: {}, API message: {}.',
            # threat intelligence module
            905: 'Error during update. {} does not have a unique_id set and cannot be updated.',
            910: 'Error during get. {} does not have a unique_id set and cannot be fetched.',
            915: 'Error during delete. {} does not have a unique_id set and cannot be deleted.',
            920: (
                'Error during create. {} does not have required values set and cannot be '
                'created.'
            ),
            # TODO: fix this and all references
            925: 'Error invalid {}. {} does not accept that {}, {}: {}.',
            950: 'Error during pagination. API status code: {}, API message: {}, API Url: {}.',
            951: 'Error during {}. API status code: {}, API message: {}, API Url: {}.',
            952: 'Error during {}. API status code: {}, API message: {}, API Url: {}.',
            # batch v2 critical:
            10500: 'Critical batch error ({}).',
            10505: 'Failed submitting batch job requests ({}).',
            10510: 'Failed submitting batch job requests. API status code: {}, API message: {}.',
            10520: 'Failed submitting batch data ({}).',
            10525: 'Failed submitting batch data. API status code: {}, API message: {}.',
        }

    def message(self, code):
        """Return the error message.

        Args:
            code (integer): The error code integer.

        Returns:
            (string): The error message.
        """
        return self.errors.get(code)
