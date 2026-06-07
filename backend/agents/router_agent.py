def classify_question(question):

    question = question.lower()

    analytics_keywords = [
        "revenue",
        "sales",
        "channel",
        "campaign",
        "customer",
        "device",
        "event",
        "count",
        "sum",
        "average",
        "avg",
        "total",
        "highest",
        "lowest",
        "top",
        "show",
        "list",
        "compare",
        "trend"
    ]

    if any(word in question for word in analytics_keywords):
        return "DATA_ANALYSIS"

    return "GENERAL_QUESTION"
