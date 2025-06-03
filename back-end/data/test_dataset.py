import pandas as pd

input_file = "./dataset/new/books_full.csv"
output_file = "books_test.csv"

df = pd.read_csv(input_file, nrows=1)

df.to_csv(output_file, index=False, encoding="utf-8-sig")

print("Đã ghi 2 dòng đầu tiên kèm cột id vào", output_file)
