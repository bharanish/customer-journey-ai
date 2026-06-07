from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY
import json

llm = ChatOpenAI(
    model="gpt-4o",
    api_key=OPENAI_API_KEY
)

def generate_visualization(question, columns):

    prompt = f"""
    You are a BI visualization expert.

    User Question:
    {question}

    Dataset Columns:
    {columns}

    Choose the best chart type.

    Allowed:
    - bar
    - line
    - pie
    - scatter
    - table

    Return JSON only:

    {{
        "chart_type":"bar",
        "x":"column_name",
        "y":"column_name"
    }}
    """

    response = llm.invoke(prompt)

    # print("===== VISUALIZATION RESPONSE =====")
    # print(response.content)

    content = (
        response.content
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    try:
        return json.loads(content)

    except Exception as e:

        print("Visualization parsing error:", e)
        print("Raw response:", response.content)

        return {
            "chart_type": "bar",
            "x": columns[0],
            "y": columns[1] if len(columns) > 1 else columns[0]
        }
