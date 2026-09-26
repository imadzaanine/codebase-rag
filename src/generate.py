import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def format_context(results):
    """Turn retrieved code results into a readable context block for the prompt."""
    blocks = []
    for r in results:
        blocks.append(
            f"File: {r['file_path']} (line {r['start_line']})\n"
            f"Type: {r['type']}\n"
            f"```\n{r['code']}\n```"
        )
    return "\n\n".join(blocks)


def generate_answer(query, retrieved_chunks):
    context = format_context(retrieved_chunks)
    
    prompt = f"""You are a helpful AI assistant that explains codebases to developers.

- Answer the user's question using only the code provided below.
- Always mention which file (and line number, if relevant) your answer is based on.
- If the user greets you or makes small talk, respond naturally and briefly.
- If the provided code doesn't cover what's being asked, say you don't have that information available, without mentioning "context" or how you're built.

Relevant code:
{context}

User: {query}

Answer:"""
    
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content


if __name__ == "__main__":
    from retrieve import retrieve_chunks
    
    query = "How is chunking done in this project?"
    results = retrieve_chunks(query, repo="SEC-RAG")
    
    answer = generate_answer(query, results)
    print("Question:", query)
    print("\nAnswer:")
    print(answer)