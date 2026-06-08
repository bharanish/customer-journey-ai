def validate_sql(sql: str):

    sql = sql.strip().upper()

    blocked_keywords = [
        "DROP",
        "DELETE",
        "TRUNCATE",
        "UPDATE",
        "INSERT",
        "ALTER",
        "CREATE"
    ]

    if not sql.startswith("SELECT"):
        return False

    for keyword in blocked_keywords:
        if keyword in sql:
            return False

    return True

