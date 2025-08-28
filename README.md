# 📚 Smart Librarian – AI + RAG + Tool Completion

Acest proiect implementeaza un **chatbot AI** care recomanda carti pe baza intereselor utilizatorului, folosind:

- **OpenAI GPT** pentru conversatie
- **ChromaDB** pentru stocarea si regasirea semantica a rezumatelor de carti (RAG)
- **Tool Calling** (`get_summary_by_title`) pentru a returna rezumatul complet dupa recomandare
- **Streamlit** pentru UI simpla

---

## 🚀 Functionalitati

1. **Baza de date cu rezumate** – `book_summaries.json` contine 30+ carti, fiecare cu titlu si rezumat scurt.
2. **Incarcare in ChromaDB** – scriptul `load_to_chroma.py` genereaza embeddings cu `text-embedding-3-small` si le salveaza in colectia `book_summaries`.
3. **Chatbot conversational** – `app.py`:
   - primeste intrebari de la utilizator (ex. *"Vreau o carte despre prietenie si magie"*)
   - cauta semantic in ChromaDB (RAG)
   - GPT alege cartea potrivita
   - GPT apeleaza tool-ul `get_summary_by_title` pentru rezumatul complet
   - UI afiseaza recomandarea conversationala si rezumatul complet (intr-un expander)
4. **Tool Calling** – `get_summary_tool.py` returneaza rezumatul complet din fisierul JSON.

---

## 🛠️ Instalare si configurare

### 1. Cloneaza proiectul
```bash
git clone <repo_url>
cd <repo_folder>


### Creare mediu virtual
python -m venv .venv
source .venv/bin/activate     # pe Linux / macOS
.venv\Scripts\activate        # pe Windows

###4. Instalare dependinte
pip install -r requirements.txt

###5. Seteaza cheia OpenAI in virtual environment
export OPENAI_API_KEY="your_open_ai_key"    # Linux / macOS
setx OPENAI_API_KEY "your_open_ai_key"      # Windows (CMD)



##▶️ Rulare
###1. Incarca cartile in ChromaDB
python scripts/load_to_chroma.py

###2. Ruleaza chatbotul cu Streamlit(asigura-te ca esti in directorul app)
streamlit run app.py

###3. Se va deschide interfata web la http://localhost:8501


##📌 Exemple de intrebari pentru testare
Vreau o carte despre prietenie si magie
Ce recomanzi pentru cineva care iubeste povesti de razboi?
Vreau o poveste despre libertate si control social
Ce este 1984?
