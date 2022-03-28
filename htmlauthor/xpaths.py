"""
X-Path expressions needed to extract and filter the main text content
"""
import re

BRACKETS = ["[", "]", "(", ")", "{", "}", "（", "）", "【", "】"]

# Extract Author from JSON: identify author name from front and after space.
AUTHOR_PREFIX = ["作者", "author", "编辑", "小编", "笔者", "editor", "edited by", "written by", "记者", "主编", "实习生"]
AUTHOR_AFTER = ["著", "Edited", "编", "编辑", "电"]
AUTHOR_MAXLENGTH = 12

AUTHOR_RE = re.compile(r'(实习记者|作者|author|编辑|小编|笔者|editor|edited by|written by|记者|主编|实习生|来源|来自|发文机关|执笔人)([\s:： ]+?['
                       r'\u4e00-\u9fa5A-Za-z0-9]+)+| '
                       r'[\u4e00-\u9fa5A-Za-z0-9]+[\s:： ]+(著|Edited|编|编辑|报道)', re.U)
# AUTHOR_RE = re.compile(r'(作者|author|编辑|小编|笔者|editor|edited by|written by|记者|主编)[\s:： ]\w+')
# AUTHOR_RE = re.compile(r'记者[\s:： ]\w+([\s,，]\w+)\1')
AUTHOR_PRE_RE = re.compile(r'作者|author|编辑|小编|笔者|editor|edited by|written by|记者|主编|实习生|来源|来自|发文机关|执笔人')
AUTHOR_AFT_RE = re.compile(r'著|Edited|编|编辑|报道')
AUTHOR_KEYWORDS_RE = re.compile(r'本报|实习记者|作者|author|编辑|小编|笔者|editor|edited by|written by|记者|主编|著|Edited|编|报道|实习生|来源|来自|发文机关|执笔人')

BLANKS_RE = re.compile(r'\s\s+')

DIVIDER_RE = re.compile('[:： ]')

# AUTHOR_RE = re.compile(r'(作者|author|编辑|小编|笔者|editor|edited by|written by|记者|主编)')
INLINE_RE = re.compile(r'[\\(（].*?[\\)）]')

AUTHOR_EXCLUDED_RE = re.compile(r"[^\u4e00-\u9fa50-9a-zA-Z ]|转载|(\w{2}网)|晨报|晚报|早报|日报")

JSON_LD_XPATH = [
    '//*[(self::script)][@type="application/ld+json"]'
]

META_XPATH = [
    '''//*[(self::meta)]'''
]

AUTHOR_XPATH = [
    '//*[(self::ref or self::head or self::item or self::p or self::quote or self::div)][@rel="author" or '
    '@id="author" or @class="author" or @itemprop="author name" or rel="me"]|//author', # specific
    '//*[(self::ref or self::head or self::item or self::p or self::quote or self::div)][contains(@class, '
    '"author-name") or '
    'contains(@class, "AuthorName") or contains(@class, "authorName") or contains(@class, "author name")]',
    # almost specific
    '//*[(self::ref or self::head or self::item or self::p or self::quote or self::div)][contains(@class, "author") or '
    'contains(@id, "author") or contains(@itemprop, "author") or @class="byline"]', # almost generic
    '//*[(self::ref or self::head or self::item or self::p or self::quote or self::div)][contains(@class, "authors") '
    'or contains(@class, '
    '"byline") or contains(@class, "ByLine") or contains(@class, "submitted-by") or contains(@class, "posted-by")]',
    # generic
    '//*[contains(@class, "author") or contains(@class, "Author") or contains(@id, "Author") or contains(@class, '
    '"screenname") or contains(@data-component, "Byline") or contains(@itemprop, "author") or contains(@class, '
    '"writer") or contains(@class, "byline")]', # any element
    '//*[(self::ref or self::head or self::item or self::p or self::quote or self::div)][@class="username" or '
    '@class="BBL"]', # not common
]

