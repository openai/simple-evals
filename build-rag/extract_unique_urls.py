import csv
import ast
import validators
from urllib.parse import urlsplit, urlunsplit

def extract_and_clean_urls(file_name):
    unique_urls = set()

    def get_canonical_url(url):
        """Remove anchors but keep query parameters."""
        parsed = urlsplit(url)
        return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, parsed.query, ''))  # Keep query, remove fragment

    with open(file_name, 'r') as file:
        reader = csv.reader(file)
        
        # Skip the header row
        next(reader)
        
        for row in reader:
            metadata = row[0]  # Metadata column
            try:
                # Convert metadata string to dictionary
                metadata_dict = ast.literal_eval(metadata)
                
                # Extract URLs and process them
                urls = metadata_dict.get('urls', [])
                for url in urls:
                    # Clean up the URL
                    url = url.strip(' "\'')  # Remove unwanted quotes or spaces
                    if validators.url(url):  # Validate the URL
                        canonical_url = get_canonical_url(url)  # Get canonical version
                        unique_urls.add(canonical_url)
            except Exception as e:
                print(f"Error processing row: {row}\n{e}")
    
    # Print valid, unique canonical URLs to stdout
    for url in sorted(unique_urls):
        print(url)

if __name__ == "__main__":
    file_name = "simple_qa_test_set.csv"  # Replace with your actual file name
    extract_and_clean_urls(file_name)

