from oslo_config import cfg

from webpage_listener.common import cli
from webpage_listener import listener

cli_opts = [
    cfg.ListOpt('list_of_urls',
                required=True,
                help='The list of urls to poll contents on'),
    cfg.IntOpt('polling_period',
               required=True,
               default=5*60,
               help='Interval to poll content from the pages'),
    cfg.StrOpt('hook_module',
               required=True,
               default='webpage_listener.hooks.email.mailgun.mailgunHook',
               help='Hook module to execute when change happens'),
    cfg.StrOpt('css_selector_expression',
               required=True,
               help='css selector expression to select the content on webpage')
]

CONF = cfg.CONF
CONF.register_cli_opts(cli_opts)
CONF(prog='web-pages-listener')


@cli.runnable
def run():
    listener.main(CONF.list_of_urls, CONF.css_selector_expression,
                  CONF.polling_period, CONF.hook_module, True)
