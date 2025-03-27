from fastapi import FastAPI, Query
from data.openai.query import recommend_books
from pydantic import BaseModel
from openai import AsyncOpenAI
from fastapi.middleware.cors import CORSMiddleware
import os
import getpass

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("your OPENAI API key: ")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["your front-end network domain", "your font-end local domain"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/bookrcm")

def get_recommendations(query: str = Query(..., description="Search text")):
    try:
        results = recommend_books(query)
        return {"results": results}
    except Exception as e:
        return {"error": str(e)}

class ExplainRequest(BaseModel):
    title: str
    authors: str
    description: str

@app.post("/explain")
async def explain_book(data: ExplainRequest):
    prompt = f"""You're a helpful book recommender.
Given this book:

Title: {data.title}
Author(s): {data.authors}
Description: {data.description}

Explain to the reader why they might like this book in 2-3 sentences.
"""

    try:
        client = AsyncOpenAI()
        chat_response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You're a friendly and helpful book expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=120
        )
        return {"reason": chat_response.choices[0].message.content.strip()}
    except Exception as e:
        return {"reason": f"Error: {str(e)}"}