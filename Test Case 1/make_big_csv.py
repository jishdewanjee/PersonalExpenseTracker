# make_big_csv.py
import csv, random, datetime
N=100000
cats=["Food","Travel","Bills","Misc"]
start=datetime.date(2023,1,1)
with open("expenses.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["date","category","amount","description"])
    for i in range(N):
        d=start+datetime.timedelta(days=random.randint(0,700))
        w.writerow([d.isoformat(), random.choice(cats), "{:.2f}".format(random.uniform(1,200)), "seed {}".format(i)])
print("done")