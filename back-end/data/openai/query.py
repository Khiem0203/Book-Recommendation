from langchain_openai import OpenAIEmbeddings
from langchain_milvus import Milvus
from pymilvus import connections, Collection

embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")

connections.connect(alias="default", uri="http://127.0.0.1:19530")
collection_name = "books_dataset"
collection = Collection(collection_name)
text_field = "page_content"

vectorstore = Milvus(
    embedding_function=embedding_model,
    connection_args={"uri": "http://127.0.0.1:19530"},
    collection_name=collection_name,
    text_field="page_content"
)

def recommend_books(query: str):
    total_docs = collection.num_entities
    results = vectorstore.similarity_search(query, k=total_docs)
    return [
        {
            "id": doc.id,
            **doc.metadata
        }
        for doc in results
    ]

if __name__ == "__main__":
    user_query = "teen"
    top_books = recommend_books(user_query)

    print("\nResult:\n")
    for i, book in enumerate(top_books, 1):
        print(f"{i}. [{book['id']}] {book.get('title')} by {book.get('author')}")