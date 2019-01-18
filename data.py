import pandas as pd

wboard, wch = 0, 0
a, b = [], []

old = pd.read_csv("data.csv")

w = 0
for i in xrange(1,25):
    for j in xrange(2):
	a = [i, j, old["voltage"][w], old["current"][w], 10, 20]
	b.append(a)
	w+=1

df = pd.DataFrame(b, columns = ["sektor", "tpcch", "voltage", "current", "rampup", "rampdown"])
df.to_csv('data.csv', encoding='utf-8', index=False)
