import unittest

import mock
import requests
from oslo_config import cfg

from webpage_listener.hooks.email.mailgun import mailgunHook

MAILGUN_CONFIG_OPTIONS = [
    cfg.StrOpt('mailgun_api_key',
               default ='<my_fake_api_key>',
               help='Mail gun secret API Key'),
    cfg.IntOpt('retry_send', default=5,
               help='Mailgun send retry'),
    cfg.StrOpt('mailgun_request_url',
               default = 'http://123.com/{0}',
               help='Mail gun request url'),
    cfg.StrOpt('sand_box',
               default ='<my_fake_sand_box_domain>',
               help='Mail gun sand box domain'),
    cfg.StrOpt('from_address', default='noreply@weblistener.org',
               help='Sent from email address'),
    cfg.ListOpt('recipients',
                default=['1@a.com', '2@b.com'],
                help='A list of emails addresses to receive notification ')
]

MAILGUN_CONFIG_GROUP = 'mailgun_config'


class TestmailgunHook(unittest.TestCase):
    
    @mock.patch.object(mailgunHook, 'MAILGUN_CONFIG_OPTIONS',
                       new=MAILGUN_CONFIG_OPTIONS)
    def setUp(self):
        self.mh = mailgunHook.mailgunHook()
    
    @mock.patch.object(requests, 'post', new=mock.Mock())
    def test_mailgun_hook_do_action(self):
        request_url = self.mh.mailgun_request_url.format(self.mh.sand_box)
        auth = ('api', self.mh.mailgun_api_key)
        subject = "A Subject"
        mail_content = "Some random text"
        data = {
            'from': self.mh.from_address,
            'to': self.mh.recipients,
            'subject': subject,
            'text': mail_content
        }
        
        requests.post.return_value = mock.Mock(status_code=200)
        self.mh.do_action(subject, mail_content)
        requests.post.assert_called_once_with(request_url, auth=auth, 
                                              data=data)
