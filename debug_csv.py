import pandas as pd
try:
    df = pd.read_csv("energia_renovable(in).csv")
    print(df.columns.tolist())
    print(df.head(2))
except Exception as e:
    print(e)
