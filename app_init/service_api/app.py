"""ThreatConnect API Service App"""
# third-party
import falcon

# first-party
from api_service_app import ApiServiceApp  # Import default API Service Class (Required)

from tcex import TcEx


class TcExMiddleware:
    """TcEx middleware module.

    Adds access to self.args, self.tcex and self.log in resource Class.

    """

    def __init__(self, args: object, tcex: TcEx):
        """Initialize class properties.

        Args:
            args: The argparser arg namespace.
            tcex: An instance of tcex
        """
        self.args = args
        self.tcex = tcex

        # properties
        self.log = tcex.log

    def process_resource(  # pylint: disable=no-self-use,unused-argument
        self, req: falcon.Request, resp: falcon.Response, resource: object, params: dict
    ):
        """Process resource method."""
        resource.args = self.args
        resource.log = self.log
        resource.tcex = self.tcex


class OneResource:
    """Handle request to /one endpoint."""

    # provided by TcEx middleware
    args = None
    log = None
    tcex = None

    def on_get(self, req, resp):  # pylint: disable=no-self-use,unused-argument
        """Handle GET requests"""
        data = {'data': 'one'}
        resp.media = data


class TwoResource:
    """Handle request to /two endpoint."""

    # provided by TcEx middleware
    args = None
    log = None
    tcex = None

    def on_get(self, req, resp):  # pylint: disable=no-self-use,unused-argument
        """Handle GET requests"""
        data = {'data': 'two'}
        resp.media = data


class App(ApiServiceApp):
    """API Service App"""

    def __init__(self, _tcex):
        """Initialize class properties."""
        super().__init__(_tcex)

        # create Falcon API with tcex middleware
        self.api = falcon.API(middleware=[TcExMiddleware(args=self.args, tcex=self.tcex)])

        # Add routes
        self.api.add_route('/one', OneResource())
        self.api.add_route('/two', TwoResource())
        self.tcex.log.trace(f'args: {self.tcex.args}')

    def api_event_callback(self, environ, response_handler):
        """Run the trigger logic."""
        return self.api(environ, response_handler)
