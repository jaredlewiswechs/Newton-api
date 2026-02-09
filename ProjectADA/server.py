#!/usr/bin/env python3
"""
ProjectADA - Synthesized System of Systems Agent
═══════════════════════════════════════════════════
Wires ALL intelligence components into a single cohesive surface:

  1.  Newton Agent        - Full 10-step verification pipeline
  2.  Logic Engine        - Verified Turing-complete computation
  3.  TI Calculator       - TI-84 expression parsing
  4.  Knowledge Base      - CIA Factbook, periodic table, verified facts
  5.  Knowledge Mesh      - Multi-source cross-referenced data
  6.  Semantic Resolver   - Datamuse semantic field resolution
  7.  Grounding Engine    - External claim verification
  8.  Ada Sentinel        - Drift / anomaly detection
  9.  Meta Newton         - Self-verifying verifier
  10. Identity            - Newton's self-knowledge
  11. Kinematic Linguistics - Language as Bezier trajectories
  12. Trajectory Composer  - Real-time writing feedback
  13. realTinyTalk        - Verified programming language eval
  14. Adanpedia           - Witness example retrieval

Served locally on port 5050.
"""

import sys
import os
import json
import time
import uuid
import traceback
from pathlib import Path
from datetime import datetime

# Add parent to path so we can import adan, core, realTinyTalk
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, request, jsonify, send_from_directory, render_template

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'projectada-dev')


# ═══════════════════════════════════════════════════════════════
# LAZY-LOADED COMPONENTS  (all 14 subsystems)
# ═══════════════════════════════════════════════════════════════

_components = {}  # name -> instance


def _load(name, loader):
    """Lazy-load a component with caching and error isolation."""
    if name not in _components:
        try:
            _components[name] = loader()
        except Exception as e:
            _components[name] = None
            print(f"[ProjectADA] {name} failed to load: {e}")
    return _components.get(name)


# 1. Newton Agent
def get_agent():
    def _init():
        from adan.agent import NewtonAgent, AgentConfig
        return NewtonAgent(config=AgentConfig(
            enable_grounding=True,
            require_official_sources=False,
            grounding_threshold=5.0,
        ))
    return _load('agent', _init)


# 2. Logic Engine
def get_logic_engine():
    def _init():
        from core.logic import LogicEngine, ExecutionBounds
        return LogicEngine(ExecutionBounds(timeout_seconds=5.0, max_operations=10000))
    return _load('logic_engine', _init)


# 3. TI Calculator
def get_ti_calculator():
    def _init():
        from adan.ti_calculator import TICalculatorEngine
        return TICalculatorEngine()
    return _load('ti_calculator', _init)


# 4. Knowledge Base
def get_knowledge_base():
    def _init():
        from adan.knowledge_base import get_knowledge_base as _get_kb
        return _get_kb()
    return _load('knowledge_base', _init)


# 5. Knowledge Mesh
def get_knowledge_mesh():
    def _init():
        from adan.knowledge_sources import get_knowledge_mesh
        return get_knowledge_mesh()
    return _load('knowledge_mesh', _init)


# 6. Semantic Resolver
def get_semantic_resolver():
    def _init():
        from adan.semantic_resolver import SemanticResolver
        return SemanticResolver()
    return _load('semantic_resolver', _init)


# 7. Grounding Engine
def get_grounding_engine():
    def _init():
        from adan.grounding_enhanced import EnhancedGroundingEngine
        return EnhancedGroundingEngine()
    return _load('grounding_engine', _init)


# 8. Ada Sentinel
def get_ada_sentinel():
    def _init():
        from adan.ada import get_ada
        return get_ada()
    return _load('ada_sentinel', _init)


# 9. Meta Newton
def get_meta():
    def _init():
        from adan.meta_newton import get_meta_newton
        return get_meta_newton()
    return _load('meta_newton', _init)


# 10. Identity
def get_identity():
    def _init():
        from adan.identity import get_identity
        return get_identity()
    return _load('identity', _init)


# 11. Kinematic Linguistics
def get_analyzer():
    def _init():
        from adan.kinematic_linguistics import get_kinematic_analyzer
        return get_kinematic_analyzer()
    return _load('kinematic_linguistics', _init)


# 12. Trajectory Verifier + Composer
def get_verifier():
    def _init():
        from adan.trajectory_verifier import get_trajectory_verifier
        return get_trajectory_verifier()
    return _load('trajectory_verifier', _init)


def get_composer():
    def _init():
        from adan.trajectory_verifier import get_trajectory_composer
        return get_trajectory_composer()
    return _load('trajectory_composer', _init)


# 13. realTinyTalk
def get_tinytalk():
    def _init():
        from realTinyTalk import TinyTalkKernel, ExecutionBounds as TTBounds
        return TinyTalkKernel(TTBounds(max_iterations=5000, timeout_seconds=5.0))
    return _load('tinytalk', _init)


# 14. Adanpedia
def get_adanpedia():
    def _init():
        from core.adanpedia import fetch_witness_examples
        return fetch_witness_examples
    return _load('adanpedia', _init)


# ═══════════════════════════════════════════════════════════════
# IN-MEMORY CHAT STORAGE
# ═══════════════════════════════════════════════════════════════

chats = {}


def _now():
    return datetime.now().isoformat()


def _chat_summary(chat):
    msgs = chat['messages']
    return {
        'id': chat['id'],
        'title': chat['title'],
        'preview': msgs[-1]['content'][:80] if msgs else '',
        'message_count': len(msgs),
        'created': chat['created'],
        'updated': chat['updated'],
    }


# ═══════════════════════════════════════════════════════════════
# PAGES
# ═══════════════════════════════════════════════════════════════

@app.route('/')
def index():
    return render_template('index.html')


# ═══════════════════════════════════════════════════════════════
# CHAT CRUD
# ═══════════════════════════════════════════════════════════════

@app.route('/api/chats', methods=['GET'])
def list_chats():
    sorted_chats = sorted(chats.values(), key=lambda c: c['updated'], reverse=True)
    return jsonify([_chat_summary(c) for c in sorted_chats])


@app.route('/api/chats', methods=['POST'])
def create_chat():
    cid = str(uuid.uuid4())[:8]
    chat = {
        'id': cid,
        'title': 'New Conversation',
        'messages': [],
        'created': _now(),
        'updated': _now(),
    }
    chats[cid] = chat
    return jsonify(_chat_summary(chat))


@app.route('/api/chats/<cid>', methods=['GET'])
def get_chat(cid):
    chat = chats.get(cid)
    if not chat:
        return jsonify({'error': 'not found'}), 404
    return jsonify(chat)


@app.route('/api/chats/<cid>', methods=['DELETE'])
def delete_chat(cid):
    if cid in chats:
        del chats[cid]
    return jsonify({'deleted': cid})


# ═══════════════════════════════════════════════════════════════
# CORE: SEND MESSAGE  (full synthesized pipeline)
# ═══════════════════════════════════════════════════════════════

@app.route('/api/chats/<cid>/message', methods=['POST'])
def send_message(cid):
    chat = chats.get(cid)
    if not chat:
        return jsonify({'error': 'chat not found'}), 404

    data = request.get_json() or {}
    user_text = data.get('message', '').strip()
    if not user_text:
        return jsonify({'error': 'empty message'}), 400

    t0 = time.time()
    pipeline_trace = []  # Track which systems fired

    # ── Step 1: Ada Sentinel pre-scan ──
    ada_whisper = None
    try:
        ada = get_ada_sentinel()
        if ada:
            whisper = ada.sense(user_text)
            if whisper:
                ada_whisper = whisper.to_dict()
                pipeline_trace.append('ada_sentinel:sense')
    except Exception:
        pass

    # ── Step 2: Trajectory verification of input ──
    trajectory_info = None
    try:
        verifier = get_verifier()
        if verifier:
            tv = verifier.verify(user_text)
            trajectory_info = tv.to_dict()
            pipeline_trace.append('trajectory_verifier')
    except Exception:
        pass

    # ── Step 3: Process through Newton Agent (full pipeline) ──
    agent_response = None
    response_source = 'agent'
    try:
        agent = get_agent()
        if agent:
            resp = agent.process(user_text)
            agent_response = resp.to_dict()
            # Detect which subsystem inside the agent actually answered
            content = agent_response.get('content', '')
            if 'Logic Engine' in content or 'Computed by' in content:
                response_source = 'ti_calculator+logic_engine'
            elif 'Source: CIA' in content or 'Source: NIST' in content:
                response_source = 'knowledge_base'
            elif 'Source:' in content and any(k in content for k in ['planet', 'USGS', 'NASA']):
                response_source = 'knowledge_mesh'
            elif agent_response.get('action') == 'refuse':
                response_source = 'safety_constraints'
            elif 'I am ' in content and ('Newton' in content or 'verification' in content):
                response_source = 'identity'
            pipeline_trace.append(f'newton_agent:{response_source}')
    except Exception as e:
        agent_response = {
            'content': f"Processing issue: {str(e)}",
            'verified': False,
            'constraints': {'passed': [], 'failed': []},
            'grounding': {'results': [], 'unverified_claims': []},
            'meta': {'timestamp': int(time.time()), 'processing_time_ms': 0, 'turn_hash': ''},
        }
        pipeline_trace.append('newton_agent:error')

    # ── Step 4: Kinematic linguistic analysis ──
    kinematic_info = None
    try:
        analyzer = get_analyzer()
        if analyzer:
            kinematic_info = analyzer.analyze_sentence(user_text)
            pipeline_trace.append('kinematic_linguistics')
    except Exception:
        pass

    # ── Step 5: Meta Newton self-verification ──
    meta_verification = None
    try:
        meta = get_meta()
        if meta:
            elapsed_ms = int((time.time() - t0) * 1000)
            ctx = {
                'iterations': 1,
                'max_iterations': 100,
                'elapsed_ms': elapsed_ms,
                'max_time_ms': 30000,
                'meta_depth': 0,
            }
            mv = meta.verify(ctx)
            meta_verification = mv.to_dict()
            pipeline_trace.append('meta_newton')
    except Exception:
        pass

    # ── Step 6: Ada Sentinel post-watch ──
    ada_watch = None
    try:
        ada = get_ada_sentinel()
        if ada:
            content = agent_response.get('content', '') if isinstance(agent_response, dict) else ''
            verified = agent_response.get('verified', False) if isinstance(agent_response, dict) else False
            watch = ada.watch_response(user_text, content, verified)
            if watch:
                ada_watch = watch.to_dict()
                pipeline_trace.append('ada_sentinel:watch')
    except Exception:
        pass

    elapsed = int((time.time() - t0) * 1000)

    # Store user message
    user_msg = {
        'role': 'user',
        'content': user_text,
        'timestamp': _now(),
    }
    chat['messages'].append(user_msg)

    # Store assistant message with full verification metadata
    content = agent_response.get('content', '') if isinstance(agent_response, dict) else str(agent_response)
    assistant_msg = {
        'role': 'assistant',
        'content': content,
        'timestamp': _now(),
        'meta': {
            'verified': agent_response.get('verified', False) if isinstance(agent_response, dict) else False,
            'constraints_passed': (agent_response.get('constraints', {}).get('passed', [])
                                   if isinstance(agent_response, dict) else []),
            'constraints_failed': (agent_response.get('constraints', {}).get('failed', [])
                                   if isinstance(agent_response, dict) else []),
            'processing_time_ms': elapsed,
            'response_source': response_source,
            'pipeline_trace': pipeline_trace,
            'ada_whisper': ada_whisper,
            'ada_watch': ada_watch,
            'trajectory': trajectory_info,
            'kinematic': kinematic_info,
            'meta_verification': meta_verification,
        }
    }
    chat['messages'].append(assistant_msg)

    # Update chat title from first user message
    if len(chat['messages']) <= 2:
        chat['title'] = user_text[:40] + ('...' if len(user_text) > 40 else '')
    chat['updated'] = _now()

    return jsonify(assistant_msg)


# ═══════════════════════════════════════════════════════════════
# DIRECT INTELLIGENCE ENDPOINTS
# ═══════════════════════════════════════════════════════════════

# ── Calculate (TI Calculator + Logic Engine) ──

@app.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.get_json() or {}
    expr = data.get('expression', '').strip()
    if not expr:
        return jsonify({'error': 'empty expression'}), 400

    result = {'expression': expr, 'source': None, 'value': None, 'verified': False}

    # Try TI Calculator first
    try:
        ti = get_ti_calculator()
        if ti:
            ti_result = ti.calculate(expr)
            if ti_result:
                val, meta = ti_result
                result['value'] = val
                result['display'] = ti.format_result(val, meta)
                result['source'] = 'ti_calculator'
                result['verified'] = True
                return jsonify(result)
    except Exception:
        pass

    # Fallback to Logic Engine
    try:
        engine = get_logic_engine()
        if engine:
            import re
            m = re.match(r'^(\d+(?:\.\d+)?)\s*([+\-*/^])\s*(\d+(?:\.\d+)?)', expr)
            if m:
                a, op, b = float(m.group(1)), m.group(2), float(m.group(3))
                op_map = {'+': '+', '-': '-', '*': '*', '/': '/', '^': '**'}
                logic_expr = {"op": op_map.get(op, op), "args": [a, b]}
                r = engine.evaluate(logic_expr)
                if r.verified:
                    val = r.value.data
                    result['value'] = float(val)
                    result['source'] = 'logic_engine'
                    result['verified'] = True
                    result['operations'] = r.operations
                    result['elapsed_us'] = r.elapsed_us
                    return jsonify(result)
    except Exception:
        pass

    return jsonify({'error': 'Could not evaluate expression', 'expression': expr}), 400


# ── Knowledge Query (KB + Mesh) ──

@app.route('/api/knowledge/query', methods=['POST'])
def knowledge_query():
    data = request.get_json() or {}
    q = data.get('query', '').strip()
    if not q:
        return jsonify({'error': 'empty query'}), 400

    # Try KB first
    try:
        kb = get_knowledge_base()
        if kb:
            fact = kb.query(q)
            if fact:
                return jsonify({
                    'answer': fact.fact,
                    'source': 'knowledge_base',
                    'category': fact.category,
                    'confidence': fact.confidence,
                    'source_url': fact.source_url,
                })
    except Exception:
        pass

    # Try Knowledge Mesh
    try:
        mesh = get_knowledge_mesh()
        if mesh:
            result = mesh.query(q)
            if result:
                return jsonify({
                    'answer': str(result.value),
                    'source': 'knowledge_mesh',
                    'key': result.key,
                    'primary_source': result.primary_source,
                })
    except Exception:
        pass

    return jsonify({'answer': None, 'source': None, 'message': 'No matching fact found'})


# ── Semantic Resolve ──

@app.route('/api/semantic/resolve', methods=['POST'])
def semantic_resolve():
    data = request.get_json() or {}
    q = data.get('query', '').strip()
    if not q:
        return jsonify({'error': 'empty query'}), 400

    try:
        resolver = get_semantic_resolver()
        if resolver:
            shape = resolver.detect_shape(q)
            entity = resolver.extract_entity(q)
            return jsonify({
                'query': q,
                'detected_shape': shape,
                'entity': entity,
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'query': q, 'detected_shape': None, 'entity': None})


# ── Grounding ──

@app.route('/api/ground', methods=['POST'])
def ground_claim():
    data = request.get_json() or {}
    claim = data.get('claim', '').strip()
    if not claim:
        return jsonify({'error': 'empty claim'}), 400

    try:
        engine = get_grounding_engine()
        if engine:
            result = engine.verify_claim(claim)
            return jsonify(result.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Grounding engine not available'}), 503


# ── Identity ──

@app.route('/api/identity', methods=['GET'])
def identity_info():
    try:
        identity = get_identity()
        if identity:
            return jsonify(identity.to_dict())
    except Exception:
        pass
    return jsonify({'name': 'Newton', 'status': 'identity module not loaded'})


# ── TinyTalk Eval ──

@app.route('/api/tinytalk/eval', methods=['POST'])
def tinytalk_eval():
    data = request.get_json() or {}
    code = data.get('code', '').strip()
    if not code:
        return jsonify({'error': 'empty code'}), 400

    try:
        kernel = get_tinytalk()
        if kernel:
            result = kernel.run(code)
            return jsonify({
                'code': code,
                'result': str(result),
                'verified': True,
                'source': 'realTinyTalk',
            })
    except Exception as e:
        return jsonify({'code': code, 'error': str(e), 'source': 'realTinyTalk'}), 400

    return jsonify({'error': 'TinyTalk kernel not available'}), 503


# ── Adanpedia Witness Examples ──

@app.route('/api/adanpedia', methods=['GET'])
def adanpedia():
    try:
        fetch_fn = get_adanpedia()
        if fetch_fn:
            examples = fetch_fn()
            return jsonify({'examples': examples, 'count': len(examples)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify({'examples': [], 'count': 0})


# ═══════════════════════════════════════════════════════════════
# TRAJECTORY: Real-time composition feedback
# ═══════════════════════════════════════════════════════════════

@app.route('/api/trajectory/compose', methods=['POST'])
def trajectory_compose():
    data = request.get_json() or {}
    text = data.get('text', '')
    try:
        composer = get_composer()
        if not composer:
            return jsonify({'error': 'Trajectory composer not available'}), 503
        state = composer.compose(text)
        return jsonify({
            'text': state.text,
            'weight': round(state.current_weight, 3),
            'curvature': round(state.current_curvature, 3),
            'commit': round(state.current_commit, 3),
            'envelope_depth': state.envelope_depth,
            'needs_closure': state.needs_closure,
            'approaching_commit': state.approaching_commit,
            'suggestions': state.suggested_completions,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/trajectory/keystroke', methods=['POST'])
def trajectory_keystroke():
    data = request.get_json() or {}
    char = data.get('char', '')
    try:
        composer = get_composer()
        if not composer:
            return jsonify({'error': 'Trajectory composer not available'}), 503
        result = composer.keystroke_analysis(char)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════
# KINEMATIC: Language analysis
# ═══════════════════════════════════════════════════════════════

@app.route('/api/kinematic/analyze', methods=['POST'])
def kinematic_analyze():
    data = request.get_json() or {}
    text = data.get('text', '')
    try:
        analyzer = get_analyzer()
        if not analyzer:
            return jsonify({'error': 'Kinematic analyzer not available'}), 503
        result = analyzer.analyze_sentence(text)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/kinematic/alphabet', methods=['GET'])
def kinematic_alphabet():
    try:
        analyzer = get_analyzer()
        if not analyzer:
            return jsonify({'error': 'Kinematic analyzer not available'}), 503
        alpha = {}
        for char, sig in analyzer.signatures.items():
            alpha[char] = sig.to_dict() if hasattr(sig, 'to_dict') else {
                'weight': sig.weight,
                'curvature': sig.curvature,
                'commit_strength': sig.commit_strength,
            }
        return jsonify(alpha)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════
# KNOWLEDGE BANK (summary)
# ═══════════════════════════════════════════════════════════════

@app.route('/api/knowledge', methods=['GET'])
def list_knowledge():
    try:
        kb = get_knowledge_base()
        if kb:
            return jsonify({
                'facts_count': len(kb.facts) if hasattr(kb, 'facts') else 0,
                'categories': list(set(f.category for f in kb.facts)) if hasattr(kb, 'facts') else [],
            })
    except Exception:
        pass
    return jsonify({'facts_count': 0, 'categories': []})


# ═══════════════════════════════════════════════════════════════
# HEALTH / STATUS  (all 14+ subsystems)
# ═══════════════════════════════════════════════════════════════

SYSTEM_CATALOG = [
    ('agent',               'Newton Agent',           get_agent),
    ('logic_engine',        'Logic Engine',           get_logic_engine),
    ('ti_calculator',       'TI Calculator',          get_ti_calculator),
    ('knowledge_base',      'Knowledge Base',         get_knowledge_base),
    ('knowledge_mesh',      'Knowledge Mesh',         get_knowledge_mesh),
    ('semantic_resolver',   'Semantic Resolver',      get_semantic_resolver),
    ('grounding_engine',    'Grounding Engine',       get_grounding_engine),
    ('ada_sentinel',        'Ada Sentinel',           get_ada_sentinel),
    ('meta_newton',         'Meta Newton',            get_meta),
    ('identity',            'Identity',               get_identity),
    ('kinematic_linguistics', 'Kinematic Linguistics', get_analyzer),
    ('trajectory_verifier', 'Trajectory Verifier',    get_verifier),
    ('trajectory_composer', 'Trajectory Composer',    get_composer),
    ('tinytalk',            'realTinyTalk',           get_tinytalk),
    ('adanpedia',           'Adanpedia',              get_adanpedia),
]


@app.route('/api/health', methods=['GET'])
def health():
    components = {}
    for key, _name, loader in SYSTEM_CATALOG:
        try:
            obj = loader()
            components[key] = 'ok' if obj is not None else 'not loaded'
        except Exception as e:
            components[key] = f'error: {str(e)}'

    ok_count = sum(1 for v in components.values() if v == 'ok')
    total = len(components)

    return jsonify({
        'status': 'healthy' if ok_count == total else ('degraded' if ok_count > total // 2 else 'critical'),
        'systems_online': ok_count,
        'systems_total': total,
        'components': components,
        'chats': len(chats),
        'timestamp': _now(),
    })


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    print(f"""
    ╭──────────────────────────────────────────────╮
    │                                              │
    │   ProjectADA  (Synthesized)                  │
    │   System of Systems Agent                    │
    │                                              │
    │   14 Intelligence Subsystems:                │
    │   Newton Agent    Logic Engine    TI Calc    │
    │   Knowledge Base  Knowledge Mesh             │
    │   Semantic Resolver  Grounding Engine         │
    │   Ada Sentinel  Meta Newton  Identity        │
    │   Kinematic Linguistics  Trajectory          │
    │   realTinyTalk  Adanpedia                    │
    │                                              │
    │   http://localhost:{port}                      │
    │                                              │
    ╰──────────────────────────────────────────────╯
    """)
    app.run(host='0.0.0.0', port=port, debug=True)
