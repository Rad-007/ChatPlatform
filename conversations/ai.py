import os
import asyncio
from typing import List
from chatbots.models import Bot
from .models import Conversation, Message

try:
    from pydantic_ai import Agent
except Exception:  # fallback if pydantic_ai not installed
    Agent = None    


def build_history(conv: Conversation) -> List[dict]:
    history = []
    for m in conv.messages.order_by("created_at"):
        if m.role == "system":
            history.append({"role": "system", "content": m.content})
        elif m.role == "assistant":
            history.append({"role": "assistant", "content": m.content})
        else:
            history.append({"role": "user", "content": m.content})
    return history


def _normalize_model_name(name: str) -> str:
    name = (name or "").strip()
    # Map a few legacy names to current Groq model aliases
    legacy_map = {
        "llama3-8b-8192": "llama-3.1-8b-instant",
        "llama3-70b-8192": "llama-3.1-70b-versatile",
    }
    if name in legacy_map:
        return legacy_map[name]
    return name or "llama-3.3-70b-versatile"


def generate_response(bot: Bot, conv: Conversation) -> str:
    """Generate an AI response using Pydantic AI with the Groq model.
    If pydantic_ai isn't available, a simple echo fallback is used.
    """
    groq_key = os.getenv("GROQ_API_KEY", "")
    if not groq_key:
        return "GROQ_API_KEY not configured."

    if not Agent:
        return "[AI Error] pydantic-ai not installed or incompatible. Please install/upgrade: pip install \"pydantic-ai-slim[groq]\""

    base_prompt = bot.system_prompt or "You are a helpful assistant."
    style_guidelines = (
        "\nGuidelines: Be concise. Reply in 2-3 sentences (<= ~80 words). "
        "Avoid repetition and boilerplate. Use short bullet points when useful."
    )
    system_prompt = base_prompt + style_guidelines
    # Normalize to a current Groq model alias
    model_name = _normalize_model_name(bot.model_name)
    if not model_name.startswith("groq:"):
        model_string = f"groq:{model_name}"
    else:
        model_string = model_name

    # Build a single user prompt from the last user message
    last_user = conv.messages.filter(role="user").order_by("-created_at").first()
    user_input = last_user.content if last_user else "Hello"

    try:
        agent = Agent(model_string, system_prompt=system_prompt)
        # Try synchronous run first (available in some versions)
        if hasattr(agent, "run_sync"):
            result = agent.run_sync(user_input)
            # Pydantic AI returns AgentRunResult; use .output for final text
            return getattr(result, "output", str(result))
        # Fallback to async run
        async def _run():
            res = await agent.run(user_input)
            return getattr(res, "output", str(res))
        return asyncio.run(_run())
    except Exception as e:
        return f"[AI Error] {e}"


def stream_response_chunks(bot: Bot, conv: Conversation):
    """Yield text chunks using Pydantic AI streaming.
    Falls back to a single full response if streaming isn't available.
    """
    groq_key = os.getenv("GROQ_API_KEY", "")
    if not groq_key or not Agent:
        # fall back to non-streaming single response
        yield generate_response(bot, conv)
        return

    base_prompt = bot.system_prompt or "You are a helpful assistant."
    style_guidelines = (
        "\nGuidelines: Be concise. Reply in 2-3 sentences (<= ~80 words). "
        "Avoid repetition and boilerplate. Use short bullet points when useful."
    )
    system_prompt = base_prompt + style_guidelines
    model_name = _normalize_model_name(bot.model_name)
    model_string = model_name if model_name.startswith("groq:") else f"groq:{model_name}"

    last_user = conv.messages.filter(role="user").order_by("-created_at").first()
    user_input = last_user.content if last_user else "Hello"

    async def _run():
        agent = Agent(model_string, system_prompt=system_prompt)
        async with agent.run_stream(user_input) as run:
            async for delta in run.stream_text():
                yield delta

    # Bridge async generator to sync context expected by Django streaming response
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        agen = _run()
        async def collect():
            async for d in agen:
                yield d
        ait = collect()
        while True:
            try:
                chunk = loop.run_until_complete(ait.__anext__())
            except StopAsyncIteration:
                break
            yield chunk
    except Exception as e:  # fallback to non-stream on error
        yield f"[AI Error] {e}"
