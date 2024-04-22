import re
from urllib.parse import urlparse, urljoin, urldefrag
from bs4 import BeautifulSoup
from configparser import ConfigParser
from utils.config import Config

ignore_tags = ['header', 'footer', 'aside']

seedurls = []
unique_links = dict()
# Get seedurl and add them to unique_links
cparser = ConfigParser()
cparser.read('config.ini')
config = Config(cparser)
for url in config.seed_urls:
    unique_links[url] = 0
    seedurls.append(urlparse(url).netloc)

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

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

    # Check if status is invalid
    if resp.status != 200: return set()

    # Check if the current depth is not too deep (Avoid traps)
    current_depth = unique_links[url]
    if(current_depth >= 200):
        return set()

    links = set()
    soup = BeautifulSoup(resp.raw_response.content, 'lxml')     # create beautifulsoup object using 'lxml' (faster)

    # remove certain tags (Avoid data noise)
    # for tag in ignore_tags:
    #     for element in soup.find_all(tag):
    #         element.decompose()
    for script_or_style in soup(ignore_tags):
        script_or_style.decompose()

    # Detect and avoid sets of pages with no information
    if has_low_information(soup):
        return set()

    for link in soup.find_all('a', href=True):                  # find all href (links) from <a> tag and loop through them
        full_url = get_full_url(url, link)                      # get full url

        if link not in unique_links and full_url != url:        # if the link has not been scraped before, add to unique_links and add to return set (Avoid duplicates)
            unique_links[full_url] = current_depth + 1
            links.add(full_url)  
            
            # print(url)
            # print(full_url)
            # print(unique_links)
            # unique_links.add(full_url)

    return list(links)

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
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

# Given the parent url, and the link's url: return the full url
def get_full_url(url, link):
    full_url = urljoin(url, link['href'])                   # get the full urls
    full_url, _ = urldefrag(full_url)                       # remove fragmentation
    # Remove '/' at the end of url
    if full_url[-1] == '/':
        full_url = full_url[:-1]
    return full_url

# Checks if the content has enough information
def has_low_information(soup):
    text = soup.get_text(separator=' ')
    words = re.findall(r'\w+', text)

    min_length = 200  # minimum number of characters for meaningful content

    return len(text) < min_length