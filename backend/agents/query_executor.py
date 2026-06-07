import pandas as pd
from database import engine

def execute_query(sql):

    df = pd.read_sql(sql, engine)

    return df
