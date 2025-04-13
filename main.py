
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import os

app = FastAPI()

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Tone prompt templates
PROMPTS = {
    "casual": "You're writing a casual, friendly daily newsletter. Summarize each headline with a brief, conversational tone. Add an emoji per story and include the source in brackets.",
    "serious": "You're writing a professional, neutral daily newsletter. Summarize each headline concisely with no emojis and include the source in brackets.",
    "humorous": "You're writing a witty, sarcastic newsletter. Summarize each headline in a humorous tone with jokes or light sarcasm. Include an emoji and the source.",
    "investor": "You're writing for financial analysts. Summarize each headline with context on economic or market impact. Include the source in brackets and avoid emojis."
}

class SummaryRequest(BaseModel):
    headlines: list[str]
    tone: str = "casual"

@app.post("/generate")
def generate_summary(data: SummaryRequest):
    if data.tone not in PROMPTS:
        raise HTTPException(status_code=400, detail="Unsupported tone")

    prompt = PROMPTS[data.tone]
    content = "\n".join([f"- {headline}" for headline in data.headlines])

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Summarize the following headlines:\n{content}"}
            ],
            temperature=0.7
        )
        summary = response['choices'][0]['message']['content']
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
