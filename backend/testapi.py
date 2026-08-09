from ollama import chat

response = chat(
    model="qwen3:8b",
    messages=[
        {
            "role": "user",
            "content": """
Translate this sentence into Korean.

Return only the Korean translation.

Text:
Long time no see.
"""
        }
    ]
)

print(response["message"]["content"])