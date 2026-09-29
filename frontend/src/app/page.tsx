"use client";

import { useState } from "react";

const originalIncident = {
  incident_id: "INC-004",
  service: "Payment API",
  severity: "SEV-2",
  description:
    "High HTTP 500 failure rate and latency spike observed in Payment API.",
  recent_changes: "Cache configuration change deployed 20 minutes prior to alert.",
  evidence: {
    http_500_errors: "79%",
    latency: "4.5 seconds",
    database_connections: "29%",
    cache_errors: "HIGH",
    recent_configuration_change: "YES",
  },
};

const learnedIncident = {
  incident_id: "INC-005",
  service: "Payment API",
  severity: "SEV-2",
  description:
    "A new Payment API outage shows elevated HTTP 500 errors and cache failures after a recent configuration change.",
  recent_changes: "Cache configuration change deployed 12 minutes prior to alert.",
  evidence: {
    http_500_errors: "68%",
    latency: "3.9 seconds",
    database_connections: "31%",
    cache_errors: "HIGH",
    recent_configuration_change: "YES",
  },
};

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  const [learning, setLearning] = useState(false);
  const [learned, setLearned] = useState(false);
  const [activeIncident, setActiveIncident] = useState(originalIncident);
  const [isLearnedScenario, setIsLearnedScenario] = useState(false);

  function loadIncident(nextIncident: typeof originalIncident, learnedScenario = false) {
    setActiveIncident(nextIncident);
    setIsLearnedScenario(learnedScenario);
    setResult(null);
    setError("");
    setLearned(false);
  }

  async function analyzeIncident() {
    setLoading(true);
    setError("");
    setResult(null);
    setLearned(false);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/incidents/analyze",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(activeIncident),
        }
      );

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(
        "Could not connect to the RecallOps backend. Make sure FastAPI is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  }

  async function learnFromIncident() {
    if (!result) return;

    setLearning(true);
    setError("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/incidents/learn",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            incident_id: activeIncident.incident_id,
            service: activeIncident.service,
            confirmed_root_cause:
              typeof result.diagnosis === "string"
                ? result.diagnosis
                : "Cache configuration regression",
            resolution: result.recommended_action,
            key_learnings: result.reasoning,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`Learning request failed: ${response.status}`);
      }

      setLearned(true);
    } catch (err) {
      setError(
        "Could not store the experience in Hindsight. Check the backend terminal."
      );
    } finally {
      setLearning(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <header className="border-b border-slate-800 bg-slate-950">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-8 py-5">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">RecallOps</h1>
            <p className="text-sm text-slate-400">
              AI Incident Commander • Learns from production experience
            </p>
          </div>

          <div className="flex items-center gap-3">
            <span className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-400">
              HINDSIGHT CONNECTED
            </span>
            <span className="rounded-full border border-blue-500/30 bg-blue-500/10 px-3 py-1 text-xs font-medium text-blue-400">
              GROQ AI
            </span>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-8 py-8">
        <section className="mb-6 rounded-xl border border-slate-800 bg-slate-900 p-5">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
                DEMO SCENARIOS
              </p>
              <p className="mt-1 text-sm text-slate-300">
                First teach Hindsight with INC-004, then test whether a new incident can recall that experience.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <button
                onClick={() => loadIncident(originalIncident, false)}
                className={!isLearnedScenario
                  ? "rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold"
                  : "rounded-lg border border-slate-700 bg-slate-950 px-4 py-2 text-sm font-semibold text-slate-300 hover:bg-slate-800"}
              >
                Original Incident
              </button>
              <button
                onClick={() => loadIncident(learnedIncident, true)}
                className={isLearnedScenario
                  ? "rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold"
                  : "rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-2 text-sm font-semibold text-emerald-300 hover:bg-emerald-500/20"}
              >
                Load Learned Incident
              </button>
            </div>
          </div>
        </section>

        {isLearnedScenario && (
          <div className="mb-6 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-5">
            <p className="text-sm font-medium uppercase tracking-wider text-emerald-400">
              LEARNING TEST
            </p>
            <p className="mt-2 text-sm leading-6 text-emerald-100">
              This is a new incident intentionally similar to the experience just retained. Investigate it to prove Hindsight can recall the learned experience.
            </p>
          </div>
        )}

        <section className="mb-6 rounded-xl border border-red-500/30 bg-slate-900 p-6">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-400">ACTIVE INCIDENT</p>
              <h2 className="mt-1 text-2xl font-bold">
                {activeIncident.incident_id} — {activeIncident.service}
              </h2>
            </div>

            <span className="rounded-lg bg-red-500/15 px-4 py-2 text-sm font-bold text-red-400">
              {activeIncident.severity}
            </span>
          </div>

          <p className="mb-5 text-slate-300">{activeIncident.description}</p>

          <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
            <Metric label="HTTP 500" value={activeIncident.evidence.http_500_errors} />
            <Metric label="Latency" value={activeIncident.evidence.latency} />
            <Metric
              label="DB Connections"
              value={activeIncident.evidence.database_connections}
            />
            <Metric label="Cache Errors" value={activeIncident.evidence.cache_errors} />
            <Metric
              label="Config Change"
              value={activeIncident.evidence.recent_configuration_change}
            />
          </div>

          <div className="mt-5 rounded-lg border border-slate-700 bg-slate-950 p-4">
            <p className="text-xs uppercase tracking-wider text-slate-500">
              Recent Change
            </p>
            <p className="mt-1 text-sm text-slate-300">
              {activeIncident.recent_changes}
            </p>
          </div>
        </section>

        <section className="mb-6">
          <button
            onClick={analyzeIncident}
            disabled={loading}
            className="w-full rounded-xl bg-blue-600 px-6 py-4 text-lg font-semibold transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading
              ? "Investigating with Hindsight..."
              : "Investigate Incident with Hindsight"}
          </button>
        </section>

        {error && (
          <div className="mb-6 rounded-xl border border-red-500/30 bg-red-500/10 p-5 text-red-300">
            {error}
          </div>
        )}

        {result && (
          <>
            {!isLearnedScenario && (
            <section className="mb-6 rounded-xl border border-blue-500/30 bg-blue-500/5 p-6">
              <div className="flex flex-col justify-between gap-5 md:flex-row md:items-center">
                <div>
                  <p className="text-sm font-medium uppercase tracking-wider text-blue-400">
                    Human Feedback
                  </p>
                  <h3 className="mt-2 text-xl font-semibold">
                    Confirm this experience
                  </h3>
                  <p className="mt-1 max-w-3xl text-sm text-slate-400">
                    Store this incident, diagnosis, resolution, and reasoning in
                    Hindsight so future incidents can learn from it.
                  </p>
                </div>

                <button
                  onClick={learnFromIncident}
                  disabled={learning || learned}
                  className="rounded-lg bg-emerald-600 px-5 py-3 font-semibold hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {learned
                    ? "✓ Experience Learned"
                    : learning
                    ? "Saving to Hindsight..."
                    : "Confirm & Learn"}
                </button>
              </div>

              {learned && (
                <div className="mt-4 rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-4 text-sm text-emerald-300">
                  Experience successfully retained in Hindsight. Future
                  investigations can recall this incident.
                </div>
              )}
            </section>
            )}

            <div className="grid gap-6 lg:grid-cols-2">
              <section className="rounded-xl border border-slate-800 bg-slate-900 p-6">
                <p className="text-sm font-medium uppercase tracking-wider text-slate-500">
                  AI Hypothesis
                </p>

                <h2 className="mt-3 text-2xl font-bold text-emerald-400">
                  {typeof result.diagnosis === "string"
                    ? result.diagnosis
                    : result.diagnosis?.likely_diagnosis ||
                      result.diagnosis?.diagnosis ||
                      "Diagnosis generated"}
                </h2>

                {result.confidence && (
                  <div className="mt-4">
                    <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-sm text-emerald-400">
                      Confidence: {result.confidence}
                    </span>
                  </div>
                )}

                {result.recommended_action && (
                  <div className="mt-6 rounded-lg border border-blue-500/20 bg-blue-500/5 p-4">
                    <p className="text-xs uppercase tracking-wider text-blue-400">
                      Recommended Immediate Action
                    </p>
                    <p className="mt-2 text-slate-200">
                      {result.recommended_action}
                    </p>
                  </div>
                )}

                {result.uncertainty && (
                  <div className="mt-4 rounded-lg border border-amber-500/20 bg-amber-500/5 p-4">
                    <p className="text-xs uppercase tracking-wider text-amber-400">
                      Uncertainty
                    </p>
                    <p className="mt-2 text-sm text-slate-300">
                      {result.uncertainty}
                    </p>
                  </div>
                )}
              </section>

              <section className="rounded-xl border border-slate-800 bg-slate-900 p-6">
                <p className="text-sm font-medium uppercase tracking-wider text-slate-500">
                  Comparative Reasoning
                </p>
                <p className="mt-4 whitespace-pre-wrap text-sm leading-6 text-slate-300">
                  {result.reasoning || "Reasoning returned by the AI agent."}
                </p>
              </section>

              <section className="rounded-xl border border-slate-800 bg-slate-900 p-6">
                <p className="text-sm font-medium uppercase tracking-wider text-slate-500">
                  Hindsight Memories — Similarities
                </p>

                <div className="mt-4 space-y-3">
                  {Array.isArray(result.similarities) ? (
                    result.similarities.map((item: string, index: number) => (
                      <div
                        key={index}
                        className="rounded-lg border border-emerald-500/20 bg-emerald-500/5 p-3 text-sm text-slate-300"
                      >
                        + {item}
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-slate-400">
                      {result.similarities || "Historical similarities found."}
                    </p>
                  )}
                </div>
              </section>

              <section className="rounded-xl border border-slate-800 bg-slate-900 p-6">
                <p className="text-sm font-medium uppercase tracking-wider text-slate-500">
                  Contradictions Detected
                </p>

                <div className="mt-4 space-y-3">
                  {Array.isArray(result.contradictions) ? (
                    result.contradictions.map(
                      (item: string, index: number) => (
                        <div
                          key={index}
                          className="rounded-lg border border-amber-500/20 bg-amber-500/5 p-3 text-sm text-slate-300"
                        >
                          − {item}
                        </div>
                      )
                    )
                  ) : (
                    <p className="text-sm text-slate-400">
                      {result.contradictions ||
                        "No major contradictions returned."}
                    </p>
                  )}
                </div>
              </section>

              <section className="rounded-xl border border-slate-800 bg-slate-900 p-6 lg:col-span-2">
                <p className="text-sm font-medium uppercase tracking-wider text-slate-500">
                  Recalled Historical Memories
                </p>

                <div className="mt-4 grid gap-3 md:grid-cols-2">
                  {Array.isArray(result.recalled_memories) &&
                  result.recalled_memories.length > 0 ? (
                    result.recalled_memories.map(
                      (memory: string, index: number) => (
                        <div
                          key={index}
                          className="rounded-lg border border-slate-700 bg-slate-950 p-4 text-sm leading-6 text-slate-300"
                        >
                          {memory}
                        </div>
                      )
                    )
                  ) : (
                    <p className="text-sm text-slate-400">
                      Historical memories were used during reasoning.
                    </p>
                  )}
                </div>
              </section>
            </div>
          </>
        )}

        <section className="mt-6 rounded-xl border border-slate-800 bg-slate-900 p-6">
          <p className="text-sm font-medium uppercase tracking-wider text-slate-500">
            RecallOps Learning Loop
          </p>

          <div className="mt-5 grid gap-3 md:grid-cols-5">
            {[
              ["01", "Current Incident"],
              ["02", "Hindsight Recall"],
              ["03", "Comparative Reasoning"],
              ["04", "Human Feedback"],
              ["05", "Experience Retained"],
            ].map(([number, label]) => (
              <div
                key={number}
                className="rounded-lg border border-slate-700 bg-slate-950 p-4"
              >
                <div className="text-xs font-bold text-blue-400">{number}</div>
                <div className="mt-2 text-sm font-medium">{label}</div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}

function Metric({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
      <p className="text-xs uppercase tracking-wider text-slate-500">{label}</p>
      <p className="mt-2 text-xl font-bold">{value}</p>
    </div>
  );
}
