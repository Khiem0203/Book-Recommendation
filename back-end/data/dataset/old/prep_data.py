import pandas as pd
df = pd.read_csv('books.csv')

def generate_amazon_link(isbn):
    if pd.isna(isbn):
        return ''
    return f"https://www.amazon.com/dp/{isbn}"

df['amazon_link'] = df['isbn10'].apply(generate_amazon_link)

df.to_csv('books_ver2.csv', index=False)

print("Done")
