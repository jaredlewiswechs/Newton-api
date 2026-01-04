/**
 * Newton Trace Engine - React Component
 *
 * A crystalline reasoning architecture that makes thought visible, verifiable, and true.
 *
 * @author Jared Lewis
 * @date January 4, 2026
 * @version 1.0.0
 *
 * Architecture: Anthropic Tracing Thoughts Inspired
 * Philosophy: Bill Atkinson Drawing Verification
 * Vision: Steve Jobs 1 == 1 Guarantee
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Cpu,
  Brain,
  Zap,
  Settings2,
  Layers,
  Sparkles,
  CheckCircle2,
  RefreshCcw,
  BookOpen,
  Activity,
  Code,
  AlertTriangle,
  Lock,
  Unlock,
} from 'lucide-react';

// ============================================================================
// Type Definitions
// ============================================================================

interface TraceStep {
  id: string;
  title: string;
  detail: string;
  type: 'system' | 'math' | 'lexical' | 'logic' | 'model' | 'success' | 'error';
  timestamp: number;
  fgRatio?: number;
}

interface TraceParams {
  entropyThreshold: number;
  consensusMargin: number;
  targetAge: number;
  verbDensity: number;
}

interface CrystallizedResult {
  thought_trace: string[];
  crystallized_result: string;
  lexical_logic: string;
}

interface TraceEngineState {
  input: string;
  isThinking: boolean;
  traceSteps: TraceStep[];
  crystallizedOutput: string | null;
  lexicalAnalysis: string | null;
  params: TraceParams;
  sessionId: string;
}

// ============================================================================
// Utility Functions
// ============================================================================

const generateId = (): string => {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

const generateSessionId = (): string => {
  return Math.floor(Math.random() * 10000).toString().padStart(4, '0');
};

/**
 * Exponential backoff retry mechanism for API calls
 */
const exponentialBackoff = async <T,>(
  fn: () => Promise<T>,
  retries: number = 5,
  delay: number = 1000
): Promise<T> => {
  for (let i = 0; i < retries; i++) {
    try {
      return await fn();
    } catch (err) {
      if (i === retries - 1) throw err;
      await new Promise((r) => setTimeout(r, delay * Math.pow(2, i)));
    }
  }
  throw new Error('Max retries exceeded');
};

// ============================================================================
// Sub-Components
// ============================================================================

interface TraceStepDisplayProps {
  step: TraceStep;
}

const TraceStepDisplay: React.FC<TraceStepDisplayProps> = ({ step }) => {
  const getIcon = () => {
    switch (step.type) {
      case 'system':
        return <Layers size={12} className="text-amber-500" />;
      case 'math':
        return <Code size={12} className="text-blue-500" />;
      case 'lexical':
        return <BookOpen size={12} className="text-emerald-500" />;
      case 'model':
        return <Brain size={12} className="text-purple-500" />;
      case 'success':
        return <CheckCircle2 size={12} className="text-emerald-600" />;
      case 'error':
        return <AlertTriangle size={12} className="text-red-500" />;
      default:
        return <Activity size={12} className="text-slate-500" />;
    }
  };

  const getContainerClass = () => {
    const base = 'text-xs leading-relaxed p-3 rounded-lg border';
    if (step.type === 'model') {
      return `${base} bg-purple-50/50 border-purple-100 text-slate-700 font-medium`;
    }
    if (step.type === 'success') {
      return `${base} bg-emerald-50/50 border-emerald-100 text-slate-700`;
    }
    if (step.type === 'error') {
      return `${base} bg-red-50/50 border-red-100 text-red-700`;
    }
    return `${base} bg-white border-slate-100 text-slate-500`;
  };

  return (
    <div className="animate-in fade-in slide-in-from-left-4 duration-500">
      <div className="flex items-center gap-2 mb-1.5">
        {getIcon()}
        <span
          className={`text-[10px] font-bold uppercase tracking-wider ${
            step.type === 'model' ? 'text-purple-600' : 'text-slate-500'
          }`}
        >
          {step.title}
        </span>
        {step.fgRatio !== undefined && (
          <span
            className={`ml-auto text-[9px] font-mono ${
              step.fgRatio < 0.9
                ? 'text-emerald-600'
                : step.fgRatio < 1.0
                ? 'text-amber-600'
                : 'text-red-600'
            }`}
          >
            f/g: {step.fgRatio.toFixed(2)}
          </span>
        )}
      </div>
      <div className={getContainerClass()}>{step.detail}</div>
    </div>
  );
};

interface CalibrationSliderProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  unit?: string;
  color: 'purple' | 'emerald';
  onChange: (value: number) => void;
}

const CalibrationSlider: React.FC<CalibrationSliderProps> = ({
  label,
  value,
  min,
  max,
  step,
  unit = '',
  color,
  onChange,
}) => {
  const displayValue =
    unit === '%' ? `${Math.round(value * 100)}%` : `${value}${unit}`;

  return (
    <div className="flex-1 space-y-4">
      <div className="flex justify-between items-center">
        <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">
          {label}
        </label>
        <span
          className={`text-xs font-mono font-bold ${
            color === 'purple' ? 'text-purple-600' : 'text-emerald-600'
          }`}
        >
          {displayValue}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className={`w-full h-1 bg-slate-200 rounded-lg appearance-none cursor-pointer ${
          color === 'purple' ? 'accent-purple-600' : 'accent-emerald-500'
        }`}
      />
    </div>
  );
};

// ============================================================================
// Main Component
// ============================================================================

const TraceEngine: React.FC = () => {
  // State
  const [state, setState] = useState<TraceEngineState>({
    input: '',
    isThinking: false,
    traceSteps: [],
    crystallizedOutput: null,
    lexicalAnalysis: null,
    params: {
      entropyThreshold: 0.65,
      consensusMargin: 0.85,
      targetAge: 12,
      verbDensity: 0.7,
    },
    sessionId: generateSessionId(),
  });

  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll trace panel
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [state.traceSteps]);

  // Add trace step
  const addTrace = useCallback(
    (
      title: string,
      detail: string,
      type: TraceStep['type'] = 'logic',
      fgRatio?: number
    ) => {
      const newStep: TraceStep = {
        id: generateId(),
        title,
        detail,
        type,
        timestamp: Date.now(),
        fgRatio,
      };
      setState((prev) => ({
        ...prev,
        traceSteps: [...prev.traceSteps, newStep],
      }));
    },
    []
  );

  // Update params
  const updateParams = useCallback((updates: Partial<TraceParams>) => {
    setState((prev) => ({
      ...prev,
      params: { ...prev.params, ...updates },
    }));
  }, []);

  // Reset trace
  const resetTrace = useCallback(() => {
    setState((prev) => ({
      ...prev,
      input: '',
      traceSteps: [],
      crystallizedOutput: null,
      lexicalAnalysis: null,
      sessionId: generateSessionId(),
    }));
  }, []);

  // Main crystallization handler
  const handleTraceCrystallize = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!state.input || state.isThinking) return;

    setState((prev) => ({
      ...prev,
      isThinking: true,
      traceSteps: [],
      crystallizedOutput: null,
      lexicalAnalysis: null,
    }));

    // Phase 1: Melt Layer
    addTrace(
      'Melt Layer Activated',
      'Stripping syntactic noise. Isolating semantic intent mass.',
      'system',
      0.42
    );
    await new Promise((r) => setTimeout(r, 800));

    // Phase 2: Entropy Calibration
    addTrace(
      'Entropy Calibration',
      `Threshold set to ${state.params.entropyThreshold}. Filtering noise as Creative State.`,
      'math',
      0.55
    );
    await new Promise((r) => setTimeout(r, 600));

    // Phase 3: Lexical Constraints
    addTrace(
      'Lexical Constraints Bound',
      `Targeting age ${state.params.targetAge}. Vocabulary ceiling: ~${(
        state.params.targetAge * 0.87
      ).toFixed(1)}k tokens.`,
      'lexical',
      0.63
    );
    await new Promise((r) => setTimeout(r, 700));

    // Phase 4: Consensus Protocol
    addTrace(
      'Consensus Protocol',
      'Alpha and Beta agents synchronizing on Truth Axis.',
      'logic',
      0.71
    );
    await new Promise((r) => setTimeout(r, 500));

    try {
      // Build system prompt
      const systemPrompt = `You are Newton, a crystalline reasoning engine mimicking a 'Tracing Thoughts' model.

Your goal is to provide a detailed 'hidden' thought process followed by a crystalline result.

LEXICAL CONSTRAINTS:
- Target Age: ${state.params.targetAge}
- Verb Density: ${state.params.verbDensity}
- Mechanical Clarity: High
- Entropy Threshold: ${state.params.entropyThreshold}

Format your response as JSON:
{
  "thought_trace": ["thought 1", "thought 2", "thought 3"],
  "crystallized_result": "Final Answer",
  "lexical_logic": "Explanation of word choices and reasoning path"
}`;

      // Simulate API call (replace with actual API integration)
      const result = await simulateAPICall(state.input, systemPrompt);

      // Inject model thoughts into trace
      for (const thought of result.thought_trace || []) {
        addTrace('Reasoning Node', thought, 'model', 0.78 + Math.random() * 0.15);
        await new Promise((r) => setTimeout(r, 500));
      }

      // Update state with results
      setState((prev) => ({
        ...prev,
        crystallizedOutput: result.crystallized_result,
        lexicalAnalysis: result.lexical_logic,
      }));

      addTrace(
        'Crystallization Complete',
        'Entropy zeroed. Signal locked. Verification: 1 == 1.',
        'success',
        1.0
      );
    } catch (error) {
      addTrace(
        'Trace Interrupt',
        'External entropy blocked crystallization. Retry with adjusted parameters.',
        'error',
        0.0
      );
    } finally {
      setState((prev) => ({ ...prev, isThinking: false }));
    }
  };

  // Simulated API call (placeholder for real integration)
  const simulateAPICall = async (
    input: string,
    _systemPrompt: string
  ): Promise<CrystallizedResult> => {
    await new Promise((r) => setTimeout(r, 1500));

    // Generate simulated response based on input
    return {
      thought_trace: [
        `Parsing input: "${input.substring(0, 50)}..."`,
        'Identifying constraint boundaries and semantic anchors.',
        'Cross-referencing with knowledge graph for verification.',
        'Applying lexical constraints for target audience.',
        'Synthesizing crystallized response from verified components.',
      ],
      crystallized_result: `The intent "${input}" has been processed through Newton's constraint verification engine. The resulting crystallized truth satisfies all specified constraints including entropy threshold (${
        state.params.entropyThreshold
      }), target age (${
        state.params.targetAge
      }), and verb density (${state.params.verbDensity.toFixed(1)}).`,
      lexical_logic: `Word choices optimized for age ${state.params.targetAge} comprehension. Verb density maintained at ${(
        state.params.verbDensity * 100
      ).toFixed(0)}% for mechanical clarity. All statements verified against constraint definitions.`,
    };
  };

  return (
    <div className="min-h-screen bg-[#FDFDFF] text-slate-900 font-sans">
      {/* Navigation Bar */}
      <nav className="border-b border-slate-200 px-8 py-5 flex items-center justify-between bg-white/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="flex items-center gap-4">
          <div className="w-8 h-8 bg-[#6D28D9] rounded flex items-center justify-center text-white shadow-lg shadow-purple-200">
            <Cpu size={18} />
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-tight text-slate-900">
              Newton v6.0
            </h1>
            <p className="text-[10px] text-purple-600 font-bold uppercase tracking-widest">
              Trace Architecture
            </p>
          </div>
        </div>
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2 px-3 py-1 bg-purple-50 rounded-full border border-purple-100">
            <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" />
            <span className="text-[10px] font-bold text-purple-700 uppercase">
              Live Trace Active
            </span>
          </div>
          <Settings2
            size={18}
            className="text-slate-400 cursor-pointer hover:text-slate-600 transition-colors"
          />
        </div>
      </nav>

      <main className="max-w-[1600px] mx-auto grid grid-cols-1 lg:grid-cols-12 min-h-[calc(100vh-80px)]">
        {/* Left Pane: Reasoning Trace */}
        <div className="lg:col-span-4 border-r border-slate-200 bg-[#F9FAFB] flex flex-col">
          <div className="p-6 border-b border-slate-200 bg-white flex items-center justify-between">
            <h2 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
              <Activity size={14} className="text-purple-500" /> Reasoning Trace
            </h2>
            <span className="text-[10px] font-mono text-slate-400">
              SNAP_ID: {state.sessionId}
            </span>
          </div>

          <div
            ref={scrollRef}
            className="flex-1 overflow-y-auto p-6 space-y-6"
          >
            {state.traceSteps.length === 0 && !state.isThinking && (
              <div className="h-full flex flex-col items-center justify-center text-center opacity-40 grayscale">
                <Brain size={48} className="text-slate-200 mb-4" />
                <p className="text-xs font-medium text-slate-400">
                  Inject intent to observe thought tracing
                </p>
                <p className="text-[10px] text-slate-300 mt-2">
                  The constraint is the instruction
                </p>
              </div>
            )}

            {state.traceSteps.map((step) => (
              <TraceStepDisplay key={step.id} step={step} />
            ))}

            {state.isThinking && (
              <div className="flex items-center gap-2 text-purple-500 animate-pulse mt-4">
                <RefreshCcw size={14} className="animate-spin" />
                <span className="text-[10px] font-bold uppercase tracking-widest">
                  Tracing...
                </span>
              </div>
            )}
          </div>

          <div className="p-6 bg-white border-t border-slate-200">
            <form onSubmit={handleTraceCrystallize} className="relative">
              <input
                value={state.input}
                onChange={(e) =>
                  setState((prev) => ({ ...prev, input: e.target.value }))
                }
                placeholder="Describe your intent..."
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/20 transition-all"
                disabled={state.isThinking}
              />
              <button
                type="submit"
                disabled={state.isThinking || !state.input}
                className="absolute right-2 top-1.5 p-2 text-purple-600 hover:bg-purple-50 rounded-lg transition-colors disabled:opacity-30"
              >
                <Zap size={18} />
              </button>
            </form>
          </div>
        </div>

        {/* Right Pane: Crystallization & Calibration */}
        <div className="lg:col-span-8 bg-white flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto">
            <div className="px-12 py-16 max-w-4xl mx-auto">
              {!state.crystallizedOutput && !state.isThinking ? (
                <div className="space-y-8 animate-in fade-in duration-1000">
                  <div className="space-y-2">
                    <h2 className="text-4xl font-light text-slate-900 tracking-tight">
                      Crystallizing Intent
                    </h2>
                    <p className="text-lg text-slate-500 font-light">
                      Newton's reasoning architecture allows for granular
                      observation of the latent space between{' '}
                      <span className="text-purple-600 font-medium italic">
                        accident
                      </span>{' '}
                      and{' '}
                      <span className="text-emerald-600 font-medium">
                        structure
                      </span>
                      .
                    </p>
                  </div>

                  <div className="grid grid-cols-3 gap-6">
                    <div className="p-6 bg-slate-50 rounded-2xl border border-slate-100">
                      <Sparkles size={20} className="text-purple-500 mb-3" />
                      <h3 className="text-xs font-bold uppercase mb-2">
                        Melt Phase
                      </h3>
                      <p className="text-[11px] text-slate-500 leading-relaxed">
                        Automatic removal of syntactic entropy and prepositional
                        noise.
                      </p>
                    </div>
                    <div className="p-6 bg-slate-50 rounded-2xl border border-slate-100">
                      <Layers size={20} className="text-emerald-500 mb-3" />
                      <h3 className="text-xs font-bold uppercase mb-2">
                        Trace Analysis
                      </h3>
                      <p className="text-[11px] text-slate-500 leading-relaxed">
                        Exposing internal chain-of-thought for lexical
                        verification.
                      </p>
                    </div>
                    <div className="p-6 bg-slate-50 rounded-2xl border border-slate-100">
                      <CheckCircle2 size={20} className="text-blue-500 mb-3" />
                      <h3 className="text-xs font-bold uppercase mb-2">
                        Snap Logic
                      </h3>
                      <p className="text-[11px] text-slate-500 leading-relaxed">
                        Deterministic crystallization once the signal hits 1 ==
                        1.
                      </p>
                    </div>
                  </div>

                  {/* Pioneer Attribution */}
                  <div className="pt-8 border-t border-slate-100">
                    <h4 className="text-[10px] font-bold text-slate-300 uppercase tracking-[0.2em] mb-4">
                      Standing on the Shoulders of Giants
                    </h4>
                    <div className="flex flex-wrap gap-3">
                      {[
                        'Engelbart',
                        'Sutherland',
                        'Atkinson',
                        'Jobs',
                        'Wozniak',
                        'Lovelace',
                        'Kay',
                      ].map((name) => (
                        <span
                          key={name}
                          className="px-3 py-1 bg-slate-50 rounded-full text-[10px] font-medium text-slate-400 border border-slate-100"
                        >
                          {name}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="space-y-12 animate-in fade-in zoom-in-95 duration-500">
                  <div className="space-y-4">
                    <div className="flex items-center gap-3">
                      <span className="px-3 py-1 bg-emerald-50 text-emerald-600 text-[10px] font-bold uppercase tracking-widest rounded-full border border-emerald-100">
                        Crystallized Result
                      </span>
                      {state.crystallizedOutput && (
                        <Lock size={14} className="text-emerald-500" />
                      )}
                    </div>
                    <h3 className="text-3xl font-medium text-slate-900 leading-tight">
                      {state.crystallizedOutput ||
                        'Newton is formulating the crystalline structure...'}
                    </h3>
                  </div>

                  {state.lexicalAnalysis && (
                    <div className="pt-8 border-t border-slate-100">
                      <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em] mb-4">
                        Lexical Mechanical Breakdown
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <p className="text-sm text-slate-600 leading-relaxed italic">
                          {state.lexicalAnalysis}
                        </p>
                        <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100 space-y-4">
                          <div className="flex justify-between items-center">
                            <span className="text-[10px] font-bold text-slate-400">
                              Target Lexicon
                            </span>
                            <span className="text-[10px] font-mono text-purple-600">
                              AGE_{state.params.targetAge}
                            </span>
                          </div>
                          <div className="w-full bg-slate-200 h-1 rounded-full overflow-hidden">
                            <div
                              className="bg-purple-500 h-full transition-all duration-500"
                              style={{
                                width: `${Math.min(
                                  (state.params.targetAge / 25) * 100,
                                  100
                                )}%`,
                              }}
                            />
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-[10px] font-bold text-slate-400">
                              Verb Density
                            </span>
                            <span className="text-[10px] font-mono text-emerald-600">
                              {Math.round(state.params.verbDensity * 100)}%
                            </span>
                          </div>
                          <div className="w-full bg-slate-200 h-1 rounded-full overflow-hidden">
                            <div
                              className="bg-emerald-500 h-full transition-all duration-500"
                              style={{
                                width: `${state.params.verbDensity * 100}%`,
                              }}
                            />
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-[10px] font-bold text-slate-400">
                              Entropy Threshold
                            </span>
                            <span className="text-[10px] font-mono text-blue-600">
                              {Math.round(state.params.entropyThreshold * 100)}%
                            </span>
                          </div>
                          <div className="w-full bg-slate-200 h-1 rounded-full overflow-hidden">
                            <div
                              className="bg-blue-500 h-full transition-all duration-500"
                              style={{
                                width: `${state.params.entropyThreshold * 100}%`,
                              }}
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Bottom Calibration Drawer */}
          <div className="bg-[#F9FAFB] border-t border-slate-200 p-8">
            <div className="max-w-4xl mx-auto flex flex-col md:flex-row gap-12 items-end">
              <CalibrationSlider
                label="Lexical Age Constraint"
                value={state.params.targetAge}
                min={5}
                max={25}
                step={1}
                unit=" Years"
                color="purple"
                onChange={(v) => updateParams({ targetAge: v })}
              />
              <CalibrationSlider
                label="Entropy Sensitivity"
                value={state.params.entropyThreshold}
                min={0}
                max={1}
                step={0.01}
                unit="%"
                color="emerald"
                onChange={(v) => updateParams({ entropyThreshold: v })}
              />
              <div className="w-full md:w-auto">
                <button
                  onClick={resetTrace}
                  className="px-6 py-2 bg-slate-900 rounded-lg text-white text-[10px] font-bold uppercase tracking-widest flex items-center gap-2 cursor-pointer hover:bg-slate-800 transition-colors"
                >
                  <RefreshCcw size={14} /> Reset Trace
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 text-center">
        <p className="text-[10px] font-bold text-slate-300 uppercase tracking-[0.3em]">
          Newton Trace Engine // Architecture: Anthropic Tracing Thoughts
          Inspired // Lab Session 2026
        </p>
        <p className="text-[9px] text-slate-200 mt-2">
          Atkinson | Jobs | Wozniak | Engelbart | Lovelace | Kay | Sutherland
        </p>
      </footer>
    </div>
  );
};

export default TraceEngine;
