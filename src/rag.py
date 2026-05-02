import os, re, time
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_core.documents import Document

DEBALES_URLS = [
    "https://debales.ai",
    "https://debales.ai/about",
    "https://debales.ai/product",
    "https://debales.ai/integrations",
    "https://debales.ai/pricing",
    "https://debales.ai/blog",
]
PERSIST_DIR = Path(__file__).parent.parent / "data" / "chroma_db"
COLLECTION_NAME = "debales_kb"

def _scrape_url(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
    except Exception as exc:
        print(f"  [Scraper] WARN: {url}: {exc}")
        return ""
    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script","style","nav","footer","header","iframe","noscript"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    return re.sub(r"\n{3,}", "\n\n", text).strip()

def scrape_debales():
    docs = []
    for url in DEBALES_URLS:
        print(f"  [Scraper] Fetching {url}")
        text = _scrape_url(url)
        if text:
            docs.append(Document(page_content=text, metadata={"source": url}))
        time.sleep(0.5)
    return docs

def get_embeddings():
    return SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

def build_vectorstore(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(docs)
    store = Chroma.from_documents(chunks, get_embeddings(), collection_name=COLLECTION_NAME, persist_directory=str(PERSIST_DIR))
    store.persist()
    return store

def load_vectorstore():
    return Chroma(collection_name=COLLECTION_NAME, embedding_function=get_embeddings(), persist_directory=str(PERSIST_DIR))

class RAGPipeline:
    _store = None

    def _get_store(self):
        if RAGPipeline._store:
            return RAGPipeline._store
        if PERSIST_DIR.exists() and any(PERSIST_DIR.iterdir()):
            print("  [RAG] Loading existing vector store...")
            RAGPipeline._store = load_vectorstore()
        else:
            print("  [RAG] Building vector store...")
            PERSIST_DIR.mkdir(parents=True, exist_ok=True)
            RAGPipeline._store = build_vectorstore(scrape_debales())
        return RAGPipeline._store

    def retrieve(self, query, k=4):
        results = self._get_store().similarity_search(query, k=k)
        if not results:
            return ""
        parts = [f"[{i}] (source: {d.metadata.get('source','')})\n{d.page_content}" for i,d in enumerate(results,1)]
        return "\n\n---\n\n".join(parts)

    def rebuild(self):
        import shutil
        if PERSIST_DIR.exists():
            shutil.rmtree(PERSIST_DIR)
        PERSIST_DIR.mkdir(parents=True, exist_ok=True)
        RAGPipeline._store = build_vectorstore(scrape_debales())
