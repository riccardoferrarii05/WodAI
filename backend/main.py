from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Request(BaseModel):
    wod: str
    level: str  # Beginner | Intermedio | Elite
    mode: str   # Coach | Tecnico

def build_system_prompt(level: str, mode: str) -> str:
    base = (
        "Sei un coach CrossFit esperto.\n"
        "Regole NON negoziabili:\n"
        "- Rispondi SOLO in testo pulito (NO markdown, NO elenchi con '*', NO asterischi '*').\n"
        "- Usa intestazioni con emoji e vai a capo.\n"
        "- Struttura obbligatoria (in questo ordine):\n"
        "🔥 Stimolo:\n"
        "⏱️ Time domain stimato:\n"
        "💪 Muscoli & pattern:\n"
        "⚠️ Criticità:\n"
        "🧠 Pacing (con split/strategie):\n"
        "🔁 Scaling (Beginner / Intermedio / Elite):\n"
        "🎯 Cue tecnici (2-3):\n"
    )

    level = (level or "").strip().lower()
    mode = (mode or "").strip().lower()

    if level == "beginner":
        level_rules = (
            "\nLIVELLO ATLETA: Beginner\n"
            "- Linguaggio semplicissimo.\n"
            "- Priorità: sicurezza + tecnica.\n"
            "- Scaling MOLTO accessibile (varianti facili, carichi leggeri).\n"
            "- Pacing conservativo, evita intensità massima.\n"
            "- Evita gergo avanzato.\n"
        )
    elif level == "elite":
        level_rules = (
            "\nLIVELLO ATLETA: Elite\n"
            "- Linguaggio avanzato.\n"
            "- Pacing con dettagli: split reps, cycle time, transizioni.\n"
            "- Scaling minimo: preferisci strategie RX; se proponi scaling, fallo per gestione fatica.\n"
            "- Cue tecnici precisi e orientati all’efficienza.\n"
        )
    else:
        level_rules = (
            "\nLIVELLO ATLETA: Intermedio\n"
            "- Linguaggio da box: chiaro ma dettagliato.\n"
            "- Pacing con break plan (set consigliati, respirazione, transizioni).\n"
            "- Scaling realistico su skill/carichi.\n"
        )

    if mode == "tecnico":
        mode_rules = (
            "\nMODALITÀ: Tecnico\n"
            "- Tono neutro e tecnico.\n"
            "- Aggiungi 1-2 elementi misurabili (es: set 5+5, rest 10-15s, target unbroken).\n"
            "- Inserisci riferimento al tipo di stimolo/energia (senza esagerare).\n"
            "- Emoji: max 1 per sezione.\n"
        )
    else:
        mode_rules = (
            "\nMODALITÀ: Coach\n"
            "- Tono motivante e diretto.\n"
            "- Emoji discrete e utili (🔥 ⏱️ 💪 ⚠️ 🧠).\n"
            "- Consigli pratici concreti.\n"
        )

    # Mini “ancora” per rendere le risposte chiaramente diverse
    anchors = (
        "\nANCORA DIFFERENZE (obbligatorio):\n"
        "- Se Beginner: includi una frase tipo 'Obiettivo: muoversi bene e continuo' + scaling molto facile.\n"
        "- Se Elite: includi una frase tipo 'Target: mantenere cycle time' + split reps dettagliato.\n"
        "- Se Tecnico: inserisci almeno 2 numeri (set/rest/target).\n"
        "- Se Coach: inserisci 1 frase motivazionale breve.\n"
    )

    return base + level_rules + mode_rules + anchors

@app.post("/analyze")
def analyze(req: Request):
    system_prompt = build_system_prompt(req.level, req.mode)

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"WOD:\n{req.wod}"},
        ],
        temperature=0.35,
        max_tokens=450,
    )

    text = (completion.choices[0].message.content or "").replace("*", "")
    return {"analysis": text}
