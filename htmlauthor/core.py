import logging
from xml import etree
from .extractors import (extract_author_by_name_dict, extract_author_by_keyword, extract_author_by_metadata,
                         extract_author_by_tags, extract_author_by_JSON_LD, extract_author_by_link)

from htmlauthor.utils import load_html
from .html_processing import convert_tags, tree_cleaning

Logger = logging.getLogger(__name__)


def baseline(file_content):
    """
    This method is used for the baseline extraction:
    Iterate through all file contents to find the string format that corresponds to the author
    """
    author = None
    # Load the html to tree content
    tree = load_html(file_content)
    if tree is None:
        Logger.debug("extract: HTML tree empty")

    # Tag conversion
    cleaned_tree = convert_tags(tree, include_tables=True)

    # Iterate through all contents to extract with name
    keywords = ['p', 'ref', 'head', 'item', 'quote', 'div']
    for keyword in keywords:
        author = extract_author_by_keyword(cleaned_tree, keyword)
        if author is not None:
            return author
    return author


def bare_extraction(file_content):
    """
    This method use a number of heuristics to extract authors from web contents
    """
    author = None

    # Load the html to tree content
    tree = load_html(file_content)
    if tree is None:
        Logger.debug("extract: HTML tree empty")
        raise ValueError

    # Tag conversion & Tree cleaning
    cleaned_tree = tree_cleaning(tree, include_tables=False)
    cleaned_tree = convert_tags(cleaned_tree)

    # Testing area
    extract_author_by_link(cleaned_tree=cleaned_tree)

    # Extract author with JSON LD - the most trusted resource
    author = extract_author_by_JSON_LD(cleaned_tree)
    if author is not None:
        return author

    # Extract with metadata - second trusted resource
    author = extract_author_by_metadata(cleaned_tree)
    if author is not None:
        return author

    # Extract with Tags - classes and ids and rels
    author = extract_author_by_tags(cleaned_tree)
    if author is not None:
        return author

    # Extract with keyword: Iterate through all contents to extract with name
    keywords = ['p', 'ref', 'head', 'item', 'quote', 'div']
    for keyword in keywords:
        author = extract_author_by_keyword(cleaned_tree, keyword)
        if author is not None:
            return author

    # print([i.text_content() for i in cleaned_tree.iter('head')])
    return author


def extract(file_content):
    try:
        author = bare_extraction(file_content)
        if author is None:
            author = baseline(file_content)
        return author if author is not None else "UNKNOWN"
    except ValueError:
        return "UNKNOWN"
