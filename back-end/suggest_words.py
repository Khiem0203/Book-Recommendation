import pandas as pd

df = pd.read_csv("./data/dataset/new/books_full.csv")

def fetch_book_suggestions(query):
    query = query.lower()
    suggestions = set()

    for _, row in df.iterrows():
        title = str(row.get("title", "")).lower()
        authors = str(row.get("author", "")).lower()
        categories = str(row.get("categories", "")).lower()

        if query in title:
            suggestions.add(row["title"])
        if query in authors:
            suggestions.add(row["author"])
        if query in categories:
            suggestions.update([cat.strip() for cat in categories.split("/")])

        if len(suggestions) >= 10:
            break

    return [{"query": s} for s in list(suggestions)[:10]]
