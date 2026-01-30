import csv
try:
    with open("energia_renovable(in).csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        print("Headers:", headers)
        row1 = next(reader)
        print("Row1:", row1)
except Exception as e:
    print("Error:", e)
