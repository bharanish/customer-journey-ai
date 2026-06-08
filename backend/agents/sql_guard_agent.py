def validate_sql(sql: str):

    sql = sql.strip().upper()

    return sql.startswith("SELECT")
