import csv
from collections import Counter
import tldextract
import re
from urllib.parse import unquote
import urllib.parse


def extract_urls_from_text(text):
    """
    Extracts all URLs (http/https or www) from a given text string.
    """
    url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    return re.findall(url_pattern, text)

def is_valid_url(url):
    """
    Checks if a URL has a valid structure (scheme and network location) and contains no spaces.
    """
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc]) and ' ' not in url
    except ValueError:
        return False

def normalize_domain_to_com(domain, domain_mappings):
    """
    Attempts to normalize a domain name to its .com equivalent if a match is found.
    """
    parts = domain.split('.')
    if len(parts) >= 2:
        name = parts[0].lower()
        
        if domain.lower().endswith('.com'):
            return domain
        
        for existing_domain in domain_mappings.values():
            if existing_domain.lower().startswith(name + '.') and existing_domain.lower().endswith('.com'):
                return existing_domain
                
        return domain
    return domain

def extract_full_domain(url, extracted):
    """
    Extracts the registered domain or the full subdomain if it's one of the specified government domains.
    """
    registered_domain = f"{extracted.domain}.{extracted.suffix}"
    
    if registered_domain in ["lacounty.gov", "lacity.gov", "ca.gov"]:
        match = re.search(r"https?://([^/]+)", url)
        if match:
            full_domain = match.group(1).replace("www.", "")  
            return full_domain  
            
    return registered_domain if extracted.suffix else extracted.domain

def is_valid_domain(domain):
    """
    Checks if the extracted domain is valid by filtering out problematic characters and blacklisted terms.
    """
    if ')' in domain:
        return False
        
    blacklisted_terms = {'file', 'www', 'http', 'https', ''}  
    
    if domain.lower() in blacklisted_terms:
        return False

    return True

# # Example Usage
# input_csv = ['all_raw_comments.csv']
# output_unique_domains = ['comment_unique_domains.csv']
#output_sorted_domains_count = ['sorted_domains_count.csv']

# # Domain mapping to normalize short/regional domains to a single major domain for consistent counting.
# domain_mappings = {
#     'youtu.be': 'youtube.com',
#     'redd.it': 'reddit.com',
#     'gofundme.org': 'gofundme.com',
#     'bbc.co.uk': 'bbc.com',
#     'dailymail.co.uk': 'dailymail.com',
#     'businessinsider.in': 'businessinsider.com',
#     'goo.gl': 'google.com'
# }

# unique_domains_set = set()
# all_domains = []

# try:
#     with open(input_csv, 'r', encoding='utf-8') as file:
#         reader = csv.DictReader(file)
#         for row in reader:
#             body = row.get('body', '')
#             urls = extract_urls_from_text(body)
            
#             for url in urls:
                
#                 if not is_valid_url(url):
#                     continue
                
#                 decoded_url = unquote(url)
                
#                 extracted = tldextract.extract(decoded_url)
#                 domain = extract_full_domain(decoded_url, extracted)
                
#                 if domain:
#                     if domain in domain_mappings:
#                         domain = domain_mappings[domain]
#                     domain = normalize_domain_to_com(domain, domain_mappings)
                    
#                     if is_valid_domain(domain):
#                         unique_domains_set.add(domain)
#                         all_domains.append(domain)
                        
#                 elif '%' in decoded_url:
#                     domain_match = re.search(r'https?://(?:www\.)?([^/]+)', decoded_url)
#                     if domain_match:
#                         domain = domain_match.group(1)
#                         if domain in domain_mappings:
#                             domain = domain_mappings[domain]
#                         domain = normalize_domain_to_com(domain, domain_mappings)
#                         if is_valid_domain(domain):
#                             unique_domains_set.add(domain)
#                             all_domains.append(domain)

# except FileNotFoundError:
#     print(f"Error: The input file was not found: {input_csv}")
#     exit()


# domain_counts = Counter(all_domains)
# sorted_domain_counts = sorted(domain_counts.items(), key=lambda item: item[1], reverse=True)


# try:
#     with open(output_sorted_domains_count, 'w', encoding='utf-8', newline='') as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(['Domain', 'Count'])
#         for domain, count in sorted_domain_counts:
#             writer.writerow([domain, count])
    
#     print(f"Domain counts saved to {output_sorted_domains_count}")
# except Exception as e:
#     print(f"Failed to write sorted domain counts: {e}")

# with open(output_unique_domains, 'w', encoding='utf-8', newline='') as csvfile:
#     writer = csv.writer(csvfile)
#     writer.writerow(['Unique_Domain'])
#     sorted_unique_domains = sorted(list(unique_domains_set))
#     for domain in sorted_unique_domains:
#         writer.writerow([domain])

# print(f"Unique domains saved to {output_unique_domains}")