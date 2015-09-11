import logging

from oslo_config import cfg
import requests

from webpage_listener.hooks.email import base


logger = logging.getLogger('mailgun-hook-log')
ch = logging.StreamHandler()
ch_format = logging.Formatter('%(asctime)s - %(message)s')
ch.setFormatter(ch_format)
logger.addHandler(ch)


MAILGUN_CONFIG_OPTIONS = [
    cfg.StrOpt('mailgun_api_key',
               help='Mail gun secret API Key'),
    cfg.IntOpt('retry_send', default=5,
               help='Mailgun send retry'),
    cfg.StrOpt('mailgun_request_url',
               help='Mail gun request url'),
    cfg.StrOpt('sand_box',
               help='Mail gun sand box domain'),
    cfg.StrOpt('from_address', default='noreply@weblistener.org',
               help='Sent from email address'),
    cfg.ListOpt('recipients',
                help='A list of emails addresses to receive notification ')
]

MAILGUN_CONFIG_GROUP = 'mailgun_config'


class mailgunHook(base.emailHookBase):

    def __init__(self):
        self.conf = cfg.CONF
        self.conf.register_opts(MAILGUN_CONFIG_OPTIONS,
                                MAILGUN_CONFIG_GROUP)
        self.mail_notification_conf = self.conf[MAILGUN_CONFIG_GROUP]

        self.mailgun_api_key = self.mail_notification_conf.mailgun_api_key
        self.retry_send = self.mail_notification_conf.retry_send
        self.mailgun_request_url = (
            self.mail_notification_conf.mailgun_request_url)
        self.sand_box = self.mail_notification_conf.sand_box
        self.from_address = self.mail_notification_conf.from_address
        self.recipients = self.mail_notification_conf.recipients

    def do_action(self, subject, mail_content):
        request_url = self.mailgun_request_url.format(self.sand_box)
        response_status_code = None
        attempt = 1

        while response_status_code != 200 and self.retry_send != attempt:
            logger.info("Sending email notification attempt: %s" %
                        str(attempt))
            response = requests.post(
                request_url,
                auth=('api', self.mailgun_api_key),
                data={
                    'from': self.from_address,
                    'to': self.recipients,
                    'subject': subject,
                    'text': mail_content
                }
            )
            print response_status_code
            response_status_code = response.status_code
            attempt += 1

        if response_status_code != 200:
            logger.warning("Send email notification failed. Details:"
                           "From: %s"
                           "To: %s"
                           "Subject: %s"
                           "Content: %s" % (self.from_address,
                                            self.recipients,
                                            subject,
                                            mail_content))
            return False
        else:
            return True
