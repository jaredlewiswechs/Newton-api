#!/usr/bin/env python3
"""
ProjectADA - System of Systems Agent
Wires: Ada Sentinel + Meta Newton + Kinematic Linguistics + Trajectory Composer
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
from dataclasses import asdict

# Add parent to path so we can import adan
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, request, jsonify, send_from_directory, render_template

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'projectada-dev')

# ═══════════════════════════════════════════════════════════════
# LAZY-LOADED ADAN COMPONENTS
# ═══════════════════════════════════════════════════════════════

_agent = None
_verifier = None
_composer = None
_analyzer = None
_meta = None
_ada = None


def get_agent():
    global _agent
    if _agent is None:
        from adan.agent import NewtonAgent, AgentConfig
        config = AgentConfig(
            enable_grounding=True,
            require_official_sources=False,
            grounding_threshold=5.0,
        )
        _agent = NewtonAgent(config=config)
    return _agent


def get_verifier():
    global _verifier
    if _verifier is None:
        from adan.trajectory_verifier import get_trajectory_verifier
        _verifier = get_trajectory_verifier()
    return _verifier


def get_composer():
    global _composer
    if _composer is None:
        from adan.trajectory_verifier import get_trajectory_composer
        _composer = get_trajectory_composer()
    return _composer


def get_analyzer():
    global _analyzer
    if _analyzer is None:
        from adan.kinematic_linguistics import get_kinematic_analyzer
        _analyzer = get_kinematic_analyzer()
    return _analyzer


def get_meta():
    global _meta
    if _meta is None:
        from adan.meta_newton import get_meta_newton
        _meta = get_meta_newton()
    return _meta


def get_ada_sentinel():
    global _ada
    if _ada is None:
        from adan.ada import get_ada
        _ada = get_ada()
    return _ada


# ═══════════════════════════════════════════════════════════════
# IN-MEMORY CHAT STORAGE
# ═══════════════════════════════════════════════════════════════

chats = {}  # id -> {id, title, messages: [{role, content, timestamp, meta}], created, updated}


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
# CORE: SEND MESSAGE (full pipeline)
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

    # ── Step 1: Ada Sentinel pre-scan ──
    ada_whisper = None
    try:
        ada = get_ada_sentinel()
        whisper = ada.sense(user_text)
        if whisper:
            ada_whisper = whisper.to_dict()
    except Exception:
        ada_whisper = None

    # ── Step 2: Trajectory verification of input ──
    trajectory_info = None
    try:
        verifier = get_verifier()
        tv = verifier.verify(user_text)
        trajectory_info = tv.to_dict()
    except Exception:
        trajectory_info = None

    # ── Step 3: Process through Newton Agent ──
    agent_response = None
    try:
        agent = get_agent()
        resp = agent.process(user_text)
        agent_response = resp.to_dict()
    except Exception as e:
        agent_response = {
            'content': f"I understand your question, but I encountered a processing issue. Let me help with what I can.\n\nError: {str(e)}",
            'verified': False,
            'constraints_passed': [],
            'constraints_failed': [],
            'processing_time_ms': int((time.time() - t0) * 1000),
        }

    # ── Step 4: Meta Newton self-verification ──
    meta_verification = None
    try:
        meta = get_meta()
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
    except Exception:
        meta_verification = None

    # ── Step 5: Ada Sentinel post-watch ──
    ada_watch = None
    try:
        ada = get_ada_sentinel()
        content = agent_response.get('content', '') if isinstance(agent_response, dict) else ''
        verified = agent_response.get('verified', False) if isinstance(agent_response, dict) else False
        watch = ada.watch_response(user_text, content, verified)
        if watch:
            ada_watch = watch.to_dict()
    except Exception:
        ada_watch = None

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
            'constraints_passed': agent_response.get('constraints_passed', []) if isinstance(agent_response, dict) else [],
            'constraints_failed': agent_response.get('constraints_failed', []) if isinstance(agent_response, dict) else [],
            'processing_time_ms': elapsed,
            'ada_whisper': ada_whisper,
            'ada_watch': ada_watch,
            'trajectory': trajectory_info,
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
# TRAJECTORY: Real-time composition feedback
# ═══════════════════════════════════════════════════════════════

@app.route('/api/trajectory/compose', methods=['POST'])
def trajectory_compose():
    data = request.get_json() or {}
    text = data.get('text', '')
    try:
        composer = get_composer()
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
        result = analyzer.analyze_sentence(text)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/kinematic/alphabet', methods=['GET'])
def kinematic_alphabet():
    try:
        analyzer = get_analyzer()
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
# HEALTH / STATUS
# ═══════════════════════════════════════════════════════════════

@app.route('/api/health', methods=['GET'])
def health():
    components = {}
    for name, loader in [('agent', get_agent), ('verifier', get_verifier),
                          ('composer', get_composer), ('analyzer', get_analyzer),
                          ('meta_newton', get_meta), ('ada_sentinel', get_ada_sentinel)]:
        try:
            loader()
            components[name] = 'ok'
        except Exception as e:
            components[name] = f'error: {str(e)}'

    all_ok = all(v == 'ok' for v in components.values())
    return jsonify({
        'status': 'healthy' if all_ok else 'degraded',
        'components': components,
        'chats': len(chats),
        'timestamp': _now(),
    })


# ═══════════════════════════════════════════════════════════════
# KNOWLEDGE (placeholder for future knowledge bank)
# ═══════════════════════════════════════════════════════════════

@app.route('/api/knowledge', methods=['GET'])
def list_knowledge():
    try:
        from adan.knowledge_base import get_knowledge_base
        kb = get_knowledge_base()
        return jsonify({
            'facts_count': len(kb.facts) if hasattr(kb, 'facts') else 0,
            'categories': list(set(f.category for f in kb.facts)) if hasattr(kb, 'facts') else [],
        })
    except Exception:
        return jsonify({'facts_count': 0, 'categories': []})


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    print(f"""
    ╭──────────────────────────────────────╮
    │                                      │
    │   ProjectADA                         │
    │   System of Systems Agent            │
    │                                      │
    │   Ada Sentinel + Meta Newton         │
    │   Kinematic Linguistics              │
    │   Trajectory Composer                │
    │                                      │
    │   http://localhost:{port}              │
    │                                      │
    ╰──────────────────────────────────────╯
    """)
    app.run(host='0.0.0.0', port=port, debug=True)
