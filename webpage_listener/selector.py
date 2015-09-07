import lxml.cssselect


def get_css_selector(expression):
    return lxml.cssselect.CSSSelector(expression)