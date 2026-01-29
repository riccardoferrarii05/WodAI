import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# CORS: metti qui TUTTI gli origin permessi (senza slash finale)
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://wod-ai.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Request(BaseModel):
    wod: str
    level: str
    mode: str

def build_system_prompt(level: str, mode: str) -> str:
    base = (
        "Sei un coach CrossFit esperto.\n"
        "Regole NON negoziabili:\n"
        "- Rispondi SOLO testo pulito (NO markdown, NO elenchi con '*', NO asterischi '*').\n"
        "- Usa intestazioni con emoji e vai a capo.\n"
        "Struttura obbligatoria (in questo ordine):\n"
        "🔥 Stimolo:\n"
        "⏱️ Time domain stimato:\n"
        "💪 Muscoli & pattern:\n"
        "⚠️ Criticità:\n"
        "🧠 Pacing (con split/strategie):\n"
        "🔁 Scaling (Beginner / Intermedio / Elite):\n"
        "🎯 Cue tecnici (2-3):\n"
    )

    level_l = (level or "").strip().lower()
    mode_l = (mode or "").strip().lower()

    if level_l == "beginner":
        level_rules = (
            "\nLIVELLO ATLETA: Beginner\n"
            "- Linguaggio semplicissimo.\n"
            "- Priorità: sicurezza + tecnica.\n"
            "- Scaling MOLTO accessibile.\n"
            "- Pacing conservativo.\n"
        )
    elif level_l == "elite":
        level_rules = (
            "\nLIVELLO ATLETA: Elite\n"
            "- Linguaggio avanzato.\n"
            "- Pacing dettagliato con split e transizioni.\n"
            "- Scaling minimo: preferisci strategie RX.\n"
        )
    else:
        level_rules = (
            "\nLIVELLO ATLETA: Intermedio\n"
            "- Linguaggio da box, chiaro ma dettagliato.\n"
            "- Break plan realistico.\n"
            "- Scaling su skill/carichi.\n"
        )

    if mode_l == "tecnico":
        mode_rules = (
            "\nMODALITÀ: Tecnico\n"
            "- Tono neutro e tecnico.\n"
            "- Inserisci almeno 2 numeri (set/rest/target).\n"
            "- Emoji max 1 per sezione.\n"
        )
    else:
        mode_rules = (
            "\nMODALITÀ: Coach\n"
            "- Tono motivante e diretto.\n"
            "- Emoji utili (🔥 ⏱️ 💪 ⚠️ 🧠).\n"
        )

    anchors = (
        "\nANCORA DIFFERENZE (obbligatorio):\n"
        "- Beginner: includi 'Obiettivo: muoversi bene e continuo'.\n"
        "- Elite: includi 'Target: mantenere cycle time' + split reps.\n"
        "- Tecnico: almeno 2 numeri.\n"
        "- Coach: 1 frase motivazionale breve.\n"
    )

    return base + level_rules + mode_rules + anchors

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/analyze")
def analyze(req: Request):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": build_system_prompt(req.level, req.mode)},
            {"role": "user", "content": f"WOD:\n{req.wod}"},
        ],
        temperature=0.35,
        max_tokens=450,
    )

    text = (completion.choices[0].message.content or "").replace("*", "")
    return {"analysis": text}
