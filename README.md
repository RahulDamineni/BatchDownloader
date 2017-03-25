# BatchDownloader
Takes an index page (url with lots of hyperlinks) as input and queues them all for download. When available, sends multiple requests to the server for better utilization of bandwidth to achieve faster download.

# Requirements
- urllib2
- lxml

# Configuration
- You can set download folder in line 85
- You can filter files to download based on key-words in link names, edit line 83 for that

# Usage
python main.py "http://url/with/a/lot/of/hyperlinks/which/you/want/to/download"
