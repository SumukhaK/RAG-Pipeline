from src.data_loader import load_all_documents
from src.vectorstore import FaissVectorStore
from src.search import RAGSearch

# Example usage
if __name__ == "__main__":
    
    docs = load_all_documents("data")
    store = FaissVectorStore("faiss_store")
    print(docs)
    store.build_from_documents(docs)
    store.load()
    print(store.query("list the different types of data structures? Explain one sentence each about different types of data structures?", top_k=3))
    rag_search = RAGSearch()
    query = "list the different types of data structures? Explain one sentence each about different types of data structures?"
    summary = rag_search.search_and_summarize(query, top_k=3)
    print("Summary:", summary)