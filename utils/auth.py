import pandas as pd
import os

def load_apartments(path="data/apartments.csv") -> pd.DataFrame:
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame(columns=["slug", "nom"])

