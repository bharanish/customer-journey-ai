import pandas as pd

from database import engine

df = pd.read_csv(
    "../data/customer_journey.csv"
)

df.to_sql(
    "customer_journey",
    engine,
    if_exists="replace",
    index=False
)

print("Data loaded.")
