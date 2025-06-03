import pandas as pd
import glob
import os

folder_path = "."

csv_files = glob.glob(os.path.join(folder_path, "*.csv"))

df_list = []
for i, file in enumerate(csv_files):
    df = pd.read_csv(file)
    if i == 0:
        df_list.append(df)
    else:
        df_list.append(df.iloc[1:] if df.columns.equals(df_list[0].columns) else df)

combined_df = pd.concat(df_list, ignore_index=True)

combined_df["id"] = range(1, len(combined_df) + 1)

cols = combined_df.columns.tolist()
cols.insert(0, cols.pop(cols.index("id")))
combined_df = combined_df[cols]

combined_df.to_csv("./books_full.csv", index=False, encoding="utf-8-sig")
print("Done")
