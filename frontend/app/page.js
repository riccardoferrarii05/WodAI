"use client";
import { useEffect, useMemo, useRef, useState } from "react";

const API_URL = "https://wodai.onrender.com/analyze";

function clsx(...a) {
  return a.filter(Boolean).join(" ");
}

function Segmented({ value, onChange, options }) {
  const idx = options.findIndex((o) => o.value === value);
  return (
    <div className="relative rounded-2xl border border-white/10 bg-white/5 p-1">
      <div
        className="absolute top-1 bottom-1 rounded-xl bg-white/15 transition-all duration-300 ease-out"
        style={{
          left: `calc(${idx} * (100% / ${options.length}) + 4px)`,
          width: `calc(100% / ${options.length} - 8px)`,
        }}
      />
      <div
        className="relative grid"
        style={{ gridTemplateColumns: `repeat(${options.length}, minmax(0, 1fr))` }}
      >
        {options.map((o) => (
          <button
            key={o.value}
            onClick={() => onChange(o.value)}
            className={clsx(
              "h-10 rounded-xl text-[12px] transition", // ✅ SOLO QUESTO CAMBIA
              value === o.value ? "text-white" : "text-white/60 hover:text-white/80"
            )}
          >
            {o.label}
          </button>
        ))}
      </div>
    </div>
  );
}


export default function Page() {
  const [mounted, setMounted] = useState(false);

  const [wod, setWod] = useState(
`AMRAP 12'
10 thruster (40/30)
10 pull-up
20 DU`
  );

  const [level, setLevel] = useState("Intermedio");
  const [mode, setMode] = useState("Coach");

  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState("");
  const [typed, setTyped] = useState("");
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  const typingRef = useRef({ timer: null });

  useEffect(() => {
    const t = setTimeout(() => setMounted(true), 10);
    return () => clearTimeout(t);
  }, []);

  const canAnalyze = useMemo(() => !!wod.trim() && !loading, [wod, loading]);

  const onReset = () => {
    setWod("");
    setAnalysis("");
    setTyped("");
    setError("");
  };

  const onCopy = async () => {
    const text = typed || analysis;
    if (!text) return;
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 900);
  };

  const startTyping = (fullText) => {
    if (typingRef.current.timer) clearInterval(typingRef.current.timer);
    setTyped("");
    let i = 0;
    const speed = 8; // più basso = più veloce
    typingRef.current.timer = setInterval(() => {
      i += 2; // scrive a “chunk” (più smooth)
      setTyped(fullText.slice(0, i));
      if (i >= fullText.length) {
        clearInterval(typingRef.current.timer);
        typingRef.current.timer = null;
      }
    }, speed);
  };

  const onAnalyze = async () => {
    setLoading(true);
    setError("");
    setAnalysis("");
    setTyped("");

    try {
      const r = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ wod, level, mode }),
      });

      if (!r.ok) {
        const txt = await r.text().catch(() => "");
        throw new Error(`Backend error (${r.status}) ${txt}`);
      }

      const data = await r.json();
      const clean = (data.analysis || "").replace(/\*/g, "");
      setAnalysis(clean);
      startTyping(clean);
    } catch (e) {
      setError(e?.message || "Errore sconosciuto");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0B0B0F] text-white overflow-x-hidden">
      <style jsx global>{`
        @keyframes floatIn { from { opacity: 0; transform: translateY(10px);} to { opacity: 1; transform: translateY(0);} }
        @keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
        .anim-in { animation: floatIn .45s ease-out both; }
        .card { transition: transform .22s ease, border-color .22s ease, background-color .22s ease, box-shadow .22s ease; }
        .card:hover { transform: translateY(-4px); border-color: rgba(255,255,255,.18); background-color: rgba(255,255,255,.06); box-shadow: 0 25px 90px rgba(0,0,0,.45); }
        .btn { transition: transform .15s ease, opacity .2s ease, background-color .2s ease; }
        .btn:active { transform: scale(.98); }
        .shine {
          background: linear-gradient(90deg, rgba(255,255,255,.06) 0%, rgba(255,255,255,.14) 20%, rgba(255,255,255,.06) 40%, rgba(255,255,255,.06) 100%);
          background-size: 200% 100%;
          animation: shimmer 1.1s linear infinite;
        }
        .custom-scroll::-webkit-scrollbar { width: 10px; }
        .custom-scroll::-webkit-scrollbar-track { background: rgba(255,255,255,0.04); border-radius: 999px; }
        .custom-scroll::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.16); border-radius: 999px; }
        .custom-scroll::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.24); }
        .custom-scroll { scrollbar-width: thin; scrollbar-color: rgba(255,255,255,0.18) rgba(255,255,255,0.05); }
      `}</style>

      {/* background clean premium */}
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(ellipse_at_top,rgba(99,102,241,0.10),rgba(0,0,0,0)_55%)]" />
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(ellipse_at_bottom,rgba(0,0,0,0),rgba(0,0,0,0.55))] opacity-80" />

      <div className={clsx("mx-auto max-w-5xl px-6 py-10", mounted ? "anim-in" : "opacity-0")}>
        {/* top */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-400" />
            <span className="text-sm text-white/70 tracking-wide">WodAI</span>
          </div>

          <button
            onClick={onCopy}
            disabled={!analysis && !typed}
            className={clsx(
              "btn rounded-xl px-3 py-2 text-sm border",
              (analysis || typed)
                ? "border-white/10 bg-white/5 text-white/75 hover:bg-white/10"
                : "border-white/5 bg-transparent text-white/30 cursor-not-allowed"
            )}
          >
            {copied ? "Copiato ✅" : "Copia"}
          </button>
        </div>

        {/* title */}
        <div className="mt-8">
          <h1 className="text-3xl md:text-4xl font-semibold tracking-tight">
            Analizza il tuo <span className="text-white/60">WOD</span>
          </h1>
          <p className="mt-2 text-white/55 max-w-xl">
            Pacing, scaling, warm-up e stima score. Tutto coerente col tuo livello.
          </p>
        </div>

        {/* content */}
        <div className="mt-8 relative">
          <div className="pointer-events-none hidden lg:block absolute left-1/2 top-6 bottom-6 w-px -translate-x-1/2 bg-gradient-to-b from-transparent via-white/10 to-transparent" />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-10">
            {/* INPUT */}
            <div className="card rounded-2xl border border-white/10 bg-white/5">
              <div className="p-5 border-b border-white/10 flex items-center justify-between">
                <h2 className="text-sm font-semibold text-white/85">Input</h2>
                <span className="text-xs text-white/45">{wod.length} chars</span>
              </div>

              <div className="p-5 space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <div className="text-xs text-white/55 mb-2">Livello atleta</div>
                    <Segmented
                      value={level}
                      onChange={setLevel}
                      options={[
                        { label: "Beginner", value: "Beginner" },
                        { label: "Intermedio", value: "Intermedio" },
                        { label: "Elite", value: "Elite" },
                      ]}
                    />
                  </div>

                  <div>
                    <div className="text-xs text-white/55 mb-2">Stile</div>
                    <Segmented
                      value={mode}
                      onChange={setMode}
                      options={[
                        { label: "Coach", value: "Coach" },
                        { label: "Tecnico", value: "Tecnico" },
                      ]}
                    />
                  </div>
                </div>

                <div>
                  <label className="text-xs text-white/55">WOD</label>
                  <textarea
                    value={wod}
                    onChange={(e) => setWod(e.target.value)}
                    rows={12}
                    className="mt-2 w-full rounded-2xl border border-white/10 bg-black/10 px-4 py-3 text-sm leading-relaxed outline-none focus:ring-2 focus:ring-white/15 transition"
                    placeholder="Incolla qui il WOD…"
                  />
                </div>

                {error ? (
                  <div className="rounded-2xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">
                    {error}
                  </div>
                ) : null}
              </div>

              <div className="p-5 border-t border-white/10 flex items-center justify-between">
                <button
                  onClick={onReset}
                  className="btn rounded-xl border border-white/10 bg-transparent px-4 py-2 text-sm text-white/70 hover:bg-white/5"
                >
                  Reset
                </button>

                <button
                  onClick={onAnalyze}
                  disabled={!canAnalyze}
                  className={clsx(
                    "btn rounded-xl px-5 py-2 text-sm font-semibold",
                    !canAnalyze
                      ? "bg-white/10 text-white/40 cursor-not-allowed opacity-70"
                      : "bg-white text-black hover:bg-white/90"
                  )}
                >
                  {loading ? "Analizzo…" : "Analizza"}
                </button>
              </div>
            </div>

            {/* OUTPUT */}
            <div className="card rounded-2xl border border-white/10 bg-white/5">
              <div className="p-5 border-b border-white/10 flex items-center justify-between">
                <h2 className="text-sm font-semibold text-white/85">Output</h2>
                <span className="text-xs text-white/40">{typed ? `${typed.length}` : analysis ? `${analysis.length}` : ""}</span>
              </div>

              <div className="p-5">
                {!analysis && !loading ? (
                  <div className="rounded-2xl border border-white/10 bg-black/10 p-5 text-white/55">
                    Inserisci un WOD e premi <span className="text-white/80 font-semibold">Analizza</span>.
                  </div>
                ) : null}

                {loading ? (
                  <div className="rounded-2xl border border-white/10 bg-black/10 p-5">
                    <div className="flex items-center gap-3 text-white/70">
                      <div className="h-4 w-4 rounded-full border border-white/30 border-t-transparent animate-spin" />
                      Sto analizzando…
                    </div>
                    <div className="mt-4 space-y-2">
                      <div className="h-4 rounded-lg shine" />
                      <div className="h-4 rounded-lg shine w-11/12" />
                      <div className="h-4 rounded-lg shine w-9/12" />
                      <div className="h-4 rounded-lg shine w-10/12" />
                    </div>
                  </div>
                ) : null}

                {analysis ? (
                  <div className="rounded-2xl border border-white/10 bg-black/10 p-5 max-h-[72vh] overflow-y-auto custom-scroll">
                    <div className="whitespace-pre-wrap text-sm leading-relaxed font-sans text-white/85">
                      {typed || analysis}
                    </div>
                  </div>
                ) : null}
              </div>

              <div className="px-5 pb-5 flex items-center justify-between text-xs text-white/40">
                <span>{analysis ? "Pronto ✅" : ""}</span>
                <span>{analysis ? "Warm-up incluso 🔥" : ""}</span>
              </div>
            </div>
          </div>
        </div>

        <footer className="mt-10 text-xs text-white/35">
          © {new Date().getFullYear()} WodAI
        </footer>
      </div>
    </div>
  );
}
