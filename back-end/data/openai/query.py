from langchain_openai import OpenAIEmbeddings
from langchain_milvus import Milvus
from pymilvus import connections, Collection

embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")

connections.connect(alias="default", uri="http://210.86.230.107:19530")
collection_name = "books_collection"
collection = Collection(collection_name)

vectorstore = Milvus(
    embedding_function=embedding_model,
    connection_args={"uri": "http://210.86.230.107:19530"},
    collection_name=collection_name
)

def recommend_books(query: str):
    total_docs = collection.num_entities
    results = vectorstore.similarity_search(query, k=total_docs)
    return [r.metadata for r in results]

if __name__ == "__main__":
    user_query = "teen"
    top_books = recommend_books(user_query)

    print("\nResult:\n")
    for i, book in enumerate(top_books, 1):
        print(f"{i}. {book.get('title')} by {book.get('authors')}: {book.get('description')}")
