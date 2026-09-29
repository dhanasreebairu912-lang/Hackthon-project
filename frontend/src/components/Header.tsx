"use client";

import React from "react";
import { ShieldAlert, Cpu, Database, Activity } from "lucide-react";
import { HealthStatus } from "../types/incident";

interface HeaderProps {
  health: HealthStatus | null;
  loading: boolean;
}

export const Header: React.FC<HeaderProps> = ({ health, loading }) => {
  const isHindsightOnline = health ? health.hindsight_connected : true;
  const isGroqOnline = health ? health.groq_configured : true;

  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
        {/* Brand / Logo */}
        <div className="flex items-center space-x-3.5">
          <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 p-0.5 shadow-lg shadow-indigo-500/20">
            <div className="h-full w-full bg-slate-950 rounded-[7px] flex items-center justify-center">
              <ShieldAlert className="h-5 w-5 text-indigo-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-wider text-white uppercase font-mono">
                Recall<span className="text-indigo-400">Ops</span>
              </h1>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded border border-indigo-500/30 bg-indigo-500/10 text-indigo-300">
                SRE INCIDENT COMMANDER
              </span>
            </div>
            <p className="text-xs text-slate-400 tracking-wide">
              Incident response that learns from experience using Vectorize Hindsight
            </p>
          </div>
        </div>

        {/* Live System Status Indicators */}
        <div className="flex items-center gap-3 text-xs font-mono">
          {/* Hindsight Status */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-slate-800 bg-slate-900/90 shadow-sm">
            <span className="relative flex h-2 w-2">
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${isHindsightOnline ? "bg-emerald-400 opacity-75" : "bg-rose-400 opacity-75"}`}></span>
              <span className={`relative inline-flex rounded-full h-2 w-2 ${isHindsightOnline ? "bg-emerald-500" : "bg-rose-500"}`}></span>
            </span>
            <Database className="h-3.5 w-3.5 text-slate-400" />
            <span className="font-semibold text-slate-300">HINDSIGHT MEMORY</span>
            <span className={`text-[10px] font-bold ${isHindsightOnline ? "text-emerald-400" : "text-rose-400"}`}>
              {isHindsightOnline ? "ONLINE" : "OFFLINE"}
            </span>
          </div>

          {/* AI Reasoning Status */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-slate-800 bg-slate-900/90 shadow-sm">
            <span className="relative flex h-2 w-2">
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${isGroqOnline ? "bg-cyan-400 opacity-75" : "bg-amber-400 opacity-75"}`}></span>
              <span className={`relative inline-flex rounded-full h-2 w-2 ${isGroqOnline ? "bg-cyan-500" : "bg-amber-500"}`}></span>
            </span>
            <Cpu className="h-3.5 w-3.5 text-slate-400" />
            <span className="font-semibold text-slate-300">AI REASONING</span>
            <span className={`text-[10px] font-bold ${isGroqOnline ? "text-cyan-400" : "text-amber-400"}`}>
              {isGroqOnline ? "ONLINE" : "OFFLINE"}
            </span>
            {health?.active_groq_model && (
              <span className="text-[10px] text-slate-500 hidden sm:inline">
                ({health.active_groq_model})
              </span>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
