import bson
from functools import wraps
import pkg_resources

from docket import grants
from docket import orders
from docket import slipopinions

from clint.textui import puts, colored
from cement.core.foundation import CementApp
from cement.ext.ext_logging import LoggingLogHandler
from cement.core.controller import CementBaseController, expose

VERSION = pkg_resources.get_distribution('nyt-docket').version
LOG_FORMAT = '%(asctime)s (%(levelname)s) %(namespace)s (v{0}) : \
%(message)s'.format(VERSION)
BANNER = "NYT Docket version {0}".format(VERSION)


class DocketBaseController(CementBaseController):
    class Meta:
        label = 'base'
        description = "Get and process Supreme Court opinions, \
        grants and orders."
        arguments = [
            (['term'], dict(
                nargs='*',
                action='store',
                help='Term year as a four-digit number, e.g., 2008. Remember \
                that term years represent the year the term began, not ended.'
            )),
            (['--format-json'], dict(
                action='store_true',
                help='Pretty print JSON when using `-o json`.'
            )),
            (['-v', '--version'], dict(
                action='version',
                version=BANNER
            )),
        ]

    @expose(hide=True)
    def default(self):
        """
        Print help
        """
        self.app.args.print_help()

    @expose(help="Get opinions")
    def opinions(self):
        """
        Initialize opinions
        """
        self.app.log.info(
            'Getting opinions for term {0}'.format(
                self.app.pargs.term[0]
            )
        )
        l = slipopinions.Load(terms=[self.app.pargs.term[0]])
        l.scrape()
        data = l.cases
        self.app.render(data)

    @expose(help="Get grants")
    def grants(self):
        """
        Initialize grants
        """
        self.app.log.info(
            'Getting grants for term {0}'.format(
                self.app.pargs.term[0]
            )
        )
        l = grants.Load(terms=[self.app.pargs.term[0]])
        l.scrape()
        data = l.cases
        self.app.render(data)

    @expose(help="Get orders")
    def orders(self):
        """
        Initialize orders
        """
        self.app.log.info(
            'Getting orders for term {0}'.format(
                self.app.pargs.term[0]
            )
        )
        l = orders.Load(terms=[self.app.pargs.term[0]])
        l.scrape()
        l.parse()
        data = l.orders
        self.app.render(data)

class DocketApp(CementApp):
    class Meta:
        label = 'docket'
        base_controller = DocketBaseController
        hooks = []
        extensions = [
            'docket.ext_csv',
            'docket.ext_json'
        ]
        output_handler = 'csv'
        handler_override_options = dict(
            output=(['-o'], dict(help='output format (default: csv)')),
        )
        log_handler = LoggingLogHandler(
            console_format=LOG_FORMAT,
            file_format=LOG_FORMAT
        )


def main():
    with DocketApp() as app:
        app.run()