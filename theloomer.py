# Configuration
UTM_SOURCE = "almost-timely-newsletter"
UTM_MEDIUM = "email"
UTM_CAMPAIGN = "almost-timely-newsletter-2024-02-11"

# Assuming UTM_SOURCE, UTM_MEDIUM, and UTM_CAMPAIGN are defined globally
# Example:
# UTM_SOURCE = "example_source"
# UTM_MEDIUM = "example_medium"
# UTM_CAMPAIGN = "example_campaign"

### DON'T EDIT PAST HERE IF YOU DON'T KNOW PYTHON

import argparse
import csv
from datetime import datetime
import os
import urllib.parse

# Installation of libraries

try:
    from tqdm import tqdm
except ImportError:
    print("tqdm is not installed. Please install it using 'pip install tqdm' and then rerun the script.")
    exit()

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("BeautifulSoup is not installed. Please install it using 'pip install beautifulsoup4' and then rerun the script.")
    exit()


def append_utm_parameters(url):
    """
    Append missing UTM parameters to the given URL if they don't exist.
    Returns the modified URL.
    """
    url_parts = list(urllib.parse.urlparse(url))
    query = dict(urllib.parse.parse_qsl(url_parts[4]))
    utm_added = False
    
    # Check and append missing UTM parameters
    for utm_key, utm_value in [("utm_source", UTM_SOURCE), ("utm_medium", UTM_MEDIUM), ("utm_campaign", UTM_CAMPAIGN)]:
        if utm_key not in query:
            query[utm_key] = utm_value
            utm_added = True

    if utm_added:
        url_parts[4] = urllib.parse.urlencode(query)
        return urllib.parse.urlunparse(url_parts)
    else:
        return url

def parse_html(input_file):
    """
    Parse the HTML file to identify links, check for UTM parameters, and prepare for CSV export and HTML modification.
    """
    with open(input_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    links_with_utm = []
    links_without_utm = []
    
    # Use tqdm for progress feedback if parsing large files
    for link in tqdm(soup.find_all('a', href=True), desc="Analyzing links"):
        href = link['href']
        # Skip non-web page links or resources
        if href.startswith(('http:', 'https:')) and not any(href.endswith(ext) for ext in ['.jpg', '.png', '.gif', '.css', '.js']):
            parsed_url = urllib.parse.urlparse(href)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            has_utm = any(param.startswith('utm_') for param in query_params)
            
            # Check and categorize links based on UTM presence
            if has_utm:
                links_with_utm.append(href)
            else:
                links_without_utm.append(href)
                modified_url = append_utm_parameters(href)
                link['href'] = modified_url  # Modify the link in the soup object for later saving

    # At this point, links_with_utm and links_without_utm lists are populated
    # And the soup object has been modified with appended UTM parameters where needed

    return links_with_utm, links_without_utm, soup

# This function is just part of the workflow. You would call it from your main function,
# and use its output for both the CSV report and saving the modified HTML file.

def save_modified_html(soup, input_file):
    """
    Save the modified HTML content to a new file with '-modified' appended to the original file name.

    Parameters:
    - soup: BeautifulSoup object containing the modified HTML content.
    - input_file: String representing the path to the original HTML file.
    """
    # Extract the base name and extension of the input file
    base_name = os.path.splitext(input_file)[0]
    extension = os.path.splitext(input_file)[1]
    
    # Construct the output file name by appending '-modified' to the base name
    output_file_name = f"{base_name}-modified{extension}"
    
    # Write the modified HTML content to the new file
    with open(output_file_name, 'w', encoding='utf-8') as output_file:
        output_file.write(str(soup))

    print(f"Modified HTML saved to {output_file_name}")

def export_to_csv(links_with_utm, links_without_utm, input_file):
    """
    Export the analysis of links to a CSV file. The CSV will include columns for
    "Input URL", "UTM Codes" (Yes/No), and "Query Parameters".

    Parameters:
    - links_with_utm: List of links that already have UTM parameters.
    - links_without_utm: List of links that did not have UTM parameters and were modified.
    - input_file: The original HTML file name used to generate a timestamped CSV file name.
    """
    # Define the CSV file name based on the input file name and the current datetime
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    datetime_stamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    csv_file_name = f"{base_name}-{datetime_stamp}.csv"

    # Open the CSV file for writing
    with open(csv_file_name, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header row
        writer.writerow(["Input URL", "UTM Codes", "Query Parameters"])

        # Process links with UTM parameters
        for link in links_with_utm:
            parsed_url = urllib.parse.urlparse(link)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            # Join all query parameters into a single string for the "Query Parameters" column
            query_params_str = '&'.join([f"{k}={','.join(v)}" for k, v in query_params.items()])
            writer.writerow([link, "Yes", query_params_str])

        # Process links without UTM parameters (modified links)
        for link in links_without_utm:
            parsed_url = urllib.parse.urlparse(link)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            query_params_str = '&'.join([f"{k}={','.join(v)}" for k, v in query_params.items()])
            writer.writerow([link, "No", query_params_str])

    print(f"CSV report saved to {csv_file_name}")

def main():
    parser = argparse.ArgumentParser(description="Process HTML file for UTM parameters.")
    parser.add_argument("--input", required=True, help="Path to the HTML file.")
    args = parser.parse_args()

    # Process the HTML file
    links_with_utm, links_without_utm, soup = parse_html(args.input)
    
    # Export to CSV
    export_to_csv(links_with_utm, links_without_utm, args.input)
    
    # Save modified HTML
    save_modified_html(soup, args.input)

if __name__ == "__main__":
    main()

"""
Requirements:
- Input Handling:
  - Accept an HTML file path through a `--input` command-line argument.
  - Ensure flexibility in handling various HTML content structures.
- Link Processing:
  - Identify and process both absolute and relative URLs within `<a>` tags.
  - Ignore non-web page links (e.g., `mailto:`, `tel:`) that can't carry UTM parameters.
- UTM Parameter Analysis:
  - Detect existing `utm_source`, `utm_medium`, and `utm_campaign` parameters in URLs.
  - Append missing UTM parameters to URLs lacking them, with values configurable at the script's top.
- CSV Reporting:
  - Generate a CSV report including columns for "Input URL", "UTM Codes" (Yes/No), and "Query Parameters".
  - Name the CSV file using the input file name appended with the current datetime in the format `yyyy-mm-dd-hh-mm-ss`.
- HTML Modification:
  - Save a modified version of the HTML file with missing UTM parameters appended to relevant links.
  - Use the naming convention `<originalfilename>-modified.htm` for the modified HTML file.
  - Ensure the modified file is saved in the same directory as the script execution.
- Resource URL Exclusion:
  - Explicitly exclude URLs to resources such as scripts, images, binary files, audio, video, and stylesheets.
- Error Handling and Logging:
  - Log malformed URLs and other errors to an `errors.txt` file.
  - Utilize `tqdm` for visual progress feedback during script execution.
- Performance and Scalability:
  - Efficiently process HTML files of any size, executing tasks serially without requiring parallel processing.
"""
