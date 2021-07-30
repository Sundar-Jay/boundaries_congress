import json

# Opening JSON file

json_input_file_path = '/Users/jaysunda/Sundar/Personal/IU-DS/Final-Project/src/json_output/Cleaned-CREC-2021-06-08.json'
f = open(json_input_file_path,)

data = json.load(f)

# print(len(data))

# for count, value in enumerate(data):
    # print(count, value)


import pandas as pd

df = pd.read_json(json_input_file_path)

# print(df.describe())

df_rows, df_columns = df.shape

print("The imported dataframe has {} rows, across {} columns".format(df_rows, df_columns))

print(df.columns)

print(df.head())

for index, row in df.iterrows():
    # print(row['CR_Section'], len(row['CR_Section']))
    print(row['title'], len(row['title']))
    print(row['Speakers'], len(row['Speakers']))
    # print(row['cleaned_text'].replace(r"\t|\n|\r",''))