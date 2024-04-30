from bs4 import BeautifulSoup
import os
import unicodedata

class ItemExtractor:
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
        # Find all tags that contain the item_text: e.g., "Item 7."
        tags = [
            tag for tag in self.soup.find_all(
                text=lambda text: text and item_text.lower() in self.normalize_text(text)
            )
        ]
        # Return the second occurrence if it exists (first occurrence is the table of contents)
        if len(tags) >= 2:
            return tags[1].parent
        return None

    def extract_content(self, from_tag, to_tag):
        # Extract the content between these tags
        content = ''
        if from_tag and to_tag:
            content += from_tag.get_text(separator=' ', strip=True) + '\n'
            element = from_tag.find_next()
            while element and element != to_tag:
                if element.name == 'div' and element.find_parent('div') is None:
                    text = element.get_text(separator=' ', strip=True)
                    if text:
                        content += text + '\n'
                element = element.find_next()

        return content

    def extract_item_7_7a_content(self):
        item_7_content_tag = self.find_second_occurrence("Item 7.")
        item_8_content_tag = self.find_second_occurrence("Item 8.")
        return self.extract_content(item_7_content_tag, item_8_content_tag)
    
    def extract_item_1_1a_content(self):
        # Find the content tags for Item 7 and Item 7A
        item_1_content_tag = self.find_second_occurrence("Item 1.")
        item_1b_content_tag = self.find_second_occurrence("Item 1B.")
        return self.extract_content(item_1_content_tag, item_1b_content_tag)

    def extract_item_8_content(self):
        item_8_content_tag = self.find_second_occurrence("Item 8.")
        item_9_content_tag = self.find_second_occurrence("Item 9.")
        return self.extract_content(item_8_content_tag, item_9_content_tag)

    def save_content_to_file(self, content, output_path):
        directory = os.path.dirname(output_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        # Save the extracted content to a file
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(content)

# Example usage:
if __name__ == "__main__":
    extractor = ItemExtractor('./sec-edgar-filings/AAPL/10-K/0000320193-17-000070/primary-document.html')
    item_7_text = extractor.extract_item_7_7a_content()
    print(item_7_text)