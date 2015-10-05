#!/bin/bash

import logging
import time

import lxml.html
import requests
from oslo_config import cfg

import selector

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


# set up log. Right now only defaulted to a hard coded web-pages-listener.log,
# I know.
logging.basicConfig(filename='web-pages-listener.log',
                    level=logging.DEBUG)


def string_non_ascii(s):
    return ''.join([x for x in 'YOUR_STRING' if ord(x) < 128])


def on_Change(hook_module_string, url, previous_content, new_content):
    hook_m = __import__(hook_module_string, globals(), locals(), ['hook'], -1)
    # hard code subject for now.
    subject = "I posted something new..."
    previous_content = previous_content or []
    new_content = [string_non_ascii(s) for s in new_content]
    content = ("%s has something changed: \n"
               "Old: %s,\n"
               "New: %s"
               "Frederick Jones"
               ) % (url, previous_content, new_content)
    hook_m.hook().do_action(subject, content)


def poll(url, css_selector_expression):
    response = requests.get(url)
    tree = lxml.html.fromstring(response.text)

    # get the selector
    sel = selector.get_css_selector(css_selector_expression)
    selected_elements = sel(tree)
    return selected_elements


def main(list_of_urls, css_selector_expression,
         polling_period,
         hook_module_string,
         on_change_from_none=False):
    previous_content = {url: None for url in list_of_urls}
    while True:
        for url in list_of_urls:
            logging.info('Scraping url: %s' % url)
            selected_elements = poll(url, css_selector_expression)
            now_content = []
            for selected_element in selected_elements:
                now_content.append(selected_element.text)
            if previous_content[url] != now_content:
                logging.info('Previous content: %s' % previous_content[url])
                logging.info('Now content: %s' % now_content)
                if previous_content[url] is None and not on_change_from_none:
                    previous_content[url] = now_content
                    continue
                else:
                    logging.info('Starting to executing hooks...')
                    on_Change(hook_module_string,
                              url,
                              previous_content[url],
                              now_content)
                    previous_content[url] = now_content
        time.sleep(polling_period)


if __name__ == '__main__':
    CONF = cfg.CONF
    CONF.register_cli_opts(cli_opts)
    CONF(prog='web-pages-listener')

    main(CONF.list_of_urls, CONF.css_selector_expression, CONF.polling_period,
         CONF.hook_module)
