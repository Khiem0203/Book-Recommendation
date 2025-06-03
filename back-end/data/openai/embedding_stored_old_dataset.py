import os
import getpass
import pandas as pd
from langchain_core.documents import Document
from langchain_milvus import Milvus
from langchain_openai import OpenAIEmbeddings

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("YOUR_OPENAI_API_KEY: ")

collection_name = "books_collection"

df = pd.read_csv("/back-end/data/dataset/old/books_ver2.csv")

embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")

df = df.fillna({"subtitle": "", "authors": "", "categories": "", "description": "","thumbnail": "","amazon_link": "",
                "published_year": 0, "average_rating": 0, "num_pages": 0, "ratings_count": 0})

docs = []

batch_size = 1000
total_books = len(df)
vectorstore = Milvus.from_documents(
    documents=docs,
    connection_args={"uri":"http://127.0.0.1:19530"},
    embedding=embedding_model,
    collection_name=collection_name,
    primary_field="id",
    vector_field="vector",
    text_field="text",
    auto_id=False,
    drop_old=True,
    index_params={
        "metric_type": "IP",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 1024}
    },
    consistency_level = "Strong"
)

for i in range(0, total_books, batch_size):
    docs = []
    batch = df.iloc[i: i + batch_size]

    for _, row in batch.iterrows():
        try:
            isbn13 = int(row["isbn13"])
        except ValueError:
            continue

        text_to_embed = f"{row['title']} {row['subtitle']} {row['authors']} {row['categories']} {row['description']}"
        doc = Document(page_content=text_to_embed, metadata={
            "isbn13": isbn13,
            "isbn10": row["isbn10"],
            "title": row["title"],
            "subtitle": row["subtitle"],
            "authors": row["authors"],
            "categories": row["categories"],
            "description": row["description"],
            "published_year": int(row["published_year"]),
            "average_rating": float(row["average_rating"]),
            "num_pages": int(row["num_pages"]),
            "ratings_count": int(row["ratings_count"]),
            "thumbnail": str(row["thumbnail"]),
            "amazon_link": str(row["amazon_link"])
        })
        docs.append(doc)

    if docs:
        vectorstore.add_documents(docs)
        print(f"Upload {len(docs)} books to Milvus (Total: {i + len(docs)} / {total_books})")

print("Store successfully")
