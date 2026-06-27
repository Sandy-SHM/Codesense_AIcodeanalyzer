import os
import chromadb
from chromadb.utils import embedding_functions
from typing import Optional

CHROMA_PATH = "./chroma_db"

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = chroma_client.get_or_create_collection(
    name="code_docs",
    embedding_function=embedding_fn,
    metadata={"hnsw:space": "cosine"}
)

SEED_DOCS = [
    {
        "text": "Python list comprehensions are faster than for loops for simple transformations. Use [x for x in items if condition] instead of appending in a loop.",
        "id": "py_list_comp",
        "meta": {"language": "python", "topic": "performance"}
    },
    {
        "text": "Always use context managers (with statement) when working with files in Python. This ensures files are properly closed even if an exception occurs.",
        "id": "py_context_manager",
        "meta": {"language": "python", "topic": "best_practices"}
    },
    {
        "text": "In JavaScript, prefer const over let, and let over var. Use arrow functions for callbacks. Always handle Promise rejections with try/catch in async functions.",
        "id": "js_modern",
        "meta": {"language": "javascript", "topic": "best_practices"}
    },
    {
        "text": "SQL N+1 problem: avoid running queries inside loops. Use JOIN or IN clause to fetch related data in a single query instead of one query per record.",
        "id": "sql_n_plus_1",
        "meta": {"language": "sql", "topic": "performance"}
    },
    {
        "text": "Time complexity: O(1) constant, O(log n) binary search, O(n) linear scan, O(n log n) merge sort, O(n²) nested loops. Always aim for the lowest complexity possible.",
        "id": "big_o",
        "meta": {"language": "general", "topic": "algorithms"}
    },
    {
        "text": "Python type hints improve code readability and enable static analysis. Use def func(name: str, age: int) -> bool: for function signatures.",
        "id": "py_type_hints",
        "meta": {"language": "python", "topic": "best_practices"}
    },
    {
        "text": "React hooks: useState for local state, useEffect for side effects, useCallback to memoize functions, useMemo for expensive calculations. Always include dependency arrays.",
        "id": "react_hooks",
        "meta": {"language": "javascript", "topic": "react"}
    },
    {
        "text": "Exception handling best practice: catch specific exceptions, not bare except. Log the error with context. Never silently swallow exceptions.",
        "id": "exception_handling",
        "meta": {"language": "general", "topic": "best_practices"}
    },
    {
        "text": "REST API design: use nouns not verbs in URLs (/users not /getUsers), use HTTP methods correctly (GET read, POST create, PUT update, DELETE remove), return proper status codes.",
        "id": "rest_design",
        "meta": {"language": "general", "topic": "api_design"}
    },
    {
        "text": "Database indexing: add indexes on columns used in WHERE clauses and JOIN conditions. Composite indexes follow leftmost prefix rule. Too many indexes slow down writes.",
        "id": "db_indexing",
        "meta": {"language": "sql", "topic": "performance"}
    },
    {
        "text": "Python generators are memory efficient for large datasets. Use yield instead of return to create iterators. Use (x for x in range(n)) instead of list comprehension when you only need to iterate.",
        "id": "py_generators",
        "meta": {"language": "python", "topic": "performance"}
    },
    {
        "text": "SOLID principles: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion. Each class should have one reason to change.",
        "id": "solid",
        "meta": {"language": "general", "topic": "design_patterns"}
    },
]

def ingest_docs():
    """Ingest seed documentation into ChromaDB on startup."""
    existing = collection.count()
    if existing >= len(SEED_DOCS):
        print(f"[RAG] ChromaDB already has {existing} docs, skipping ingest.")
        return

    texts = [d["text"] for d in SEED_DOCS]
    ids = [d["id"] for d in SEED_DOCS]
    metadatas = [d["meta"] for d in SEED_DOCS]

    collection.upsert(documents=texts, ids=ids, metadatas=metadatas)
    print(f"[RAG] Ingested {len(SEED_DOCS)} documents into ChromaDB.")

def get_relevant_context(code: str, language: str, n_results: int = 3) -> str:
    """Retrieve relevant documentation snippets for the given code."""
    try:
        query = f"{language} code: {code[:500]}"
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where={"language": {"$in": [language, "general"]}} if language in ["python", "javascript", "sql"] else None
        )

        if not results["documents"] or not results["documents"][0]:
            return ""

        docs = results["documents"][0]
        context_parts = []
        for i, doc in enumerate(docs, 1):
            context_parts.append(f"{i}. {doc}")

        return "\n".join(context_parts)
    except Exception as e:
        print(f"[RAG] Context retrieval error: {e}")
        return ""

def add_custom_docs(texts: list[str], ids: list[str], metadatas: Optional[list[dict]] = None):
    """Add custom documentation to the knowledge base."""
    if metadatas is None:
        metadatas = [{"language": "general", "topic": "custom"} for _ in texts]
    collection.upsert(documents=texts, ids=ids, metadatas=metadatas)
    return {"added": len(texts)}
