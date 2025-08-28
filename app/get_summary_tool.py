import json
import os

def get_summary_by_title(title: str) -> str:
    """Return the full summary for a given book title from the local JSON file."""
    # Adjust the path if needed
    json_path = os.path.join(os.path.dirname(__file__), "data", "book_summaries.json")
    if not os.path.exists(json_path):
        return f"Book summaries file not found at {json_path}."
    with open(json_path, "r", encoding="utf-8") as f:
        books = json.load(f)
    for book in books:
        if book["title"].lower() == title.lower():
            return book["summary"]
    return f"No summary found for '{title}'."

# Example usage:
if __name__ == "__main__":
    print(get_summary_by_title("The Hobbit"))
