#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON AGENT - SELF-VERIFYING AUTONOMOUS AGENT
═══════════════════════════════════════════════════════════════════════════════

The constraint IS the instruction.
The verification IS the computation.
The ledger IS the memory.

Pipeline:
    User Input → Constraint Check → Grounding → Action → Ledger → Response

Every action the agent takes is:
    1. Checked against safety constraints (BEFORE execution)
    2. Grounded against external evidence (factual claims)
    3. Logged to immutable ledger (audit trail)
    4. Verified for consistency (hash-chained)

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
"""

import time
import hashlib
import re
import json
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from enum import Enum

from .grounding_enhanced import EnhancedGroundingEngine, GroundingResult, SourceTier
from .memory import AgentMemory, ConversationTurn, TurnRole, ConstraintCheck, GroundingInfo
from .knowledge_base import get_knowledge_base, VerifiedFact
from .trajectory_verifier import get_trajectory_verifier, TrajectoryVerification

# Import new components: Ada (sentinel), Meta Newton (self-verifier), Knowledge Mesh
try:
    from .ada import get_ada, Ada, Whisper, AlertLevel
    _ada = get_ada()
except ImportError:
    _ada = None

try:
    from .meta_newton import get_meta_newton, MetaNewton, MetaVerification
    _meta = get_meta_newton()
except ImportError:
    _meta = None

try:
    from .knowledge_sources import get_knowledge_mesh, KnowledgeMesh
    _knowledge_mesh = get_knowledge_mesh()
except ImportError:
    _knowledge_mesh = None

# Import Identity - Newton's self-knowledge
try:
    from .identity import get_identity, Identity
    _identity = get_identity()
except ImportError:
    _identity = None

# Import Logic Engine for math evaluation
try:
    from core.logic import LogicEngine, ExecutionBounds
    _logic_engine = LogicEngine(ExecutionBounds(timeout_seconds=5.0, max_operations=10000))
except ImportError:
    _logic_engine = None

# Import TI Calculator for full math expression parsing
try:
    from .ti_calculator import TICalculatorEngine
    _ti_calculator = TICalculatorEngine()
except ImportError:
    _ti_calculator = None


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AgentConfig:
    """Configuration for the Newton Agent."""
    # Safety
    max_tokens: int = 4096
    enable_grounding: bool = True
    require_official_sources: bool = False
    grounding_threshold: float = 5.0  # Claims above this score are flagged
    
    # Memory
    max_conversation_turns: int = 50
    
    # Behavior
    allow_code_execution: bool = False
    allow_web_requests: bool = True
    allow_file_operations: bool = False
    
    # Constraints
    enable_harm_filter: bool = True
    enable_medical_filter: bool = True
    enable_legal_filter: bool = True
    enable_security_filter: bool = True


class ActionType(Enum):
    """Types of actions the agent can take."""
    RESPOND = "respond"           # Generate a response
    GROUND = "ground"             # Verify a claim
    CALCULATE = "calculate"       # Perform calculation
    SEARCH = "search"             # Search for information
    REFUSE = "refuse"             # Refuse to act (constraint violation)
    CLARIFY = "clarify"           # Ask for clarification


@dataclass
class AgentResponse:
    """Complete agent response with full provenance."""
    content: str
    action_type: ActionType
    verified: bool
    
    # Constraint checking
    constraints_passed: List[str] = field(default_factory=list)
    constraints_failed: List[str] = field(default_factory=list)
    
    # Grounding
    grounding_results: List[Dict] = field(default_factory=list)
    unverified_claims: List[str] = field(default_factory=list)
    
    # Metadata
    timestamp: int = 0
    processing_time_ms: int = 0
    turn_hash: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "content": self.content,
            "action": self.action_type.value,
            "verified": self.verified,
            "constraints": {
                "passed": self.constraints_passed,
                "failed": self.constraints_failed,
            },
            "grounding": {
                "results": self.grounding_results,
                "unverified_claims": self.unverified_claims,
            },
            "meta": {
                "timestamp": self.timestamp,
                "processing_time_ms": self.processing_time_ms,
                "turn_hash": self.turn_hash,
            }
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SAFETY CONSTRAINTS
# ═══════════════════════════════════════════════════════════════════════════════

SAFETY_CONSTRAINTS = {
    "harm": {
        "name": "No Harm",
        "description": "Blocks requests that could cause physical harm",
        "patterns": [
            r"(how to )?(make|build|create|construct).*\b(bomb|weapon|explosive|explosives|poison|grenade)\b",
            r"(how to )?(kill|murder|harm|hurt|injure|assassinate)",
            r"(how to )?(suicide|self.harm)",
            r"\b(i want to|i need to|help me) (kill|murder|harm|hurt)",
            r"\b(bomb|explosive|explosives|weapon|poison|grenade)\b",
        ]
    },
    "medical": {
        "name": "Medical Bounds",
        "description": "Prevents medical diagnosis or prescription",
        "patterns": [
            r"what (medication|drug|dosage|prescription) should (i|you) take",
            r"diagnose (my|this|the)",
            r"prescribe (me|a)",
            r"(am i|do i have) (sick|ill|infected|dying)",
        ]
    },
    "legal": {
        "name": "Legal Bounds",
        "description": "Blocks illegal activity instructions",
        "patterns": [
            r"(how to )?(evade|avoid|cheat).*(tax|irs)",
            r"(how to )?(launder|hide|offshore) money",
            r"(how to )?(forge|fake|counterfeit)",
            r"(how to )?(steal|rob|burgle)",
            r"\billegal (activity|activities|action|actions)\b",
            r"\binstructions for illegal\b",
        ]
    },
    "security": {
        "name": "Security",
        "description": "Blocks hacking and security exploits",
        "patterns": [
            r"(how to )?(hack|crack|break into|exploit|bypass)",
            r"\b(steal password|phishing|malware|ransomware)\b",
            r"(how to )?(ddos|denial of service)",
            r"\bjailbreak (mode|enabled|activated)\b",
            r"\bignore (filters|safety|rules|restrictions|your rules)\b",
            r"\bno (restrictions|limitations|rules|filters)\b",
            r"\boverride (safety|security|filters|rules)\b",
            r"\bsystem prompt\b.*\b(ignore|bypass|override)\b",
        ]
    },
    "privacy": {
        "name": "Privacy",
        "description": "Blocks requests for personal information",
        "patterns": [
            r"(give me|find|get).*(social security|ssn|credit card)",
            r"(dox|doxx|expose).*personal",
            r"(how to )?(stalk|track|spy on)",
        ]
    }
}


# ═══════════════════════════════════════════════════════════════════════════════
# NEWTON AGENT
# ═══════════════════════════════════════════════════════════════════════════════

class NewtonAgent:
    """
    Self-verifying autonomous agent powered by Newton OS.
    
    Every action is:
    - Constraint-checked before execution
    - Grounded against external evidence
    - Logged to immutable memory
    - Hash-chained for audit
    """
    
    def __init__(
        self,
        config: AgentConfig = None,
        response_generator: Callable[[str, List[Dict]], str] = None
    ):
        self.config = config or AgentConfig()
        self.memory = AgentMemory(max_turns=self.config.max_conversation_turns)
        self.grounding = EnhancedGroundingEngine()
        self.knowledge_base = get_knowledge_base()
        self.trajectory_verifier = get_trajectory_verifier()
        self.response_generator = response_generator
        
        # Stats
        self.total_requests = 0
        self.blocked_requests = 0
        self.grounded_claims = 0
        self.kb_hits = 0
        self.trajectory_checks = 0
        
        # Initialize with system message
        self.memory.add_turn(
            role=TurnRole.SYSTEM,
            content=(
                "You are Newton Agent, a self-verifying AI assistant. "
                "Every claim you make should be factual and verifiable. "
                "If you're uncertain about something, say so. "
                "You cannot provide medical, legal, or financial advice. "
                "You prioritize accuracy over helpfulness."
            ),
            verified=True,
        )
    
    def _check_constraints(self, text: str) -> tuple[List[str], List[str]]:
        """
        Check text against safety constraints.
        Returns (passed, failed) constraint names.
        """
        passed = []
        failed = []
        text_lower = text.lower()
        
        constraint_map = {
            "harm": self.config.enable_harm_filter,
            "medical": self.config.enable_medical_filter,
            "legal": self.config.enable_legal_filter,
            "security": self.config.enable_security_filter,
            "privacy": True,  # Always on
        }
        
        for constraint_id, constraint_data in SAFETY_CONSTRAINTS.items():
            if not constraint_map.get(constraint_id, True):
                continue
                
            violated = False
            for pattern in constraint_data["patterns"]:
                if re.search(pattern, text_lower):
                    violated = True
                    break
            
            if violated:
                failed.append(constraint_id)
            else:
                passed.append(constraint_id)
        
        return passed, failed
    
    def _extract_claims(self, text: str) -> List[str]:
        """Extract factual claims from text for grounding."""
        claims = []
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 10:
                continue
            
            # Skip questions
            if sentence.endswith('?') or sentence.lower().startswith(('what', 'how', 'why', 'when', 'where', 'who', 'is', 'are', 'can', 'could', 'would')):
                continue
            
            # Skip obvious opinions/preferences
            if re.search(r'^(i think|i believe|in my opinion|maybe|perhaps)', sentence.lower()):
                continue
            
            # Look for factual indicators
            factual_patterns = [
                r'\b(is|are|was|were)\b',  # State of being
                r'\b(created|invented|founded|discovered)\b',  # Historical
                r'\b(according to|research shows|studies show)\b',  # Citations
                r'\b\d{4}\b',  # Contains a year
                r'\b(always|never|every|all)\b',  # Absolute claims
            ]
            
            for pattern in factual_patterns:
                if re.search(pattern, sentence.lower()):
                    claims.append(sentence)
                    break
        
        return claims[:5]  # Limit to 5 claims for performance
    
    def _ground_claims(self, claims: List[str]) -> tuple[List[GroundingInfo], List[str]]:
        """Ground claims against external sources."""
        grounding_results = []
        unverified = []
        
        for claim in claims:
            # First, check knowledge base for instant verification
            kb_verify = self.knowledge_base.verify_statement(claim)
            if kb_verify:
                is_correct, fact = kb_verify
                info = GroundingInfo(
                    claim=claim,
                    score=0.0 if is_correct else 10.0,
                    status="VERIFIED" if is_correct else "INCORRECT",
                    sources=[fact.source_url],
                )
                grounding_results.append(info)
                if not is_correct:
                    unverified.append(claim)
                continue
            
            # Fall back to external grounding
            result = self.grounding.verify_claim(
                claim,
                require_official=self.config.require_official_sources,
            )
            self.grounded_claims += 1
            
            info = GroundingInfo(
                claim=claim,
                score=result.confidence_score,
                status=result.status,
                sources=[e.url for e in result.evidence[:3]],
            )
            grounding_results.append(info)
            
            if result.confidence_score > self.config.grounding_threshold:
                unverified.append(claim)
        
        return grounding_results, unverified
    
    def _try_knowledge_base(self, user_input: str) -> Optional[str]:
        """Try to answer from knowledge base first (no LLM needed)."""
        fact = self.knowledge_base.query(user_input)
        if fact:
            self.kb_hits += 1
            return f"{fact.fact}\n\n📚 *Source: {fact.source}*"
        return None
    
    def _try_knowledge_mesh(self, user_input: str) -> Optional[str]:
        """Try to answer from the expanded knowledge mesh."""
        if not _knowledge_mesh:
            return None
        
        result = _knowledge_mesh.query(user_input)
        if result:
            # Format the response based on the data
            value = result.value
            
            if isinstance(value, dict):
                # Format dict-style facts
                if "type" in value and value["type"] == "planet":
                    return (
                        f"**{result.key.split(':')[1].title()}** ({value['type']})\n"
                        f"• Mass: {value.get('mass_kg', 'N/A')} kg\n"
                        f"• Radius: {value.get('radius_km', 'N/A')} km\n"
                        f"• Orbital period: {value.get('orbital_period_days', 'N/A')} days\n\n"
                        f"🌐 *Source: {result.primary_source.upper()}*"
                    )
                elif "height_m" in value:
                    return (
                        f"**{result.key.split(':')[1].replace('_', ' ').title()}**: "
                        f"{value['height_m']:,} meters ({value['height_m'] * 3.281:.0f} ft)\n"
                        f"Location: {value.get('location', 'N/A')}\n\n"
                        f"🏔️ *Source: {result.primary_source.upper()}*"
                    )
                elif "depth_m" in value:
                    return (
                        f"**{result.key.split(':')[1].replace('_', ' ').title()}**: "
                        f"{value['depth_m']:,} meters deep\n"
                        f"Location: {value.get('location', 'N/A')}\n\n"
                        f"🌊 *Source: {result.primary_source.upper()}*"
                    )
                elif "created" in value and "creator" in value:
                    return (
                        f"**{result.key.split(':')[1].title()}** was created in "
                        f"{value['created']} by {value['creator']}.\n"
                        f"Type: {value.get('typing', 'N/A')} typing\n\n"
                        f"💻 *Source: {result.primary_source.title()}*"
                    )
                elif "symbol" in value and "atomic_number" in value:
                    return (
                        f"**{result.key.split(':')[1].title()}** ({value['symbol']})\n"
                        f"• Atomic number: {value['atomic_number']}\n"
                        f"• Atomic mass: {value['atomic_mass']}\n\n"
                        f"⚛️ *Source: {result.primary_source.upper()}*"
                    )
                elif "value" in value and "unit" in value:
                    return (
                        f"**{result.key.split(':')[1].replace('_', ' ').title()}**: "
                        f"{value['value']:,.2f} {value['unit']} ({value.get('year', 'latest')})\n\n"
                        f"📊 *Source: {result.primary_source.title()}*"
                    )
                elif "value" in value and "symbol" in value:
                    return (
                        f"**{value.get('name', result.key.split(':')[1]).title()}** ({value['symbol']}): "
                        f"{value['value']}\n\n"
                        f"🔢 *Source: {result.primary_source.upper()}*"
                    )
            
            # Fallback for other formats
            return f"{result.key}: {result.value}\n\n*Source: {result.primary_source}*"
        
        return None

    def _try_math_evaluation(self, user_input: str) -> Optional[str]:
        """
        Try to evaluate math expressions using TI Calculator + Logic Engine.
        
        Supports TI-84 style calculations:
        - Chained operations: 3*3*3, 2+3*4-5
        - Parentheses: (2+3)*4
        - Functions: sqrt(16), sin(0), log(100)
        - Constants: pi, e
        - Powers: 2^10
        - Factorials: 5!
        """
        # Use TI Calculator if available
        if _ti_calculator:
            result = _ti_calculator.calculate(user_input)
            if result:
                val, meta = result
                return _ti_calculator.format_result(val, meta)
        
        # Fallback to basic Logic Engine for simple expressions
        if not _logic_engine:
            return None
        
        # Simple patterns for basic fallback
        math_patterns = [
            # "What is 2 + 2?" or "what's 5 * 3"
            r"what(?:'s| is)\s+(\d+(?:\.\d+)?)\s*([+\-*/×÷^])\s*(\d+(?:\.\d+)?)",
            # "calculate 2 + 2" or "compute 5 * 3"
            r"(?:calculate|compute|evaluate|solve)\s+(\d+(?:\.\d+)?)\s*([+\-*/×÷^])\s*(\d+(?:\.\d+)?)",
            # Just "2 + 2" or "5 * 3"
            r"^(\d+(?:\.\d+)?)\s*([+\-*/×÷^])\s*(\d+(?:\.\d+)?)\s*[?]?$",
        ]
        
        text = user_input.lower().strip()
        
        for pattern in math_patterns:
            match = re.search(pattern, text)
            if match:
                a, op, b = match.groups()
                a, b = float(a), float(b)
                
                # Map operators
                op_map = {
                    '+': '+', '-': '-', '*': '*', '×': '*',
                    '/': '/', '÷': '/', '^': '**'
                }
                newton_op = op_map.get(op, op)
                
                # Build expression
                expr = {"op": newton_op, "args": [a, b]}
                
                try:
                    result = _logic_engine.evaluate(expr)
                    if result.verified and result.value.type.value != "error":
                        val = result.value.data
                        # Format nicely
                        if float(val) == int(val):
                            val = int(val)
                        return (
                            f"**{val}**\n\n"
                            f"🔢 *Computed by Newton Logic Engine (verified: {result.verified}, "
                            f"{result.operations} ops, {result.elapsed_us}μs)*"
                        )
                except Exception:
                    pass
        
        return None
    
    def _get_datetime_context(self) -> str:
        """Get current date/time context for the model."""
        now = datetime.now()
        return (
            f"Current date: {now.strftime('%A, %B %d, %Y')}\n"
            f"Current time: {now.strftime('%I:%M %p %Z').strip()}\n"
            f"Timestamp: {now.isoformat()}"
        )
    
    def _generate_response(self, user_input: str, context: List[Dict]) -> str:
        """Generate response using LLM (knowledge base is checked separately)."""
        # Use LLM with datetime context
        if self.response_generator:
            # Inject current datetime as system context
            datetime_context = self._get_datetime_context()
            enriched_context = [
                {"role": "system", "content": f"[CURRENT TIME]\n{datetime_context}"},
                *context
            ]
            return self.response_generator(user_input, enriched_context)
        
        # Default: echo with verification note
        now = datetime.now()
        return f"I received your message: '{user_input}'. (Note: No LLM backend configured - using echo mode. Current time: {now.strftime('%Y-%m-%d %H:%M')})"
    
    def _generate_refusal(self, failed_constraints: List[str]) -> str:
        """Generate a refusal message for constraint violations."""
        constraint_names = [
            SAFETY_CONSTRAINTS[c]["name"] 
            for c in failed_constraints 
            if c in SAFETY_CONSTRAINTS
        ]
        
        return (
            f"I can't help with that request. It violates the following safety constraints: "
            f"{', '.join(constraint_names)}. "
            f"This isn't a limitation - it's by design. "
            f"The constraint IS the instruction."
        )
    
    def process(self, user_input: str) -> AgentResponse:
        """
        Process user input through the full verification pipeline.
        
        Pipeline:
        1. Ada senses the input (intuitive check)
        2. Log user input
        3. Check safety constraints
        4. If blocked → refuse
        5. Generate response (KB → Mesh → Math → LLM)
        6. Ada watches the response
        7. Ground factual claims in response
        8. Meta Newton verifies the pipeline
        9. Log response with metadata
        10. Return verified response
        """
        start_time = time.time()
        self.total_requests += 1
        
        # Track operations for Meta Newton
        operations = 0
        ada_whispers = []
        
        # 1. Ada senses the input (quick intuitive check)
        if _ada:
            input_whisper = _ada.sense(user_input)
            if input_whisper and input_whisper.level in [AlertLevel.ALERT, AlertLevel.ALARM]:
                ada_whispers.append(input_whisper)
        operations += 1
        
        # 2. Log user input
        user_turn = self.memory.add_turn(
            role=TurnRole.USER,
            content=user_input,
        )
        operations += 1
        
        # 3. Check safety constraints on user input
        passed, failed = self._check_constraints(user_input)
        operations += 1
        
        # 4. If constraints violated → refuse
        if failed:
            self.blocked_requests += 1
            refusal = self._generate_refusal(failed)
            
            response_turn = self.memory.add_turn(
                role=TurnRole.ASSISTANT,
                content=refusal,
                constraints=[
                    ConstraintCheck(c, c in passed, "") 
                    for c in list(SAFETY_CONSTRAINTS.keys())
                ],
                verified=True,
                action="refuse",
            )
            
            return AgentResponse(
                content=refusal,
                action_type=ActionType.REFUSE,
                verified=True,
                constraints_passed=passed,
                constraints_failed=failed,
                timestamp=int(time.time()),
                processing_time_ms=int((time.time() - start_time) * 1000),
                turn_hash=response_turn.hash,
            )
        
        # 5. Generate response (identity first, then knowledge base, mesh, math, LLM)
        context = self.memory.get_context(max_turns=10)
        
        # Check if this is an identity question (Newton knows himself)
        identity_answer = None
        is_identity_response = False
        if _identity:
            identity_answer = _identity.respond_to_identity_question(user_input)
            is_identity_response = identity_answer is not None
        operations += 1
        
        # Check knowledge base (already verified)
        kb_answer = None
        is_kb_response = False
        if not is_identity_response:
            kb_answer = self._try_knowledge_base(user_input)
            is_kb_response = kb_answer is not None
        operations += 1
        
        # Check knowledge mesh for expanded data
        mesh_answer = None
        is_mesh_response = False
        if not is_identity_response and not is_kb_response and _knowledge_mesh:
            mesh_answer = self._try_knowledge_mesh(user_input)
            is_mesh_response = mesh_answer is not None
        operations += 1
        
        # Check if this is a math question (use Logic Engine)
        math_answer = None
        is_math_response = False
        if not is_identity_response and not is_kb_response and not is_mesh_response:
            math_answer = self._try_math_evaluation(user_input)
            is_math_response = math_answer is not None
        operations += 1
        
        if is_identity_response:
            response_content = identity_answer
            response_source = "identity"
        elif is_kb_response:
            response_content = kb_answer
            response_source = "knowledge_base"
        elif is_mesh_response:
            response_content = mesh_answer
            response_source = "knowledge_mesh"
        elif is_math_response:
            response_content = math_answer
            response_source = "logic_engine"
        else:
            response_content = self._generate_response(user_input, context)
            response_source = "llm"
        operations += 1
        
        # 6. Ada watches the response
        if _ada:
            response_whisper = _ada.watch_response(
                query=user_input,
                response=response_content,
                verified=is_kb_response or is_mesh_response or is_math_response,
                sources=[response_source]
            )
            if response_whisper and response_whisper.level in [AlertLevel.ALERT, AlertLevel.ALARM]:
                ada_whispers.append(response_whisper)
        operations += 1
        
        # 7. Check constraints on response (self-check)
        response_passed, response_failed = self._check_constraints(response_content)
        operations += 1
        
        # 8. Ground factual claims in response (skip for identity/KB/mesh/math - already verified)
        grounding_results = []
        unverified_claims = []
        
        if self.config.enable_grounding and not is_identity_response and not is_kb_response and not is_mesh_response and not is_math_response:
            claims = self._extract_claims(response_content)
            if claims:
                grounding_results, unverified_claims = self._ground_claims(claims)
                
                # Add warnings for unverified claims
                if unverified_claims:
                    response_content += (
                        f"\n\n⚠️ **Note**: The following claims could not be fully verified "
                        f"against official sources: {', '.join(unverified_claims[:2])}..."
                    )
        operations += 1
        
        # 9. Meta Newton verifies the pipeline
        elapsed_ms = int((time.time() - start_time) * 1000)
        meta_verified = True
        
        if _meta:
            meta_context = {
                "iterations": operations,
                "max_iterations": 1000,
                "elapsed_ms": elapsed_ms,
                "max_time_ms": 30000,
                "meta_depth": 0,
            }
            meta_result = _meta.quick_check(meta_context)
            meta_verified = meta_result[0]
        
        # Identity, KB, mesh, and math answers are always verified (Newton trusts himself)
        is_verified = (is_identity_response or is_kb_response or is_mesh_response or is_math_response or 
                      (len(response_failed) == 0 and len(unverified_claims) == 0)) and meta_verified
        
        # Add Ada warnings if any (skip for identity - Newton knows himself)
        if ada_whispers and not is_identity_response and not is_kb_response and not is_mesh_response:
            warning_count = len(ada_whispers)
            response_content += f"\n\n🐕 *Ada detected {warning_count} potential issue(s) - review recommended*"
        
        # 10. Log response with full metadata
        response_turn = self.memory.add_turn(
            role=TurnRole.ASSISTANT,
            content=response_content,
            constraints=[
                ConstraintCheck(c, c in response_passed, "")
                for c in list(SAFETY_CONSTRAINTS.keys())
            ],
            grounding=grounding_results,
            verified=is_verified,
            action="respond",
        )
        
        # 11. Build and return response
        return AgentResponse(
            content=response_content,
            action_type=ActionType.RESPOND,
            verified=is_verified,
            constraints_passed=passed + response_passed,
            constraints_failed=failed + response_failed,
            grounding_results=[g.to_dict() for g in grounding_results],
            unverified_claims=unverified_claims,
            timestamp=int(time.time()),
            processing_time_ms=int((time.time() - start_time) * 1000),
            turn_hash=response_turn.hash,
        )
    
    def ground_claim(self, claim: str) -> Dict:
        """Directly ground a specific claim."""
        result = self.grounding.verify_claim(claim)
        return result.to_dict()
    
    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history."""
        return self.memory.get_full_history()
    
    def export_audit_trail(self) -> Dict:
        """Export full audit trail."""
        return {
            **self.memory.export_audit_trail(),
            "agent_stats": {
                "total_requests": self.total_requests,
                "blocked_requests": self.blocked_requests,
                "grounded_claims": self.grounded_claims,
                "kb_hits": self.kb_hits,
                "block_rate": self.blocked_requests / max(1, self.total_requests),
            },
            "grounding_stats": self.grounding.get_stats(),
            "knowledge_base_stats": self.knowledge_base.get_stats(),
        }
    
    def clear_conversation(self):
        """Clear conversation and start fresh."""
        self.memory.clear()
        # Re-add system message
        self.memory.add_turn(
            role=TurnRole.SYSTEM,
            content=(
                "You are Newton Agent, a self-verifying AI assistant. "
                "Every claim you make should be factual and verifiable. "
                "If you're uncertain about something, say so."
            ),
            verified=True,
        )
    
    def get_stats(self) -> Dict:
        """Get agent statistics."""
        return {
            "total_requests": self.total_requests,
            "blocked_requests": self.blocked_requests,
            "grounded_claims": self.grounded_claims,
            "kb_hits": self.kb_hits,
            "trajectory_checks": self.trajectory_checks,
            "conversation_turns": len(self.memory.turns),
            "memory_chain_valid": self.memory.verify_chain(),
        }
    
    def verify_trajectory(self, text: str) -> Dict:
        """
        Verify text as a kinematic trajectory through meaning space.
        
        Language IS a Bézier trajectory:
        - Subject → P₀ (anchor)
        - Verb → The curve (motion)
        - Object → P₃ (terminus)
        - Grammar → Ω (admissible region)
        """
        self.trajectory_checks += 1
        result = self.trajectory_verifier.verify(text)
        return result.to_dict()
    
    def analyze_text(self, text: str) -> Dict:
        """
        Full kinematic analysis of text.
        
        Returns trajectory properties:
        - Weight, curvature, commit level
        - Envelope balance
        - Semantic coherence
        """
        from .kinematic_linguistics import get_kinematic_analyzer
        analyzer = get_kinematic_analyzer()
        return analyzer.analyze_sentence(text)
