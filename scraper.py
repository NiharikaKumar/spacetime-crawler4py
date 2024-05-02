import re
from urllib.parse import urlparse, urljoin, urldefrag, urlunparse
from bs4 import BeautifulSoup
from configparser import ConfigParser
from utils.config import Config
import urllib.robotparser
from simhash import Simhash, SimhashIndex
from hashlib import sha256
from stopwords import stopwords
from collections import Counter


# with depth, with tags, without words

word_counts = Counter()
ignore_tags = ['header', 'footer', 'aside']

max_words = 0
count = 0

subdomain_counts = dict()
seedurls = []
unique_links = dict()
# seen_hashes = set()
content_hashes = set()
simhash_index = SimhashIndex([], k=3)

# Get seedurl and add them to unique_links
cparser = ConfigParser()
cparser.read('config.ini')
config = Config(cparser)
for url in config.seed_urls:
    unique_links[url] = 0
    seedurls.append(urlparse(url).netloc)

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return links
    # return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    global count, max_words

    # Avoid invalid data passed
    if resp is None or resp.raw_response is None or resp.raw_response.content is None:
        return set()

    # Avoid invalid status
    if not 200 <= resp.status < 400:
        return set()

    # Check for redirect
    if resp.status in (301, 302, 303, 307, 308):
        location = resp.headers.get('Location')
        if location:
            url = urljoin(url, location)
        else:
            return set()

    # Check content size
    content_length = resp.raw_response.headers.get('Content-Length')
    if content_length != None and int(content_length) > 100000000: # 100MB
        return set()

    # Check for duplicates:
    # get encoding
    content_type = resp.raw_response.headers.get('Content-Type', '')
    encoding = 'utf-8'  # Default to UTF-8
    if 'charset=' in content_type:
        encoding = content_type.split('charset=')[-1].split(';')[0].strip()
    else:
        encoding = 'iso-8859-1'  # Common default if charset is not specified
    # decode given encoding
    try:
        content = resp.raw_response.content.decode(encoding)
    except UnicodeDecodeError:
        content = resp.raw_response.content.decode('latin-1')
    except LookupError:
        content = resp.raw_response.content.decode('iso-8859-1')
    # check for duplicates
    if is_duplicate(content):
        return set()

    # Check if the current depth is not too deep (Avoid traps)
    current_depth = unique_links[url]
    if(current_depth >= 500):
       return set()

    soup = BeautifulSoup(content, 'lxml')

    # Remove certain tags (Avoid data noise)
    for tag in ignore_tags:
        for element in soup.find_all(tag):
            element.decompose()

    # Check if the website has little information
    if has_low_information(soup):
        return set()
    
    if not is_valid(url):
        return set()

    # [] WRITE url with max words
    # content_type = resp.headers.get('Content-Type', '')
    text = soup.get_text(separator=' ')
    words = [word.lower() for word in re.findall(r'\w+', text)]
    if len(words) > max_words:
        max_words = len(words)
        with open("x_max_words.txt", 'w') as file:
            file.write(f"{url} {max_words}")
        print("\t max words:", max_words ,url)

    # [] WRITE most common words
    words_set = set(words) - set(stopwords)
    filtered_words = [word for word in words_set if len(word) > 2 and word.isalpha()]
    word_counts.update(filtered_words)
    top_words = word_counts.most_common(50)
    with open("x_most_frequent.txt", 'w') as file:
        for word, frequency in top_words:
            file.write(f"{word}: {frequency}\n")

    count += 1
    # [] WRITE number of unique urls
    # print("\t number:", count)
    with open("x_count.txt", 'w') as file:
        file.write(f"{count}")
        print("\tcount", count)

    # [] WRITE subdomains of ics.uci.edu
    parsed_url = urlparse(url)
    subdomain = parsed_url.netloc
    if subdomain.endswith(".ics.uci.edu"):
        if subdomain in subdomain_counts:
            subdomain_counts[url] += 1
        else:
            subdomain_counts[url] = 1
    with open("x_subdomains.txt", 'w') as file:
        for subdomain in sorted(subdomain_counts.keys()):
            file.write(f"{subdomain}, {subdomain_counts[subdomain]}\n")

    links = set()

    # Read robots.txt
    #rp = urllib.robotparser.RobotFileParser()
    #rp.set_url(urljoin(url, '/robots.txt'))
    #rp.read()

    # Check every link in the website
    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            full_url = get_full_url(url, href)
            if full_url not in unique_links: #and rp.can_fetch('*', full_url):    # If the link has not been scanned, and we are allowed to scan
                unique_links[full_url] = current_depth + 1
                links.add(full_url)

    return list(links)

# Given the parent url, and the link's url: return the full url
def get_full_url(url, href):
    full_url = urljoin(url, href)       # join url if necessary
    full_url, _ = urldefrag(full_url)   # remove fragment
    # remove query
    parsed_url = urlparse(full_url)
    clean_url = urlunparse(parsed_url._replace(query=""))
    # remove '/' at the end
    if clean_url[-1] == '/':
        clean_url = clean_url[:-1]
    return clean_url

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        # if parsed not in seedurls: return False (Avoid other urls)
        if parsed.netloc not in seedurls:
            return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|img|jpg|war|mpg|apk|z"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

# Checks if the content has enough information
def has_low_information(soup):
    text = soup.get_text(separator=' ')
    min_length = 200  # minimum number of characters
    return len(text) < min_length

def get_content_hash(content):
    return sha256(content.encode('utf-8')).hexdigest()

def get_simhash(content):
    return Simhash(content)

def is_duplicate(content):
    # Check exact duplicate
    content_hash = get_content_hash(content)
    if content_hash in content_hashes:
        return True
    content_hashes.add(content_hash)
    
    # Check near duplicate
    simhash = get_simhash(content)
    near_dup = simhash_index.get_near_dups(simhash)
    if near_dup:
        return True
    simhash_index.add(str(simhash), simhash)

    return False
