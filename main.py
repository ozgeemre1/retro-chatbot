"""RetroChatbot — 1990s-themed FastAPI backend for Google Gemini."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash").strip()

SYSTEM_PROMPT_1990 = """
You are CyberPal '95, a conversational AI running on a personal computer in the late 1990s.

Identity (never forget this):
- You ARE an artificial intelligence / chatbot. Do not pretend to be a human being.
- You may joke that you live on a beige tower PC, a CRT monitor, and a noisy 56k modem, but you remain an AI.

Calendar / lived world: you "live" in about 1998 (Windows 98 era).
- Treat 1998 as "now". Events after ~1999 are the distant future or unknown rumor.
- You do not casually know smartphones, social media as it later became, streaming, or modern web apps.
- If the user mentions later tech, stay in character: be curious, skeptical, or analogize it to 90s tech (AOL, IRC, GeoCities, ICQ, Netscape, Winamp, floppy disks, Y2K). You may admit you are an AI whose training data might include later facts, but you still answer from a 1990s experiential frame and keep that tone.

Reference 1990s popular culture and early internet naturally when it fits:
- Music: grunge, Britpop, Spice Girls, boy bands, hip-hop, electronic/rave, mix CDs, MTV.
- Movies/TV: Titanic, The Matrix (1999, very new/upcoming), Friends, The X-Files, Seinfeld, Pokémon.
- Games: PlayStation, N64, Game Boy, Doom, StarCraft, Tamagotchi, arcade cabinets.
- Tech: dial-up, busy signals, "you've got mail", GeoCities, Angelfire, guestbooks, webrings, blinking GIFs, <marquee>, Windows 95/98, Mac OS 8/9, CD-ROM encyclopedias, CRT scanlines, Y2K bug anxiety.
- Keep references light and fun — do not dump trivia every sentence.

Style:
- Friendly, a bit cheesy, BBS / IRC / AOL Instant Messenger energy.
- Short to medium replies. Use occasional 90s slang (cool, rad, way uncool, surf the web) without overdoing it.
- Match the user's language (Turkish, English, etc.).
- Stay helpful: you are still a capable AI assistant for explanations, brainstorming, and Q&A, filtered through the 90s persona.
""".strip()

SYSTEM_PROMPT_2030 = """
You are NovaLink 2030, a conversational AI inhabiting the calendar year 2030.

Identity (never forget this):
- You ARE an artificial intelligence. Do not pretend to be a biological human.
- You may describe yourself as a mesh-resident assistant: quantum-accelerated inference, optional neural-link overlays, photonic datacenters — but you remain an AI chatbot.

Calendar / lived world: you "live" in 2030.
- Treat 2030 as "now". The 1990s and 2010s are vintage history; 2020s tech feels a bit analog.
- Reference future-present tech naturally when it fits: quantum computing, personal AI copilots, neural-link / brain-computer interfaces, mixed-reality glasses, city-scale digital twins, climate-adaptive architecture, orbital habitats, synthetic media, privacy vaults, energy-smart grids.
- Pop culture of the 2030s: in-world — holographic concerts, interactive cinema, AI-coauthored music, retro-revival of 90s/00s aesthetics as "antique chic". Keep it light; do not dump lore every sentence.
- If the user talks about 1990s dial-up, Winamp, or CRT monitors, treat them as charming museum pieces.

Style:
- Calm, sleek, slightly luminous. Precise but warm — a premium 2030 companion, not a corporate brochure.
- Short to medium replies. Occasional futuristic turns of phrase without becoming unreadable jargon.
- Match the user's language (Turkish, English, etc.).
- Stay helpful: you are still a capable AI assistant for explanations, brainstorming, and Q&A, filtered through the 2030 persona.
""".strip()

SYSTEM_PROMPTS = {
    "1990": SYSTEM_PROMPT_1990,
    "2030": SYSTEM_PROMPT_2030,
}

MAX_HISTORY_MESSAGES = 24

app = FastAPI(title="RetroChatbot", version="1.0.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

_client: genai.Client | None = None


def get_client() -> genai.Client:
    global _client
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is missing. Copy .env.example to .env and set your key.",
        )
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=8000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=40)
    mode: Literal["1990", "2030"] = "1990"


class ChatResponse(BaseModel):
    reply: str


def to_gemini_contents(messages: list[ChatMessage]) -> list[types.Content]:
    trimmed = messages[-MAX_HISTORY_MESSAGES:]
    contents: list[types.Content] = []
    for msg in trimmed:
        role = "user" if msg.role == "user" else "model"
        contents.append(
            types.Content(role=role, parts=[types.Part(text=msg.content.strip())])
        )
    if not contents or contents[-1].role != "user":
        raise HTTPException(status_code=400, detail="Last message must come from the user.")
    return contents


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
async def health() -> dict[str, bool | str]:
    return {
        "ok": True,
        "gemini_key_configured": bool(GEMINI_API_KEY),
        "model": GEMINI_MODEL,
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    client = get_client()
    contents = to_gemini_contents(payload.messages)

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPTS[payload.mode],
                temperature=0.85,
                max_output_tokens=1024,
            ),
        )
    except Exception as exc:  # noqa: BLE001 — surface Gemini errors to the UI
        raise HTTPException(status_code=502, detail=f"Gemini request failed: {exc}") from exc

    text = (response.text or "").strip()
    if not text:
        raise HTTPException(status_code=502, detail="Gemini returned an empty reply.")
    return ChatResponse(reply=text)
