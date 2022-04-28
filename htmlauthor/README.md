# Htmlauthor - extract author from HTML webpages

## Description
<b>htmlauthor</b> is an python application supports to extract author from web or from local html files.

### Features
- Relatively high extraction accuracy
  - Uses a number of heuristics and fallbacks
  - 48.6% Accuracy, 49.3% Recall and 48.9% F1-Score.
- Robust and efficient extraction

## Basic Usage
### Use as command-line application
<pre>
Usage: cli.py [-h] [-p P] [-b B]

Command-line interface for html-author

optional arguments:
  -h, --help  show this help message and exit
  -p P        Path or URL for extraction
  -b B        Whether uses baseline to improve the recall rate.

For Example:
    python3 cli.py -p http://www.sx.chinanews.com.cn/news/2022/0421/207133.html

Example output:
    ’≈‚˘
</pre>

### Use as library
<pre>
from htmlauthor import extract, chosen_extraction

# extract: Use a bundle of extraction heuristics
extract(file_content, allow_baseline=True)
extract(file_content)

# chosen_extraction: Use specified extraction heuristic(s)
chosen_extraction(file_content, heuristics='all', use_tree_cleaning=True)
chosen_extraction(file_content, heuristics=['ld', 'tag'])
chosen_extraction(file_content)
</pre>
