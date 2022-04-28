import json
import re

from .utils import decode_url_string_to_list
from .xpaths import *


def find_excluded_extraction(string):
    # print(AUTHOR_EXCLUDED_RE.search(string))
    return False if AUTHOR_EXCLUDED_RE.search(string) is None else True


# Extract author information from a string
def str_extractor(string: re.Match):
    string = string.group()
    for br in BRACKETS:
        string = string.strip().strip(br)
    author = string
    keywords = AUTHOR_KEYWORDS_RE.findall(string)

    for i in keywords:
        author = author.replace(i, "")
    dividers = DIVIDER_RE.findall(author)
    for i in dividers:
        author = author.strip(i)
    # Heuristic of getting the longest word in the list
    if len(max(author.split(" "), key=len)) > AUTHOR_MAXLENGTH:
        return None
    return author
    # Recover previous search

    # if author is not None:
    #     author = author.string.split(" ")
    #     # print(author)
    #     author = " ".join(author[1:])
    # else:
    #     return None
    # print(author)
    # if len(author) > AUTHOR_MAXLENGTH:
    #     return None
    # return author


def test_author_by_link_density():
    pass


# def extract_author_by_keyword(cleaned_tree, tag):
#     for subtree in cleaned_tree.iter(tag):
#         # print(tag, subtree.text_content())
#         # result = INLINE_RE.findall('(123), (234)')
#         # Search for inline brackets
#         result = INLINE_RE.findall(subtree.text_content())
#         # print(result)
#         for res in result:
#             # Iterate through inline result to attempt extracting authors
#             author = str_extractor(res)
#             if author is not None:
#                 # print(author)
#                 return author
#     return None

# Baseline extraction
def extract_author_by_keyword(cleaned_tree, tag):
    for subtree in cleaned_tree.iter(tag):
        # if len(subtree.text_content()) < 20:
        # if '山石' in subtree.text_content():
        #     print(tag, subtree.text_content())
        # result = INLINE_RE.findall('(123), (234)')
        # Search for inline brackets
        # result = AUTHOR_RE.search(subtree.text_content())
        # print(tag, subtree.text_content())
        result = AUTHOR_RE.search(subtree.text_content())
        # print(result)
        if result is not None:
            author = str_extractor(result)
            if author is not None:
                if not find_excluded_extraction(author):
                    return author
    return None


def extract_author_by_name_dict(cleaned_tree):
    pass


# TODO: Improve heuristic
def extract_author_by_link(cleaned_tree):
    subtree = cleaned_tree.xpath("//ref")
    if not subtree:
        return None
    author = None
    for ele in subtree:
        # print([link for link in ele.iterlinks()])
        words = decode_url_string_to_list(ele.get("href"))
        if words is None:
            continue
        # print(words)
        for word in words:
            if word in AUTHOR_LINK_KEYWORD:
                ind = AUTHOR_LINK_KEYWORD.index(word)
                if len(words) > ind + 1:
                    print('>', words[ind + 1])
            # if not ind:
            #     continue
            # print(ind, words[ind])
    return author


def extract_author_by_JSON_LD(cleaned_tree):
    for expr in JSON_LD_XPATH:
        subtree = cleaned_tree.xpath(expr)
        if not subtree:
            continue
        for ele in subtree:
            data = json.loads(ele.text_content())
            if 'author' in data:
                if 'name' in data['author']:
                    return data['author']['name']
            elif 'brand' in data:
                if 'name' in data['brand']:
                    return data['brand']['name']
    return None


def extract_author_by_metadata(cleaned_tree):
    for expr in META_XPATH:
        subtree = cleaned_tree.xpath(expr)
        if not subtree:
            continue
        for ele in subtree:
            data = ele.attrib
            if 'name' in data:
                if data['name'].lower() == 'author':
                    tmp = data['content'] if 'content' in data else None
                    # print(tmp)
                    if not find_excluded_extraction(tmp):
                        return tmp
                    # return data['content'] if 'content' in data else None
            if 'property' in data:
                if data['property'].lower() == 'article:author':
                    # return data['content'] if 'content' in data else None
                    tmp = data['content'] if 'content' in data else None
                    if not find_excluded_extraction(tmp):
                        return tmp

    return None


def tag_str_extractor(string):
    keywords = AUTHOR_KEYWORDS_RE.findall(string)
    if not keywords:
        return None
    for ele in keywords:
        string = string.replace(ele, "").strip()
    # print(string)
    dividers = DIVIDER_RE.findall(string)
    for ele in dividers:
        string = string.replace(ele, "").strip()
    # Remove blank spaces
    while True:
        blank_space = BLANKS_RE.search(string)
        if not blank_space:
            break
        string = string.split(blank_space.string)[0]
    if string == "":
        return None
    if find_excluded_extraction(string):
        # print(string)
        return None
    return string


def extract_author_by_tags(cleaned_tree):
    for expr in AUTHOR_XPATH:
        subtree = cleaned_tree.xpath(expr)
        if not subtree:
            continue
        for ele in subtree:
            data = ele.text_content()
            author = tag_str_extractor(data)
            if author:
                return author
    return None


heuristics_dict = {
    "ld": extract_author_by_JSON_LD,
    "tag": extract_author_by_tags,
    "keyword": extract_author_by_keyword,
    "link": extract_author_by_link,
    "meta": extract_author_by_metadata
}
