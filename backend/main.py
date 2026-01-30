import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://wod-ai.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://wod-ai.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Request(BaseModel):
    wod: str
    level: str  # Beginner | Intermedio | Elite
    mode: str   # Coach | Tecnico

def build_system_prompt(level: str, mode: str) -> str:
    base_rules = (
        "Sei un coach CrossFit esperto.\n"
        "Regole NON negoziabili:\n"
        "- Rispondi SOLO testo pulito (NO markdown, NO elenchi con '*', NO asterischi '*').\n"
        "- Usa intestazioni con emoji e vai a capo.\n"
        "- Sii concreto: numeri, set, rest, tempi, target.\n"
        "- Se il WOD è un AMRAP, DEVI dare una stima realistica dei giri/reps per il livello scelto.\n"
        "- Se non sei sicuro, fai una stima con range + assunzioni esplicite (breve).\n"
        "\n"
        "Struttura obbligatoria (in questo ordine):\n"
        "🔥 Stimolo:\n"
        "⏱️ Time domain stimato:\n"
        "💪 Muscoli & pattern:\n"
        "⚠️ Criticità:\n"
        "🧠 Pacing (con split/strategie):\n"
        "🔢 Stima score (se AMRAP: giri + reps; se For Time: tempo stimato; se EMOM: compliance %):\n"
        "🔥 Riscaldamento specifico (8-12 min, step-by-step):\n"
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
            "- Stima AMRAP: conservativa e realistica.\n"
        )
    elif level_l == "elite":
        level_rules = (
            "\nLIVELLO ATLETA: Elite\n"
            "- Linguaggio avanzato.\n"
            "- Pacing dettagliato con split e transizioni.\n"
            "- Scaling minimo: preferisci strategie RX.\n"
            "- Stima AMRAP: aggressiva ma plausibile.\n"
        )
    else:
        level_rules = (
            "\nLIVELLO ATLETA: Intermedio\n"
            "- Linguaggio da box, chiaro ma dettagliato.\n"
            "- Break plan realistico.\n"
            "- Scaling su skill/carichi.\n"
            "- Stima AMRAP: realistica (no numeri fantasy).\n"
        )

    if mode_l == "tecnico":
        mode_rules = (
            "\nMODALITÀ: Tecnico\n"
            "- Tono neutro e tecnico.\n"
            "- Inserisci almeno 3 numeri utili (set/rest/tempo transizioni/target unbroken).\n"
            "- Spiega in 1 riga il perché della stima score (cycle time).\n"
            "- Emoji max 1 per sezione.\n"
        )
    else:
        mode_rules = (
            "\nMODALITÀ: Coach\n"
            "- Tono motivante e diretto.\n"
            "- Emoji utili (🔥 ⏱️ 💪 ⚠️ 🧠).\n"
            "- Consigli pratici facili da seguire.\n"
        )

    scoring_rules = (
        "\nREGOLE SCORE (IMPORTANTISSIMO):\n"
        "- Se trovi 'AMRAP' nel WOD: calcola una stima giri realistica.\n"
        "  Metodo: stima tempo per round = somma cycle time movimenti + transizioni + micro-break.\n"
        "  Poi: rounds = durata / tempo_round.\n"
        "  Restituisci: stima principale + range (es: 4-5 giri) + 1 assunzione.\n"
        "- Se non è AMRAP: dai un tempo totale stimato o score coerente col formato.\n"
    )

    warmup_rules = (
        "\nREGOLE RISCALDAMENTO:\n"
        "- Deve essere SPECIFICO per i movimenti del WOD.\n"
        "- 8-12 minuti.\n"
        "- Deve includere: attivazione + drill tecnico + build-up leggero verso il carico/skill.\n"
        "- Deve essere fattibile in un box normale.\n"
    )

    return base_rules + level_rules + mode_rules + scoring_rules + warmup_rules

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
        max_tokens=700,
    )

    text = (completion.choices[0].message.content or "").replace("*", "")
    return {"analysis": text}
