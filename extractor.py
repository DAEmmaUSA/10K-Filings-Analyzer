from bs4 import BeautifulSoup
import os
import unicodedata

class Item7Extractor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.soup = None
        self._load_html()

    def _load_html(self):
        # Load HTML content from the specified file path
        with open(self.file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        self.soup = BeautifulSoup(html_content, 'html.parser')

    def normalize_text(self, text):
        # Normalize unicode characters, replace non-breaking spaces, and convert to lower case
        return unicodedata.normalize('NFKD', text).lower()

    def find_second_occurrence(self, item_text):
        # Find all tags that contain the item_text
        tags = [
            tag for tag in self.soup.find_all(
                text=lambda text: text and item_text.lower() in self.normalize_text(text)
            )
        ]
        # Return the second occurrence if it exists
        if len(tags) >= 2:
            return tags[1].parent  # Return the parent of the text node
        return None

    def extract_item_7_content(self):
        # Find the content tags for Item 7 and Item 7A
        item_7_content_tag = self.find_second_occurrence("Item 7.")
        item_7a_content_tag = self.find_second_occurrence("Item 7A.")

        # Extract the content between these tags
        item_7_content = ''
        if item_7_content_tag and item_7a_content_tag:
            item_7_content += item_7_content_tag.get_text(separator=' ', strip=True) + '\n'
            # Collect all elements until reaching the start of Item 7A
            element = item_7_content_tag.find_next()
            while element and element != item_7a_content_tag:
                if element.name == 'div' and element.find_parent('div') is None:
                    text = element.get_text(separator=' ', strip=True)
                    if text:
                        item_7_content += text + '\n'
                element = element.find_next()

        return item_7_content
    
    def save_content_to_file(self, content, output_path):
        directory = os.path.dirname(output_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        # Save the extracted content to a file
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(content)

# Example usage:
if __name__ == "__main__":
    extractor = Item7Extractor('./sec-edgar-filings/AAPL/10-K/0000320193-17-000070/primary-document.html')
    item_7_text = extractor.extract_item_7_content()
    print(item_7_text)