import logging
from xml import etree
from .extractors import (extract_author_by_name_dict, extract_author_by_keyword, extract_author_by_metadata,
                         extract_author_by_tags, extract_author_by_JSON_LD, extract_author_by_link, heuristics_dict)

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


def chosen_extraction(file_content, heuristics="all", use_tree_cleaning=True):
    """
    This allows for extracting the author choosing heuristics by user. The function have two parameters:

    file_content - refers to the input parameter, accepting LXML tree, trafilatura/urllib3 response, bytestring and string

    heuristics - accept list or string, which includes:
    String:
    "all" uses bare extraction heuristic
    "ld" will use the json-ld heuristic
    "tag" will use meta-tag heuristic
    "keyword" will use extraction with keyword
    "link" will use extraction with link
    "meta" will use extraction with meata heuristic
    Lists takes input of string above and the function will execute all in order.
    For example,
    ["ld", "tag"] will execute extract using JSON-LD and then execute using Tag heuristic

    tree_cleaning: decide whether need to pre-clean the DOM tree to improve accuracy
    """
    tree = load_html(file_content)
    if tree is None:
        Logger.debug("extract: HTML tree empty")
        raise ValueError

    if use_tree_cleaning:
        cleaned_tree = tree_cleaning(tree, include_tables=False)
        cleaned_tree = convert_tags(cleaned_tree)
    else:
        cleaned_tree = convert_tags(tree)

    if isinstance(heuristics, list):
        for item in heuristics:
            if item not in heuristics_dict.keys():
                Logger.warning(f"{item} not included in heuristics_dict.")
                continue
            if item == 'keyword':
                keywords = ['p', 'ref', 'head', 'item', 'quote', 'div']
                for keyword in keywords:
                    author = extract_author_by_keyword(cleaned_tree, keyword)
                    if author is not None:
                        return author
            else:
                author = heuristics_dict[item](cleaned_tree)
                if author is not None:
                    return author
    elif isinstance(heuristics, str):
        if heuristics == 'all':
            return extract(file_content, allow_baseline=True)
        if heuristics == 'keyword':
            keywords = ['p', 'ref', 'head', 'item', 'quote', 'div']
            for keyword in keywords:
                author = extract_author_by_keyword(cleaned_tree, keyword)
                if author is not None:
                    return author
        else:
            author = heuristics_dict[heuristics](cleaned_tree)
            if author is not None:
                return author
    else:
        Logger.warning("Unrecognized heuristics in function 'chosen_extraction'")
        return "UNKNOWN"


def bare_extraction(file_content):
    """
    This method use a number of heuristics to extract authors from web contents
    """

    # Load the html to tree content
    tree = load_html(file_content)
    if tree is None:
        Logger.debug("extract: HTML tree empty")
        raise ValueError

    # print('extracting JSON_ld')
    # s = [i for i in tree.iter('script')]
    # for script in s:
    #     if "type" in script.keys():
    #         if script.attrib['type'] == 'application/ld+json':
    #             print(script.getparent().tag)

    # Extract author with JSON LD - the most trusted resource
    author = extract_author_by_JSON_LD(tree)
    if author is not None:
        return author

    # Tag conversion & Tree cleaning
    cleaned_tree = tree_cleaning(tree, include_tables=False)
    cleaned_tree = convert_tags(cleaned_tree)

    # Testing area
    # extract_author_by_link(cleaned_tree=cleaned_tree)


    # Extract with metadata - second trusted resource
    author = extract_author_by_metadata(cleaned_tree)
    if author is not None:
        # print(author)
        return author

    # Extract with Tags - classes and ids and rels
    author = extract_author_by_tags(cleaned_tree)
    if author is not None:
        return author

    # Extract with Links
    author = extract_author_by_link(cleaned_tree)
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


def extract(file_content, allow_baseline=True):
    try:
        author = bare_extraction(file_content)
        if author is None and allow_baseline:
            author = baseline(file_content)
        return author if author is not None else "UNKNOWN"
    except ValueError:
        return "UNKNOWN"
