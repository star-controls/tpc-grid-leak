import pandas as pd

wboard, wch = 0, 0
a, b = [], []

for i in xrange(1,25):
    for j in xrange(2):
	a = [i, j, 115]
        b.append(a)

df = pd.DataFrame(b, columns = ["sektor", "tpcch", "voltage"])
df.to_csv('data.csv', encoding='utf-8', index=False)

