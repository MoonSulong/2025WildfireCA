import csv
from collections import Counter
import tldextract
import re
import urllib.parse


def extract_urls_from_text(text):
    """
    Extracts all URLs (http/https or www) from a given text string.
    """
    url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    return re.findall(url_pattern, text)


def is_valid_url(url):
    """
    Checks if a URL has a valid structure and contains no spaces.
    """
    try:
        url_to_check = url
        if url.lower().startswith('www.') and not url.lower().startswith(('http://', 'https://')):
            url_to_check = 'http://' + url

        result = urllib.parse.urlparse(url_to_check)
        return all([result.scheme, result.netloc]) and ' ' not in url
    except ValueError:
        return False


def normalize_domain_to_com(domain, domain_mappings):
    """
    Normalizes a domain name to its .com equivalent if possible.
    """
    domain_lower = domain.lower()

    if domain_lower in domain_mappings:
        return domain_mappings[domain_lower]

    if domain_lower.endswith('.com'):
        return domain

    parts = domain.split('.')
    if len(parts) >= 2:
        name = parts[0].lower()

        for existing_domain in domain_mappings.values():
            existing_domain_lower = existing_domain.lower()
            existing_name = existing_domain_lower.split('.')[0]

            if existing_name == name and existing_domain_lower.endswith('.com'):
                return existing_domain

    return domain


def extract_full_domain(url, extracted):
    """
    Extracts the registered domain or the full subdomain for specified government domains.
    """
    registered_domain = f"{extracted.domain}.{extracted.suffix}"

    if registered_domain in {"lacounty.gov", "lacity.gov", "ca.gov"}:
        match = re.search(r"https?://([^/]+)", url)
        if match:
            return match.group(1).replace("www.", "")

    return registered_domain if extracted.suffix else extracted.domain


def is_valid_domain(domain):
    """
    Checks if the extracted domain is valid by filtering out blacklisted terms and malformed structures.
    """
    if ')' in domain:
        return False

    blacklisted_terms = {'file', 'www', 'http', 'https'}
    if domain.lower() in blacklisted_terms:
        return False

    domain_regex = re.compile(
        r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)"
        r"(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*\.[A-Za-z]{2,}$"
    )

    return bool(domain_regex.match(domain))


def main(input_csv, output_unique_domains, output_sorted_domains_count):
    """
    Main execution logic to read comments, extract, normalize, and count domains.
    """
    domain_mappings = {
        'youtu.be': 'youtube.com',
        'redd.it': 'reddit.com',
        'gofundme.org': 'gofundme.com',
        'bbc.co.uk': 'bbc.com',
        'dailymail.co.uk': 'dailymail.com',
        'businessinsider.in': 'businessinsider.com',
        'goo.gl': 'google.com'
    }

    unique_domains_set = set()
    all_domains = []

    try:
        with open(input_csv, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                body = row.get('body', '')
                urls = extract_urls_from_text(body)

                for url in urls:
                    if not is_valid_url(url):
                        continue

                    decoded_url = urllib.parse.unquote(url)
                    extracted = tldextract.extract(decoded_url)
                    domain = extract_full_domain(decoded_url, extracted)

                    if domain:
                        domain = normalize_domain_to_com(domain, domain_mappings)

                        if is_valid_domain(domain):
                            unique_domains_set.add(domain)
                            all_domains.append(domain)

    except FileNotFoundError:
        print(f"Error: The input file was not found: {input_csv}")
        return

    domain_counts = Counter(all_domains)
    sorted_domain_counts = sorted(
        domain_counts.items(),
        key=lambda item: item[1],
        reverse=True
    )

    try:
        with open(output_sorted_domains_count, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Domain', 'Count'])
            for domain, count in sorted_domain_counts:
                writer.writerow([domain, count])

        print(f"Domain counts saved to {output_sorted_domains_count}")
    except Exception as e:
        print(f"Failed to write sorted domain counts: {e}")

    try:
        with open(output_unique_domains, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Unique_Domain'])
            for domain in sorted(unique_domains_set):
                writer.writerow([domain])

        print(f"Unique domains saved to {output_unique_domains}")
    except Exception as e:
        print(f"Failed to write unique domains: {e}")


# # Example
# INPUT_CSV = r"C:\Users\lucy0\Desktop\all_raw_comments.csv"
# OUTPUT_UNIQUE_DOMAINS = r"C:\Users\lucy0\Desktop\1\comment_unique_domains.csv"
# OUTPUT_SORTED_DOMAINS_COUNT = r"C:\Users\lucy0\Desktop\1\sorted_domains_count.csv"

# if __name__ == "__main__":
#     main(
#         INPUT_CSV,
#         OUTPUT_UNIQUE_DOMAINS,
#         OUTPUT_SORTED_DOMAINS_COUNT
#     )
