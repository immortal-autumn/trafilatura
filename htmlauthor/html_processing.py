import logging
import re

from lxml import etree
from lxml.html.clean import Cleaner

from .utils import trim

# HTML_CLEANER config
# https://lxml.de/api/lxml.html.clean.Cleaner-class.html
# https://lxml.de/apidoc/lxml.html.clean.html
HTML_CLEANER = Cleaner(
    annoying_tags=False,  # True
    comments=True,
    embedded=False,  # True
    forms=False,  # True
    frames=False,  # True
    javascript=False,
    links=False,
    meta=False,
    page_structure=False,
    processing_instructions=True,
    remove_unknown_tags=False,
    safe_attrs_only=False,
    scripts=False,
    style=False,
    # remove_tags = MANUALLY_STRIPPED,
    # kill_tags = MANUALLY_CLEANED,
)

# order could matter, using lists to keep extraction deterministic
MANUALLY_CLEANED = [
    # important
    'aside', 'embed', 'footer', 'form', 'head', 'iframe', 'menu', 'object',
    # other content
    'applet', 'audio', 'canvas', 'figure', 'map', 'picture', 'svg', 'video',
    # secondary
    'area', 'blink', 'button', 'datalist', 'dialog',
    'frame', 'frameset', 'fieldset', 'input', 'ins', 'label', 'legend',
    'marquee', 'math', 'menuitem', 'nav', 'noscript', 'optgroup', 'option',
    'output', 'param', 'progress', 'rp', 'rt', 'rtc', 'select', 'source',
    'style', 'track', 'template', 'textarea', 'time', 'use',
]
# 'meta', 'hr', 'img', 'data', 'details', 'summary'

MANUALLY_STRIPPED = [
    'abbr', 'acronym', 'address', 'bdi', 'bdo', 'big', 'cite', 'data', 'dfn',
    'hgroup', 'img', 'ins', 'mark', 'ruby', 'small', 'tbody',
    'tfoot', 'thead',
    # Added:
]


# filters
CUT_EMPTY_ELEMS = {'article', 'b', 'blockquote', 'dd', 'div', 'dt', 'em',
                   'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'i', 'li', 'main',
                   'p', 'pre', 'q', 'section', 'span', 'strong'}


def convert_tags(tree, include_formatting=False, include_tables=False, include_images=False, include_links=False):
    '''Simplify markup and convert relevant HTML tags to an XML standard'''
    # ul/ol → list / li → item
    for elem in tree.iter('ul', 'ol', 'dl'):
        elem.tag = 'list'
        for subelem in elem.iter('dd', 'dt', 'li'):
            subelem.tag = 'item'
    # images
    if include_images is True:
        for elem in tree.iter('img'):
            elem.tag = 'graphic'
    # delete links for faster processing
    if include_links is False:
        if include_tables is True:
            xpath_expr = '//div//a|//list//a|//table//a'
        else:
            xpath_expr = '//div//a|//list//a'
        # necessary for further detection
        for elem in tree.xpath(xpath_expr):
            elem.tag = 'ref'
        # strip the rest
        etree.strip_tags(tree, 'a')
    else:
        for elem in tree.iter('a', 'ref'):
            elem.tag = 'ref'
            # replace href attribute and delete the rest
            target = elem.get('href')  # defaults to None
            elem.attrib.clear()
            if target is not None:
                elem.set('target', target)
    # head tags + delete attributes
    for elem in tree.iter('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
        elem.attrib.clear()
        elem.set('rend', elem.tag)
        elem.tag = 'head'
    # br → lb
    for elem in tree.iter('br', 'hr'):
        elem.tag = 'lb'
    # wbr
    # blockquote, pre, q → quote
    for elem in tree.iter('blockquote', 'pre', 'q', 'font'):
        elem.tag = 'quote'
    # include_formatting
    if include_formatting is False:
        etree.strip_tags(tree, 'em', 'i', 'b', 'strong', 'u', 'kbd', 'samp', 'tt', 'var', 'sub', 'sup')
    else:
        # italics
        for elem in tree.iter('em', 'i'):
            elem.tag = 'hi'
            elem.set('rend', '#i')
        # bold font
        for elem in tree.iter('b', 'strong'):
            elem.tag = 'hi'
            elem.set('rend', '#b')
        # u (very rare)
        for elem in tree.iter('u'):
            elem.tag = 'hi'
            elem.set('rend', '#u')
        # tt (very rare)
        for elem in tree.iter('kbd', 'samp', 'tt', 'var'):
            elem.tag = 'hi'
            elem.set('rend', '#t')
        # sub and sup (very rare)
        for elem in tree.iter('sub'):
            elem.tag = 'hi'
            elem.set('rend', '#sub')
        for elem in tree.iter('sup'):
            elem.tag = 'hi'
            elem.set('rend', '#sup')
    # del | s | strike → <del rend="overstrike">
    for elem in tree.iter('del', 's', 'strike'):
        elem.tag = 'del'
        elem.set('rend', 'overstrike')
    # details + summary
    for elem in tree.iter('details'):
        elem.tag = 'div'
        for subelem in elem.iter('summary'):
            subelem.tag = 'head'
    # Text - Unknown...
    for elem in tree.iter('text'):
        elem.tag = 'p'
    return tree


# Strip: Remove contents in the tag / Clean: Flatten the content
# Modification: Due to result 11 from self-made dataset, improve the logic.
def tree_cleaning(tree, include_tables, include_images=False):
    '''Prune the tree by discarding unwanted elements'''
    # determine cleaning strategy, use lists to keep it deterministic
    cleaning_list, stripping_list = \
        MANUALLY_CLEANED.copy(), MANUALLY_STRIPPED.copy()
    if include_tables is False:
        cleaning_list.extend(['table', 'td', 'th', 'tr'])
    if include_images is True:
        # Many websites have <img> inside <figure> or <picture> or <source> tag
        cleaning_list = [e for e in cleaning_list if e
                         not in ('figure', 'picture', 'source')]
        stripping_list.remove('img')
    # delete targeted elements
    for expression in cleaning_list:
        for element in tree.getiterator(expression):
            try:
                element.drop_tree()  # faster when applicable
            except AttributeError:
                element.getparent().remove(element)
    HTML_CLEANER.kill_tags, HTML_CLEANER.remove_tags = cleaning_list, stripping_list
    # save space and processing time
    return HTML_CLEANER.clean_html(prune_html(tree))


def prune_html(tree):
    '''Delete selected empty elements'''
    for element in tree.xpath(".//*[not(node())]"):
        if element.tag in CUT_EMPTY_ELEMS:
            try:
                element.drop_tree()
            except AttributeError:
                element.getparent().remove(element)
    return tree


def prune_unwanted_nodes(tree, nodelist):
    '''Prune the HTML tree by removing unwanted sections.'''
    for expr in nodelist:
        for subtree in tree.xpath(expr):
            # preserve tail text from deletion
            if subtree.tail is not None:
                previous = subtree.getprevious()
                if previous is None:
                    previous = subtree.getparent()
                if previous is not None:
                    # There is a previous node, append text to its tail
                    if previous.tail is not None:
                        previous.tail = ' '.join([previous.tail, subtree.tail])
                    else:
                        previous.tail = subtree.tail
            # remove the node
            subtree.getparent().remove(subtree)
    return tree
