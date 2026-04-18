import os
from groq import Groq
from app.core.config import settings
from app.core.timeout import timeout_config
from app.core.token_tracker import token_tracker

#debug=settings.DEBUG


client = Groq(
        api_key=settings.GROQ_API_KEY,
        timeout=timeout_config.read
    )

def generate_response(prompt: str, query: str = "") -> str:
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=settings.MODEL_NAME
    )
    
    # Track token usage
    if chat_completion.usage:
        token_tracker.track(
            query=query or prompt[:100],
            prompt_tokens=chat_completion.usage.prompt_tokens,
            completion_tokens=chat_completion.usage.completion_tokens,
            total_tokens=chat_completion.usage.total_tokens,
            model=settings.MODEL_NAME,
        )

    return chat_completion.choices[0].message.content


