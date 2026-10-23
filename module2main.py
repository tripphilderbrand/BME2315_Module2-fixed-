import pandas as pd

df = pd.read_csv("Module2_FSHD_Dataset (1).csv") 

for header in df.columns:
    print(header) 
