# file: scripts/load_to_chroma.py
"""
Loads book summaries from data/book_summaries.json, generates OpenAI embeddings, and stores them in ChromaDB.
"""
import json
import os
import chromadb
from openai import OpenAI

# Load OpenAI API key from environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("🔐 OPENAI_API_KEY nu este setat!")

# Initialize OpenAI client
client_openai = OpenAI(api_key=api_key)

# Initialize ChromaDB persistent client
chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_or_create_collection(name="book_summaries")

# Load summaries from JSON (expects a list of dicts with 'title' and 'summary')
with open("data/book_summaries.json", "r", encoding="utf-8") as f:
    summaries = json.load(f)

ids, documents, embeddings = [], [], []

for book in summaries:
    title = book.get("title")
    summary = book.get("summary")
    if not title or not summary:
        print(f"⚠️ Skipping entry with missing title or summary: {book}")
        continue
    try:
        response = client_openai.embeddings.create(
            input=summary,
            model="text-embedding-3-small"
        )
        emb = response.data[0].embedding
        ids.append(title)
        documents.append(summary)
        embeddings.append(emb)
        print(f"✅ Embedded: {title}")
    except Exception as e:
        print(f"❌ Error embedding {title}: {e}")

if ids:
    collection.add(ids=ids, documents=documents, embeddings=embeddings)
    print(f"✅ Uploaded {len(ids)} books to ChromaDB.")
else:
    print("❌ No valid books to upload.")
