import re
from urllib.parse import urlparse, urljoin, urldefrag
from bs4 import BeautifulSoup

unique_links = set()
# ignore_tags = ['header', 'footer', 'aside']

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

    links = set()
    soup = BeautifulSoup(resp.raw_response.content, 'lxml')     # create beautifulsoup object using 'lxml' (faster)

    body = soup.find('body')
    for link in soup2.find_all('a', href=True):                 # find all href (links) from <a> tag and loop through them
        full_url = urljoin(url, link['href'])                   # get the full urls
        full_url, _ = urldefrag(full_url)                       # remove fragmentation
        if link not in unique_links:
            unique_links.add(full_url)
            links.add(full_url)                                 # add to the retuning set
    

    return list(links)

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
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
