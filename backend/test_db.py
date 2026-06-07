import pandas as pd

from database import engine

query = """
SELECT *
FROM customer_journey
LIMIT 5
"""

df = pd.read_sql(
    query,
    engine
)

print(df)
