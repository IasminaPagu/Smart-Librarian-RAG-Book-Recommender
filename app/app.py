# file: app.py
import os
import streamlit as st
import chromadb
from openai import OpenAI
from get_summary_tool import get_summary_by_title  # asigură-te că fișierul e în project-root/
                                                   # și data/book_summaries.json există

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "book_summaries"
OPENAI_MODEL = "gpt-4o-mini"
EMBED_MODEL = "text-embedding-3-small"


api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OPENAI_API_KEY is not set in environment.")
    st.stop()

client_openai = OpenAI(api_key=api_key)
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_summary_by_title",
            "description": "Returneaza rezumatul complet al unei carti dupa titlul exact.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Titlul exact al cărții pentru care vrei rezumatul."
                    }
                },
                "required": ["title"]
            }
        },
    }
]

st.title("📚 Smart Librarian: Book Recommendation Chatbot")
st.write("Cere o carte după tema, subiect sau stare. Ex.: „Vreau o carte despre prietenie și magie”.")

user_query = st.text_input("Ce fel de carte cauți?")

if user_query:
    try:
        emb_resp = client_openai.embeddings.create(
            input=user_query,
            model=EMBED_MODEL
        )
        query_emb = emb_resp.data[0].embedding
    except Exception as e:
        st.error(f"Eroare la generarea embedding-ului: {e}")
        st.stop()

    results = collection.query(query_embeddings=[query_emb], n_results=3)
    ids = results.get("ids", [[]])[0]
    docs = results.get("documents", [[]])[0]

    if not ids:
        st.warning("Nu am găsit potriviri pentru interogarea ta.")
        st.stop()

    context_blocks = []
    for i, (bid, bsum) in enumerate(zip(ids, docs), start=1):
        context_blocks.append(f"{i}. Title: {bid}\nSummary: {bsum}")
    context_str = "\n\n".join(context_blocks)

    system_msg = {
        "role": "system",
        "content": (
            "Ești un asistent care recomandă cărți pe baza unor potriviri dintr-un vector store. "
            "Analizează potrivirile și alege o singură carte potrivită pentru utilizator. "
            "DUPĂ ce alegi cartea, cere tool-ul get_summary_by_title(title) pentru rezumatul complet. "
            "În răspunsul tău conversațional NU include rezumatul complet; spune doar titlul și de ce îl recomanzi. "
            "Aplicația va afișa rezumatul complet separat."
        )
    }

    user_msg = {
        "role": "user",
        "content": (
            f"Întrebarea utilizatorului: \"{user_query}\"\n\n"
            f"Potriviri candidate (top 3):\n{context_str}\n\n"
            "Alege exact UN titlu din listă. După ce alegi, apelează tool-ul cu titlul exact."
        )
    }

    try:
        first = client_openai.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[system_msg, user_msg],
            tools=tools,
            tool_choice="auto",
            temperature=0.3
        )
    except Exception as e:
        st.error(f"Eroare la apelul LLM: {e}")
        st.stop()

    assistant_msg = first.choices[0].message
    tool_calls = getattr(assistant_msg, "tool_calls", None)

    full_summary_text = None
    final_answer = None

    if tool_calls:
        for tc in tool_calls:
            if tc.function.name == "get_summary_by_title":
                import json as _json
                args = _json.loads(tc.function.arguments or "{}")
                title = args.get("title", "")
                full_summary_text = get_summary_by_title(title)

                tool_msg = {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": "get_summary_by_title",
                    "content": full_summary_text
                }

                try:
                    second = client_openai.chat.completions.create(
                        model=OPENAI_MODEL,
                        messages=[system_msg, user_msg, assistant_msg, tool_msg],
                        temperature=0.3
                    )
                    final_answer = second.choices[0].message.content
                except Exception as e:
                    final_answer = f"(Eroare la generarea răspunsului final: {e})"
    else:
        chosen_title = ids[0]
        st.info("⚠️ Modelul nu a cerut tool-ul; afișez recomandarea de bază.")
        prompt = (
            f"Recomandă cartea '{chosen_title}' pentru cererea: '{user_query}'. "
            f"Răspunde conversațional, scurt (2-3 fraze)."
        )
        try:
            fallback = client_openai.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            final_answer = fallback.choices[0].message.content
            full_summary_text = get_summary_by_title(chosen_title)
        except Exception as e:
            final_answer = f"(Eroare GPT fallback: {e})"
            full_summary_text = None

    if final_answer:
        st.success(final_answer)
    if full_summary_text:
        with st.expander("📖 Rezumat complet"):
            st.write(full_summary_text)
