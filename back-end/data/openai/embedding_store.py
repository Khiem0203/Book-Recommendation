import os
import pandas as pd
from langchain_core.documents import Document
from langchain_milvus import Milvus
from langchain_openai import OpenAIEmbeddings
from tqdm import tqdm
import getpass

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("YOUR_OPENAI_API_KEY: ")

csv_path = "../dataset/new/books_full.csv"
df = pd.read_csv(csv_path)

df.fillna({
    "title": "",
    "description": "",
    "thumbnail": "",
    "author": "",
    "publisher": "",
    "publishing_year": 0,
    "num_pages": 0,
    "language": "",
    "categories": "",
    "link": ""
}, inplace=True)

df["publishing_year"] = pd.to_numeric(df["publishing_year"], errors="coerce").fillna(0).astype(int)
df["num_pages"] = pd.to_numeric(df["num_pages"], errors="coerce").fillna(0).astype(int)
df["id"] = pd.to_numeric(df["id"], errors="coerce").astype(int)
df.reset_index(drop=True, inplace=True)

processed_path = "processed_ids.txt"
processed_ids = set()
if os.path.exists(processed_path):
    with open(processed_path, "r") as f:
        processed_ids = set(int(line.strip()) for line in f.readlines())

embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")

collection_name = "books_dataset"
vectorstore = Milvus(
    embedding_function=embedding_model,
    connection_args={"uri": "http://127.0.0.1:19530"},
    collection_name=collection_name,
    primary_field="id",
    vector_field="vector",
    text_field="page_content",
    auto_id=False,
    index_params={
        "metric_type": "IP",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 1024}
    },
    consistency_level="Strong"
)

docs = []
batch_size = 100
total = len(df)

with open(processed_path, "a") as done_file:
    for i, row in tqdm(df.iterrows(), total=total, desc="Processing books"):
        book_id = int(row["id"])
        if book_id in processed_ids:
            continue

        text_to_embed = f"{row['title']} {row['description']} {row['author']} {row['categories']}"
        doc = Document(
            page_content=text_to_embed,
            id=book_id,
            metadata={
                "title": row["title"],
                "author": row["author"],
                "description": row["description"],
                "categories": row["categories"],
                "publisher": row["publisher"],
                "publishing_year": row["publishing_year"],
                "num_pages": row["num_pages"],
                "language": row["language"],
                "thumbnail": row["thumbnail"],
                "link": row["link"]
            }
        )
        docs.append(doc)

        if len(docs) >= batch_size:
            vectorstore.add_documents(docs, ids=[d.id for d in docs])
            for d in docs:
                done_file.write(f"{d.id}\n")
            done_file.flush()
            print(f"Uploaded batch of {len(docs)} books")
            docs = []

    if docs:
        vectorstore.add_documents(docs, ids=[d.id for d in docs])
        for d in docs:
            done_file.write(f"{d.id}\n")
        print(f"Uploaded final batch of {len(docs)} books")

print("Done embedding and storing to Milvus.")
