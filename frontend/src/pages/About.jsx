import {
  Brain,
  Database,
  MapPinned,
  ShieldCheck,
  BarChart3,
  Server,
  Activity,
  Target,
} from "lucide-react";

export default function About() {
  return (
    <div className="space-y-8">

      {/* Header */}

      <section className="bg-[#111827] border border-slate-800 rounded-3xl p-8">
        <h1 className="text-4xl font-bold text-sky-400">
          About The Project
        </h1>

        <p className="text-slate-400 mt-4 max-w-5xl">
          Bengaluru Parking Hotspot Intelligence is an AI-powered
          analytics platform designed to forecast illegal parking
          hotspots, estimate parking-induced congestion risk,
          prioritize patrol deployment, and support data-driven
          enforcement planning using machine learning and
          spatial intelligence.
        </p>
      </section>

      {/* Project Overview */}

      <section className="grid md:grid-cols-2 gap-6">

        <div className="bg-[#111827] border border-slate-800 rounded-3xl p-6">
          <div className="flex items-center gap-3 mb-4">
            <Brain className="text-sky-400" />
            <h2 className="text-xl font-semibold text-white">
              Problem Statement
            </h2>
          </div>

          <p className="text-slate-400">
            Illegal parking contributes significantly to urban
            congestion, emergency response delays, reduced road
            capacity, and traffic bottlenecks. Traditional
            enforcement strategies often rely on historical
            knowledge and manual monitoring, making resource
            allocation inefficient.
          </p>
        </div>

        <div className="bg-[#111827] border border-slate-800 rounded-3xl p-6">
          <div className="flex items-center gap-3 mb-4">
            <Target className="text-green-400" />
            <h2 className="text-xl font-semibold text-white">
              Project Goal
            </h2>
          </div>

          <p className="text-slate-400">
            Forecast future hotspot locations, identify
            high-risk congestion zones, recommend optimal
            patrol deployment strategies, and provide
            explainable insights for city planners and
            law enforcement agencies.
          </p>
        </div>

      </section>

      {/* Data Pipeline */}

      <section className="bg-[#111827] border border-slate-800 rounded-3xl p-6">

        <div className="flex items-center gap-3 mb-4">
          <Database className="text-yellow-400" />
          <h2 className="text-2xl font-semibold text-white">
            Data Pipeline
          </h2>
        </div>

        <ul className="space-y-3 text-slate-400">
          <li>
            • Bengaluru traffic and parking violation records
          </li>

          <li>
            • Spatial grid-cell generation and hotspot mapping
          </li>

          <li>
            • Historical trend extraction and aggregation
          </li>

          <li>
            • Station-level and junction-level analytics
          </li>

          <li>
            • Risk labeling and hotspot stability analysis
          </li>
        </ul>

      </section>

      {/* ML Pipeline */}

      <section className="bg-[#111827] border border-slate-800 rounded-3xl p-6">

        <div className="flex items-center gap-3 mb-4">
          <BarChart3 className="text-purple-400" />
          <h2 className="text-2xl font-semibold text-white">
            Machine Learning Pipeline
          </h2>
        </div>

        <div className="space-y-3 text-slate-400">

          <p>
            • LightGBM forecasting model for hotspot prediction
          </p>

          <p>
            • Rolling Mean baseline comparison
          </p>

          <p>
            • Lag-1 forecasting benchmark
          </p>

          <p>
            • Feature importance and explainability analysis
          </p>

          <p>
            • Ensemble evaluation using Recall@20 and Recall@50
          </p>

        </div>

      </section>

      {/* Risk Engine */}

      <section className="grid md:grid-cols-2 gap-6">

        <div className="bg-[#111827] border border-slate-800 rounded-3xl p-6">

          <div className="flex items-center gap-3 mb-4">
            <Activity className="text-red-400" />
            <h2 className="text-xl font-semibold text-white">
              Risk Scoring Engine
            </h2>
          </div>

          <p className="text-slate-400">
            Every hotspot receives a congestion-risk score
            based on forecast intensity, recurrence,
            stability, trend behaviour, and operational
            impact indicators.
          </p>

        </div>

        <div className="bg-[#111827] border border-slate-800 rounded-3xl p-6">

          <div className="flex items-center gap-3 mb-4">
            <ShieldCheck className="text-green-400" />
            <h2 className="text-xl font-semibold text-white">
              Patrol Recommendation Engine
            </h2>
          </div>

          <p className="text-slate-400">
            Patrol deployment priorities are generated
            using a composite scoring strategy that
            combines forecasted violations, congestion
            risk, hotspot recurrence, and stability
            patterns.
          </p>

        </div>

      </section>

      {/* Architecture */}

      <section className="bg-[#111827] border border-slate-800 rounded-3xl p-6">

        <div className="flex items-center gap-3 mb-4">
          <Server className="text-cyan-400" />
          <h2 className="text-2xl font-semibold text-white">
            System Architecture
          </h2>
        </div>

        <div className="grid md:grid-cols-3 gap-4 mt-6">

          <div className="bg-[#0f172a] rounded-2xl p-4 border border-slate-800">
            <h3 className="text-sky-400 font-semibold">
              Frontend
            </h3>

            <p className="text-slate-400 mt-2">
              React.js + Vite + Tailwind CSS
            </p>
          </div>

          <div className="bg-[#0f172a] rounded-2xl p-4 border border-slate-800">
            <h3 className="text-sky-400 font-semibold">
              Backend
            </h3>

            <p className="text-slate-400 mt-2">
              FastAPI + Python
            </p>
          </div>

          <div className="bg-[#0f172a] rounded-2xl p-4 border border-slate-800">
            <h3 className="text-sky-400 font-semibold">
              ML Layer
            </h3>

            <p className="text-slate-400 mt-2">
              LightGBM + Spatial Analytics
            </p>
          </div>

        </div>

      </section>

      {/* Future Scope */}

      <section className="bg-[#111827] border border-slate-800 rounded-3xl p-6">

        <div className="flex items-center gap-3 mb-4">
          <MapPinned className="text-orange-400" />
          <h2 className="text-2xl font-semibold text-white">
            Future Enhancements
          </h2>
        </div>

        <ul className="space-y-3 text-slate-400">
          <li>
            • Real-time traffic integration
          </li>

          <li>
            • Dynamic patrol route optimization
          </li>

          <li>
            • GIS heatmaps and clustering
          </li>

          <li>
            • Live violation ingestion pipelines
          </li>

          <li>
            • Multi-city deployment support
          </li>

          <li>
            • Automated enforcement scheduling
          </li>
        </ul>

      </section>

    </div>
  );
}