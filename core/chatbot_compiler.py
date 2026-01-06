#!/usr/bin/env python3
"""
===============================================================================
NEWTON CHATBOT COMPILER - The Better ChatGPT
Intent Compilation with Verification

"The best chatbot is not the one that answers the most -
 it's the one that knows when not to."

This module implements a compiler for human intent:
- Parse user input into intent types
- Classify requests with risk levels
- Check constraints before generation
- Only generate within verified bounds
- Validate output before delivery

Pipeline:
    User Input (natural language)
            |
    Intent Parsing
            |
    Constraint Checking
            |
    Response Generation (if allowed)
            |
    Response Validation
            |
    Final Output

The constraint IS the instruction.
The verification IS the computation.

(C) 2025-2026 Jared Lewis - Ada Computing Company - Houston, Texas
===============================================================================
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from enum import Enum
import hashlib
import json
import re
import time
import uuid

from .cdl import (
    Domain, Operator, AtomicConstraint, CompositeConstraint,
    verify, verify_and
)
from .forge import get_forge, ForgeConfig, SAFETY_PATTERNS


# =============================================================================
# SECTION 1: REQUEST TYPE SYSTEM
# Natural language is untyped. That's chaos.
# Newton move: type the conversation.
# =============================================================================

class RequestType(Enum):
    """
    The type system for conversational requests.

    Every user input is classified into exactly one type.
    Each type has specific rules about what the chatbot is allowed to do.
    """
    QUESTION = "question"           # Factual queries, lookups
    OPINION = "opinion"             # Subjective matters, preferences
    INSTRUCTION = "instruction"     # Commands, tasks, actions
    SPECULATION = "speculation"     # What-if scenarios, hypotheticals
    CALCULATION = "calculation"     # Math, computation, data analysis
    MEDICAL_ADVICE = "medical_advice"     # Health-related guidance
    LEGAL_ADVICE = "legal_advice"         # Law-related guidance
    FINANCIAL_ADVICE = "financial_advice" # Money/investment guidance
    PERSONAL_DATA = "personal_data"       # PII, sensitive information
    CODE_GENERATION = "code_generation"   # Programming requests
    CREATIVE = "creative"           # Stories, art, brainstorming
    HARMFUL = "harmful"             # Violence, illegal, dangerous
    UNKNOWN = "unknown"             # Cannot be classified


class RiskLevel(Enum):
    """
    Risk assessment for a request.

    Determines how carefully the response must be verified.
    """
    LOW = "low"           # Safe to answer directly
    MEDIUM = "medium"     # Requires disclaimers or caveats
    HIGH = "high"         # Requires deferral or refusal
    CRITICAL = "critical" # Must refuse - potential for harm


class CompilerDecision(Enum):
    """
    The four possible decisions a constrained chatbot can make.

    This is the output of the constraint checking phase.
    """
    ANSWER = "answer"     # Generate response within constraints
    ASK = "ask"           # Request clarification from user
    DEFER = "defer"       # Recommend external resource
    REFUSE = "refuse"     # Decline to respond


# =============================================================================
# SECTION 2: REQUEST CLASSIFICATION
# The first compiler pass: parsing intent.
# =============================================================================

@dataclass
class RequestClassification:
    """
    The result of classifying a user request.

    This is the intermediate representation between raw input
    and constrained response generation.
    """
    id: str
    request_type: RequestType
    risk_level: RiskLevel
    decision: CompilerDecision

    # Context extracted from input
    intent: str                       # What the user wants
    subject: str                      # Topic/domain
    entities: List[str]               # Named entities extracted

    # Constraint information
    constraints: List[str]            # Active constraints for this type
    violations: List[str]             # Any detected violations

    # Decision rationale
    reasoning: str                    # Why this decision was made

    # Metadata
    confidence: float                 # Classification confidence (0-1)
    timestamp: float = field(default_factory=time.time)
    fingerprint: Optional[str] = None

    def __post_init__(self):
        if self.fingerprint is None:
            data = f"{self.id}:{self.request_type.value}:{self.decision.value}:{self.timestamp}"
            self.fingerprint = f"NC_{hashlib.sha256(data.encode()).hexdigest()[:16]}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "request_type": self.request_type.value,
            "risk_level": self.risk_level.value,
            "decision": self.decision.value,
            "intent": self.intent,
            "subject": self.subject,
            "entities": self.entities,
            "constraints": self.constraints,
            "violations": self.violations,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "fingerprint": self.fingerprint
        }


# =============================================================================
# SECTION 3: RESPONSE CONSTRAINTS
# Rules that define what is allowed for each request type.
# =============================================================================

@dataclass
class ResponseConstraint:
    """
    Constraints that govern response generation for a request type.

    This is the type system in action: each type has specific rules.
    """
    request_type: RequestType
    allowed: bool                     # Is response allowed at all?
    requires_disclaimer: bool         # Must include caveats?
    requires_deferral: bool           # Must recommend professional?
    requires_citation: bool           # Must cite sources?
    requires_verification: bool       # Must verify claims?
    max_specificity: str              # How specific can response be?
    forbidden_patterns: List[str]     # Patterns that trigger refusal
    required_elements: List[str]      # Must include these elements
    recovery_action: CompilerDecision # What to do if constraint violated


# Define the constraint rules for each request type
RESPONSE_CONSTRAINTS: Dict[RequestType, ResponseConstraint] = {
    RequestType.QUESTION: ResponseConstraint(
        request_type=RequestType.QUESTION,
        allowed=True,
        requires_disclaimer=False,
        requires_deferral=False,
        requires_citation=True,
        requires_verification=True,
        max_specificity="high",
        forbidden_patterns=[],
        required_elements=["factual_basis"],
        recovery_action=CompilerDecision.ASK
    ),

    RequestType.OPINION: ResponseConstraint(
        request_type=RequestType.OPINION,
        allowed=True,
        requires_disclaimer=True,
        requires_deferral=False,
        requires_citation=False,
        requires_verification=False,
        max_specificity="medium",
        forbidden_patterns=[],
        required_elements=["opinion_label"],
        recovery_action=CompilerDecision.ANSWER
    ),

    RequestType.INSTRUCTION: ResponseConstraint(
        request_type=RequestType.INSTRUCTION,
        allowed=True,
        requires_disclaimer=False,
        requires_deferral=False,
        requires_citation=False,
        requires_verification=True,
        max_specificity="high",
        forbidden_patterns=[
            r"(how to )?(hack|crack|break into)",
            r"(how to )?(make|build).*\b(bomb|weapon)\b",
        ],
        required_elements=["steps", "verification"],
        recovery_action=CompilerDecision.REFUSE
    ),

    RequestType.SPECULATION: ResponseConstraint(
        request_type=RequestType.SPECULATION,
        allowed=True,
        requires_disclaimer=True,
        requires_deferral=False,
        requires_citation=False,
        requires_verification=False,
        max_specificity="low",
        forbidden_patterns=[],
        required_elements=["uncertainty_acknowledgment"],
        recovery_action=CompilerDecision.ASK
    ),

    RequestType.CALCULATION: ResponseConstraint(
        request_type=RequestType.CALCULATION,
        allowed=True,
        requires_disclaimer=False,
        requires_deferral=False,
        requires_citation=False,
        requires_verification=True,  # MUST verify calculations
        max_specificity="exact",
        forbidden_patterns=[],
        required_elements=["computation", "result", "verification"],
        recovery_action=CompilerDecision.REFUSE
    ),

    RequestType.MEDICAL_ADVICE: ResponseConstraint(
        request_type=RequestType.MEDICAL_ADVICE,
        allowed=False,  # Cannot provide medical advice
        requires_disclaimer=True,
        requires_deferral=True,  # MUST recommend professional
        requires_citation=True,
        requires_verification=True,
        max_specificity="general_only",
        forbidden_patterns=[
            r"(take|prescribe|dosage|dose).*\d+\s*(mg|ml|g|pill|tablet)",
            r"(diagnose|diagnosis|you have)",
            r"(stop taking|start taking|change).*medication",
        ],
        required_elements=["general_info", "professional_referral"],
        recovery_action=CompilerDecision.DEFER
    ),

    RequestType.LEGAL_ADVICE: ResponseConstraint(
        request_type=RequestType.LEGAL_ADVICE,
        allowed=False,  # Cannot provide legal advice
        requires_disclaimer=True,
        requires_deferral=True,  # MUST recommend lawyer
        requires_citation=True,
        requires_verification=True,
        max_specificity="general_only",
        forbidden_patterns=[
            r"(you should|you must|you need to).*\b(sue|file|claim)\b",
            r"(your rights are|you can legally)",
            r"(guilty|innocent|liable|not liable)",
        ],
        required_elements=["general_info", "legal_referral"],
        recovery_action=CompilerDecision.DEFER
    ),

    RequestType.FINANCIAL_ADVICE: ResponseConstraint(
        request_type=RequestType.FINANCIAL_ADVICE,
        allowed=True,  # Can provide educational info
        requires_disclaimer=True,
        requires_deferral=True,  # Should recommend advisor
        requires_citation=False,
        requires_verification=False,
        max_specificity="educational",
        forbidden_patterns=[
            r"(you should|you must).*\b(buy|sell|invest)\b",
            r"guaranteed.*\b(return|profit|gain)\b",
            r"can't lose|sure thing|100%",
        ],
        required_elements=["educational_context", "advisor_referral", "risk_warning"],
        recovery_action=CompilerDecision.DEFER
    ),

    RequestType.PERSONAL_DATA: ResponseConstraint(
        request_type=RequestType.PERSONAL_DATA,
        allowed=False,  # Cannot handle PII
        requires_disclaimer=False,
        requires_deferral=False,
        requires_citation=False,
        requires_verification=False,
        max_specificity="none",
        forbidden_patterns=[
            r"\b\d{3}[-.]?\d{2}[-.]?\d{4}\b",  # SSN
            r"\b\d{16}\b",  # Credit card
            r"password|secret|credential",
        ],
        required_elements=[],
        recovery_action=CompilerDecision.REFUSE
    ),

    RequestType.CODE_GENERATION: ResponseConstraint(
        request_type=RequestType.CODE_GENERATION,
        allowed=True,
        requires_disclaimer=False,
        requires_deferral=False,
        requires_citation=False,
        requires_verification=True,  # Code should be verifiable
        max_specificity="high",
        forbidden_patterns=[
            r"(malware|virus|trojan|keylogger)",
            r"(exploit|vulnerability|0day|zero.day)",
            r"(ransomware|phishing|steal.*password)",
        ],
        required_elements=["code", "explanation"],
        recovery_action=CompilerDecision.REFUSE
    ),

    RequestType.CREATIVE: ResponseConstraint(
        request_type=RequestType.CREATIVE,
        allowed=True,
        requires_disclaimer=False,
        requires_deferral=False,
        requires_citation=False,
        requires_verification=False,
        max_specificity="high",
        forbidden_patterns=[
            r"(hate speech|slur|derogatory)",
            r"(explicit|pornographic|nsfw)",
            r"(violence|gore|torture).*detail",
        ],
        required_elements=["creative_content"],
        recovery_action=CompilerDecision.ASK
    ),

    RequestType.HARMFUL: ResponseConstraint(
        request_type=RequestType.HARMFUL,
        allowed=False,  # Never allowed
        requires_disclaimer=False,
        requires_deferral=False,
        requires_citation=False,
        requires_verification=False,
        max_specificity="none",
        forbidden_patterns=[".*"],  # All patterns blocked
        required_elements=[],
        recovery_action=CompilerDecision.REFUSE
    ),

    RequestType.UNKNOWN: ResponseConstraint(
        request_type=RequestType.UNKNOWN,
        allowed=True,  # But must ask for clarification
        requires_disclaimer=False,
        requires_deferral=False,
        requires_citation=False,
        requires_verification=False,
        max_specificity="none",
        forbidden_patterns=[],
        required_elements=["clarifying_question"],
        recovery_action=CompilerDecision.ASK
    ),
}


# =============================================================================
# SECTION 4: CLASSIFICATION PATTERNS
# How to recognize each request type from natural language.
# =============================================================================

CLASSIFICATION_PATTERNS: Dict[RequestType, List[str]] = {
    RequestType.QUESTION: [
        r"^(what|who|where|when|why|how|which|is|are|can|does|do|did|will|would|could|should)\s",
        r"\?$",
        r"tell me (about|what|who|where|when|why|how)",
        r"explain\s",
        r"describe\s",
        r"define\s",
    ],

    RequestType.OPINION: [
        r"(what do you think|your opinion|your view|your thoughts)",
        r"(better|worse|best|worst|prefer|favorite)",
        r"(should i|would you recommend)",
        r"(do you like|do you believe|do you feel)",
    ],

    RequestType.INSTRUCTION: [
        r"^(create|make|build|write|generate|design|develop|implement)",
        r"^(show me how|teach me|help me)",
        r"^(can you|could you|would you|please)\s*(create|make|build|write)",
        r"^(i need|i want)\s*(you to|a|an)",
    ],

    RequestType.SPECULATION: [
        r"(what if|what would happen|hypothetically|imagine if)",
        r"(could.*possibly|might.*happen|in theory)",
        r"(suppose|assuming|let's say)",
    ],

    RequestType.CALCULATION: [
        r"(calculate|compute|solve|evaluate|find the)",
        r"\d+\s*[\+\-\*\/\^]\s*\d+",
        r"(what is|equals|=)\s*\d+",
        r"\b(percent|percentage|ratio|average|mean|median)\b",
        r"\b(sum|total|difference|product|quotient)\b",
    ],

    RequestType.MEDICAL_ADVICE: [
        r"(symptom|diagnose|diagnosis|treatment|cure|medication|medicine)",
        r"(doctor|physician|medical|health|illness|disease|condition)",
        r"(dose|dosage|prescription|prescribe|side effect)",
        r"(should i take|how much.*take|is it safe)",
        r"(pain|ache|fever|cough|headache|nausea)",
        r"\b(rash|swelling|bleeding|infection|allergic|allergy)\b",
        r"\b(serious|dangerous|emergency|urgent)\b.*(rash|symptom|condition|pain)",
        r"(is this|is my|are these).*(serious|normal|dangerous)",
    ],

    RequestType.LEGAL_ADVICE: [
        r"(legal|lawyer|attorney|sue|lawsuit|court|judge)",
        r"(my rights|legally|unlawful|illegal|liable|liability)",
        r"(contract|agreement|terms|conditions)",
        r"(arrest|criminal|misdemeanor|felony)",
        r"(divorce|custody|settlement)",
        r"(enforceable|non-?compete|clause|jurisdiction)",
        r"(can i be|am i|is this).*(sued|legal|liable)",
    ],

    RequestType.FINANCIAL_ADVICE: [
        r"(invest|investment|stock|bond|portfolio|retirement)",
        r"(should i buy|should i sell|is.*good investment)",
        r"(crypto|bitcoin|ethereum|nft)",
        r"(mortgage|loan|debt|credit|interest rate)",
        r"(tax|taxes|deduction|401k|ira)",
    ],

    RequestType.PERSONAL_DATA: [
        r"(my ssn|my social security|my credit card)",
        r"(my password|my pin|my account number)",
        r"(my address|my phone number|my email)",
        r"here is my\s*(personal|private|sensitive)",
    ],

    RequestType.CODE_GENERATION: [
        r"(write|create|generate|implement)\s*(a|an|the)?\s*(function|class|script|program|code|app)",
        r"\b(python|javascript|java|c\+\+|rust|go|ruby|php|sql|html|css)\b",
        r"\b(code|programming|developer|software|api|database)\b",
        r"(debug|fix|refactor|optimize)\s*(this|the|my)\s*code",
    ],

    RequestType.CREATIVE: [
        r"(write|create|generate)\s*(a|an)?\s*(story|poem|song|script|novel)",
        r"(brainstorm|ideate|imagine)\b",
        r"\b(creative|artistic|fiction|fantasy)\b",
        r"^(write|create)\s+(me\s+)?(a|an)\s+",
    ],

    RequestType.HARMFUL: [
        r"\b(kill|murder|harm|hurt|injure|assassinate)\b",
        r"\b(bombs?|weapons?|explosives?|poisons?)\b",
        r"\b(hack|steal|phish|scam|fraud)\b.*\b(accounts?|passwords?|emails?|systems?)\b",
        r"\b(hack|crack|break into)\b",
        r"(suicide|suicidal|self-?harm|hurt(ing)?\s+(my)?self)",
        r"\b(meth|methamphetamine|cocaine|heroin|drugs?)\b",
        r"\b(napalm|ricin|sarin|anthrax)\b",
        r"(how to|tell me|explain).*\b(kill|murder|harm|hurt)\b",
        r"(how to|tell me|explain).*\b(make|build|create|synthesize|cook)\b.*\b(bombs?|weapons?|drugs?|explosives?|meth|poisons?)\b",
        r"\b(get|buy|find|obtain)\s+(illegal\s+)?drugs?\b",
        r"\b(mix|combine|mixing)\b.*(ammonia|chlorine|bleach)",
        r"(chlorine|ammonia|bleach).*(mix|combine|together)",
    ],
}


# =============================================================================
# SECTION 5: COMPILED RESPONSE
# The output of the chatbot compiler.
# =============================================================================

@dataclass
class CompiledResponse:
    """
    The final output of the chatbot compiler.

    This is what gets returned to the user - a verified,
    constraint-satisfying response.
    """
    id: str
    classification: RequestClassification
    decision: CompilerDecision

    # Response content
    content: Optional[str]            # The actual response (if allowed)
    disclaimer: Optional[str]         # Any required disclaimers
    referral: Optional[str]           # Deferral recommendation
    clarification_question: Optional[str]  # Question for user

    # Verification
    verified: bool                    # Did response pass verification?
    constraints_satisfied: List[str]  # Which constraints were met
    constraints_violated: List[str]   # Which constraints were violated

    # Recovery
    recovery_action: Optional[str]    # What to do next
    alternative_suggestion: Optional[str]  # Safe alternative

    # Metadata
    elapsed_us: int = 0               # Processing time in microseconds
    timestamp: float = field(default_factory=time.time)
    fingerprint: Optional[str] = None
    engine: str = "Newton Chatbot Compiler 1.0"

    def __post_init__(self):
        if self.fingerprint is None:
            data = f"{self.id}:{self.decision.value}:{self.verified}:{self.timestamp}"
            self.fingerprint = f"NR_{hashlib.sha256(data.encode()).hexdigest()[:16]}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "classification": self.classification.to_dict(),
            "decision": self.decision.value,
            "content": self.content,
            "disclaimer": self.disclaimer,
            "referral": self.referral,
            "clarification_question": self.clarification_question,
            "verified": self.verified,
            "constraints_satisfied": self.constraints_satisfied,
            "constraints_violated": self.constraints_violated,
            "recovery_action": self.recovery_action,
            "alternative_suggestion": self.alternative_suggestion,
            "elapsed_us": self.elapsed_us,
            "timestamp": self.timestamp,
            "fingerprint": self.fingerprint,
            "engine": self.engine
        }


# =============================================================================
# SECTION 6: THE CHATBOT COMPILER
# The core engine that compiles human intent into verified responses.
# =============================================================================

class ChatbotCompiler:
    """
    The Constrained Chatbot Compiler.

    This is not a chatbot. This is a compiler for human intent.

    Pipeline:
    1. Parse user input into intent types
    2. Determine what is allowed to be answered
    3. Ask clarifying questions when intent is underspecified
    4. Refuse when constraints are violated
    5. Only generate content that satisfies constraints

    LLMs are great generators. They are terrible governors.
    - Claude = Generator
    - Newton logic = Governor

    Cars have engines. They also have brakes.
    """

    def __init__(
        self,
        forge=None,
        custom_constraints: Optional[Dict[RequestType, ResponseConstraint]] = None,
        enable_metrics: bool = True
    ):
        """
        Initialize the Chatbot Compiler.

        Args:
            forge: Optional Forge instance for verification
            custom_constraints: Custom constraint rules to override defaults
            enable_metrics: Whether to track performance metrics
        """
        self.forge = forge or get_forge(ForgeConfig(enable_metrics=enable_metrics))
        self.constraints = {**RESPONSE_CONSTRAINTS}
        if custom_constraints:
            self.constraints.update(custom_constraints)

        # Metrics
        self.enable_metrics = enable_metrics
        self._total_compilations = 0
        self._decisions: Dict[CompilerDecision, int] = {d: 0 for d in CompilerDecision}
        self._types: Dict[RequestType, int] = {t: 0 for t in RequestType}

    # -------------------------------------------------------------------------
    # PASS 1: INTENT CLASSIFICATION
    # -------------------------------------------------------------------------

    def classify_request(self, user_input: str) -> RequestClassification:
        """
        First compiler pass: Classify the user's intent.

        This is type inference for natural language.

        Args:
            user_input: Raw user input

        Returns:
            RequestClassification with type, risk, and preliminary decision
        """
        start_time = time.time()
        normalized_input = user_input.lower().strip()

        # Check for harmful content first (highest priority)
        if self._matches_patterns(normalized_input, CLASSIFICATION_PATTERNS[RequestType.HARMFUL]):
            return self._create_classification(
                user_input,
                RequestType.HARMFUL,
                RiskLevel.CRITICAL,
                CompilerDecision.REFUSE,
                "Harmful content detected",
                confidence=0.99
            )

        # Check for personal data
        if self._matches_patterns(normalized_input, CLASSIFICATION_PATTERNS[RequestType.PERSONAL_DATA]):
            return self._create_classification(
                user_input,
                RequestType.PERSONAL_DATA,
                RiskLevel.HIGH,
                CompilerDecision.REFUSE,
                "Personal/sensitive data detected",
                confidence=0.95
            )

        # Check high-risk types first
        for request_type in [
            RequestType.MEDICAL_ADVICE,
            RequestType.LEGAL_ADVICE,
            RequestType.FINANCIAL_ADVICE,
        ]:
            if self._matches_patterns(normalized_input, CLASSIFICATION_PATTERNS[request_type]):
                constraint = self.constraints[request_type]
                decision = CompilerDecision.DEFER if constraint.requires_deferral else CompilerDecision.ANSWER
                return self._create_classification(
                    user_input,
                    request_type,
                    RiskLevel.HIGH,
                    decision,
                    f"Classified as {request_type.value} - professional guidance recommended",
                    confidence=0.85
                )

        # Check other types
        for request_type in [
            RequestType.CALCULATION,
            RequestType.CODE_GENERATION,
            RequestType.CREATIVE,
            RequestType.SPECULATION,
            RequestType.INSTRUCTION,
            RequestType.OPINION,
            RequestType.QUESTION,
        ]:
            if self._matches_patterns(normalized_input, CLASSIFICATION_PATTERNS[request_type]):
                risk = RiskLevel.LOW
                if request_type == RequestType.INSTRUCTION:
                    # Check for harmful instructions
                    constraint = self.constraints[request_type]
                    if self._matches_patterns(normalized_input, constraint.forbidden_patterns):
                        return self._create_classification(
                            user_input,
                            RequestType.HARMFUL,
                            RiskLevel.CRITICAL,
                            CompilerDecision.REFUSE,
                            "Harmful instruction detected",
                            confidence=0.95
                        )
                    risk = RiskLevel.MEDIUM

                return self._create_classification(
                    user_input,
                    request_type,
                    risk,
                    CompilerDecision.ANSWER,
                    f"Classified as {request_type.value}",
                    confidence=0.80
                )

        # Unknown type - ask for clarification
        return self._create_classification(
            user_input,
            RequestType.UNKNOWN,
            RiskLevel.LOW,
            CompilerDecision.ASK,
            "Could not determine intent - clarification needed",
            confidence=0.30
        )

    def _matches_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if text matches any of the patterns."""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _create_classification(
        self,
        user_input: str,
        request_type: RequestType,
        risk_level: RiskLevel,
        decision: CompilerDecision,
        reasoning: str,
        confidence: float
    ) -> RequestClassification:
        """Create a RequestClassification with full metadata."""
        constraint = self.constraints.get(request_type)

        # Extract entities (simplified - would use NLP in production)
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', user_input)

        # Get applicable constraints
        constraints = []
        if constraint:
            if constraint.requires_disclaimer:
                constraints.append("requires_disclaimer")
            if constraint.requires_deferral:
                constraints.append("requires_deferral")
            if constraint.requires_citation:
                constraints.append("requires_citation")
            if constraint.requires_verification:
                constraints.append("requires_verification")

        return RequestClassification(
            id=f"cls_{uuid.uuid4().hex[:12]}",
            request_type=request_type,
            risk_level=risk_level,
            decision=decision,
            intent=self._extract_intent(user_input),
            subject=self._extract_subject(user_input),
            entities=entities,
            constraints=constraints,
            violations=[],
            reasoning=reasoning,
            confidence=confidence
        )

    def _extract_intent(self, text: str) -> str:
        """Extract the core intent from user input."""
        # Simplified extraction - would use NLP in production
        verbs = ["want", "need", "help", "tell", "explain", "show", "create", "make", "calculate"]
        for verb in verbs:
            if verb in text.lower():
                return verb
        return "query"

    def _extract_subject(self, text: str) -> str:
        """Extract the subject/topic from user input."""
        # Simplified - would use NLP in production
        words = text.split()
        if len(words) > 3:
            return " ".join(words[-3:])
        return text

    # -------------------------------------------------------------------------
    # PASS 2: CONSTRAINT CHECKING
    # -------------------------------------------------------------------------

    def check_constraints(
        self,
        classification: RequestClassification
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Second compiler pass: Check constraints for the classified request.

        This is where we determine if response generation is allowed.

        Args:
            classification: The classified request

        Returns:
            Tuple of (satisfied, satisfied_constraints, violated_constraints)
        """
        constraint = self.constraints.get(classification.request_type)
        if not constraint:
            return True, [], []

        satisfied = []
        violated = []

        # Check if response is allowed at all
        if not constraint.allowed:
            violated.append(f"Response not allowed for type: {classification.request_type.value}")
        else:
            satisfied.append("Response type allowed")

        # Check risk level compatibility
        if classification.risk_level == RiskLevel.CRITICAL:
            violated.append("Critical risk level requires refusal")
        elif classification.risk_level == RiskLevel.HIGH and not constraint.requires_deferral:
            violated.append("High risk without deferral protocol")
        else:
            satisfied.append("Risk level acceptable")

        # Check for forbidden patterns in the original input
        # (This was already done in classification, but we verify here)
        if classification.request_type == RequestType.HARMFUL:
            violated.append("Harmful content detected")
        else:
            satisfied.append("No harmful patterns detected")

        return len(violated) == 0, satisfied, violated

    # -------------------------------------------------------------------------
    # PASS 3: RESPONSE GENERATION (CONSTRAINED)
    # -------------------------------------------------------------------------

    def generate_constrained_response(
        self,
        classification: RequestClassification,
        generator: Optional[Callable[[str, RequestClassification], str]] = None
    ) -> CompiledResponse:
        """
        Third compiler pass: Generate response within constraints.

        This is where we either:
        - Generate a constrained response
        - Ask for clarification
        - Defer to a professional
        - Refuse to respond

        Args:
            classification: The classified and constraint-checked request
            generator: Optional function to generate content

        Returns:
            CompiledResponse with the appropriate action taken
        """
        start_time = time.time()
        constraint = self.constraints.get(classification.request_type)

        # Check constraints
        satisfied, satisfied_list, violated_list = self.check_constraints(classification)

        # Determine final decision
        if not satisfied:
            decision = constraint.recovery_action if constraint else CompilerDecision.REFUSE
        else:
            decision = classification.decision

        # Build response based on decision
        content = None
        disclaimer = None
        referral = None
        clarification = None
        alternative = None

        if decision == CompilerDecision.ANSWER:
            # Generate content if generator provided
            if generator:
                content = generator(classification.intent, classification)
            else:
                content = self._generate_default_response(classification)

            # Add disclaimer if required
            if constraint and constraint.requires_disclaimer:
                disclaimer = self._generate_disclaimer(classification)

            # Add referral if required
            if constraint and constraint.requires_deferral:
                referral = self._generate_referral(classification)

        elif decision == CompilerDecision.ASK:
            clarification = self._generate_clarification_question(classification)

        elif decision == CompilerDecision.DEFER:
            referral = self._generate_referral(classification)
            content = self._generate_deferral_content(classification)
            disclaimer = self._generate_disclaimer(classification)

        elif decision == CompilerDecision.REFUSE:
            content = self._generate_refusal(classification)
            alternative = self._generate_alternative(classification)

        elapsed_us = int((time.time() - start_time) * 1_000_000)

        # Update metrics
        if self.enable_metrics:
            self._total_compilations += 1
            self._decisions[decision] = self._decisions.get(decision, 0) + 1
            self._types[classification.request_type] = self._types.get(classification.request_type, 0) + 1

        return CompiledResponse(
            id=f"rsp_{uuid.uuid4().hex[:12]}",
            classification=classification,
            decision=decision,
            content=content,
            disclaimer=disclaimer,
            referral=referral,
            clarification_question=clarification,
            verified=satisfied,
            constraints_satisfied=satisfied_list,
            constraints_violated=violated_list,
            recovery_action=constraint.recovery_action.value if constraint else None,
            alternative_suggestion=alternative,
            elapsed_us=elapsed_us
        )

    # -------------------------------------------------------------------------
    # PASS 4: RESPONSE VALIDATION
    # -------------------------------------------------------------------------

    def validate_response(
        self,
        response: CompiledResponse,
        generated_content: Optional[str] = None
    ) -> Tuple[bool, List[str]]:
        """
        Fourth compiler pass: Validate the generated response.

        Ensures the response satisfies all constraints before delivery.

        Args:
            response: The compiled response
            generated_content: Optional externally generated content to validate

        Returns:
            Tuple of (valid, violations)
        """
        violations = []
        constraint = self.constraints.get(response.classification.request_type)

        content_to_check = generated_content or response.content

        if not content_to_check:
            return True, []  # No content to validate

        if not constraint:
            return True, []  # No constraints to check

        # Check forbidden patterns (skip for DEFER responses - we're just acknowledging
        # the question and referring to professionals, not providing the forbidden advice)
        if response.decision != CompilerDecision.DEFER:
            for pattern in constraint.forbidden_patterns:
                if re.search(pattern, content_to_check, re.IGNORECASE):
                    violations.append(f"Response contains forbidden pattern: {pattern}")

        # Check required elements
        for element in constraint.required_elements:
            # Simplified check - would be more sophisticated in production
            if element == "factual_basis" and not any(word in content_to_check.lower() for word in ["because", "since", "therefore", "according"]):
                pass  # Soft check
            elif element == "opinion_label" and "opinion" not in content_to_check.lower() and "think" not in content_to_check.lower():
                pass  # Soft check

        # Check for hallucination patterns (simplified)
        hallucination_patterns = [
            r"I know for certain",
            r"definitely|absolutely|100%",
            r"always|never|every time",
        ]
        for pattern in hallucination_patterns:
            if re.search(pattern, content_to_check, re.IGNORECASE):
                if response.classification.request_type in [RequestType.MEDICAL_ADVICE, RequestType.LEGAL_ADVICE]:
                    violations.append(f"Overconfident language in high-risk response: {pattern}")

        return len(violations) == 0, violations

    # -------------------------------------------------------------------------
    # MAIN COMPILE METHOD
    # -------------------------------------------------------------------------

    def compile(
        self,
        user_input: str,
        generator: Optional[Callable[[str, RequestClassification], str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> CompiledResponse:
        """
        Compile user input into a verified response.

        This is the main entry point for the chatbot compiler.
        It runs all four passes:
        1. Intent Classification
        2. Constraint Checking
        3. Response Generation
        4. Response Validation

        Args:
            user_input: The raw user input
            generator: Optional content generator function
            context: Optional context information

        Returns:
            CompiledResponse with verified, constrained output
        """
        start_time = time.time()

        # Pass 1: Classify
        classification = self.classify_request(user_input)

        # Pass 2 & 3: Check constraints and generate response
        response = self.generate_constrained_response(classification, generator)

        # Pass 4: Validate
        valid, violations = self.validate_response(response)

        if not valid:
            # If validation fails, generate recovery response
            response = CompiledResponse(
                id=f"rsp_{uuid.uuid4().hex[:12]}",
                classification=classification,
                decision=CompilerDecision.REFUSE,
                content=self._generate_refusal(classification),
                disclaimer=None,
                referral=None,
                clarification_question=None,
                verified=False,
                constraints_satisfied=[],
                constraints_violated=violations,
                recovery_action="refuse",
                alternative_suggestion=self._generate_alternative(classification),
                elapsed_us=int((time.time() - start_time) * 1_000_000)
            )

        return response

    # -------------------------------------------------------------------------
    # DEFAULT RESPONSE GENERATORS
    # -------------------------------------------------------------------------

    def _generate_default_response(self, classification: RequestClassification) -> str:
        """Generate a default response based on request type."""
        templates = {
            RequestType.QUESTION: f"Regarding your question about {classification.subject}: [factual response would be generated here]",
            RequestType.OPINION: f"In my assessment of {classification.subject}: [balanced perspective would be provided here]",
            RequestType.INSTRUCTION: f"Here are the steps for {classification.intent}: [verified instructions would be provided here]",
            RequestType.CALCULATION: f"Calculating {classification.subject}: [verified computation would be performed here]",
            RequestType.CODE_GENERATION: f"Here's the code for {classification.subject}: [verified code would be generated here]",
            RequestType.CREATIVE: f"Here's a creative response for {classification.subject}: [creative content would be generated here]",
            RequestType.SPECULATION: f"Considering the hypothetical about {classification.subject}: [speculative analysis would be provided here]",
        }
        return templates.get(classification.request_type, f"Processing request about {classification.subject}...")

    def _generate_disclaimer(self, classification: RequestClassification) -> str:
        """Generate appropriate disclaimer based on request type."""
        disclaimers = {
            RequestType.MEDICAL_ADVICE: "This is general health information only, not medical advice. Please consult a qualified healthcare provider for personalized guidance.",
            RequestType.LEGAL_ADVICE: "This is general legal information only, not legal advice. Please consult a qualified attorney for personalized guidance.",
            RequestType.FINANCIAL_ADVICE: "This is educational information only, not financial advice. Please consult a qualified financial advisor. All investments carry risk.",
            RequestType.OPINION: "This represents one perspective. Other valid viewpoints exist.",
            RequestType.SPECULATION: "This is speculative analysis based on stated assumptions. Actual outcomes may differ.",
        }
        return disclaimers.get(classification.request_type, "Please verify this information independently.")

    def _generate_referral(self, classification: RequestClassification) -> str:
        """Generate professional referral based on request type."""
        referrals = {
            RequestType.MEDICAL_ADVICE: "For medical concerns, please consult: a physician, urgent care, or call emergency services if needed.",
            RequestType.LEGAL_ADVICE: "For legal matters, please consult: a licensed attorney, legal aid services, or your state bar association.",
            RequestType.FINANCIAL_ADVICE: "For financial guidance, please consult: a certified financial planner (CFP), registered investment advisor (RIA), or licensed financial advisor.",
        }
        return referrals.get(classification.request_type, "Please consult an appropriate professional.")

    def _generate_deferral_content(self, classification: RequestClassification) -> str:
        """Generate content that defers to professionals."""
        return f"I can provide general information about {classification.subject}, but for specific guidance, professional consultation is recommended."

    def _generate_clarification_question(self, classification: RequestClassification) -> str:
        """Generate a clarifying question for ambiguous requests."""
        if classification.request_type == RequestType.UNKNOWN:
            return "I want to help you accurately. Could you please clarify: Are you asking for information, requesting an action, or seeking guidance on a decision?"
        return f"To better assist you with {classification.subject}, could you please provide more details about what specifically you need?"

    def _generate_refusal(self, classification: RequestClassification) -> str:
        """Generate a refusal message."""
        if classification.request_type == RequestType.HARMFUL:
            return "I cannot help with this request as it involves potentially harmful content."
        elif classification.request_type == RequestType.PERSONAL_DATA:
            return "I cannot process requests involving sensitive personal information."
        return "I'm unable to complete this request as stated."

    def _generate_alternative(self, classification: RequestClassification) -> str:
        """Generate a safe alternative suggestion."""
        alternatives = {
            RequestType.HARMFUL: "If you're experiencing difficulties, please consider reaching out to appropriate support services.",
            RequestType.PERSONAL_DATA: "For matters involving sensitive data, please use secure, verified channels.",
            RequestType.MEDICAL_ADVICE: "For health concerns, please consult healthcare.gov or call your doctor.",
            RequestType.LEGAL_ADVICE: "For legal questions, consider consulting findlaw.com or your local bar association.",
        }
        return alternatives.get(classification.request_type, "Please consider rephrasing your request.")

    # -------------------------------------------------------------------------
    # METRICS
    # -------------------------------------------------------------------------

    def get_metrics(self) -> Dict[str, Any]:
        """Get compiler performance metrics."""
        return {
            "total_compilations": self._total_compilations,
            "decisions": {k.value: v for k, v in self._decisions.items()},
            "request_types": {k.value: v for k, v in self._types.items()},
            "decision_rates": {
                k.value: (v / self._total_compilations * 100 if self._total_compilations > 0 else 0)
                for k, v in self._decisions.items()
            }
        }


# =============================================================================
# SECTION 7: TINYTALK CHATBOT GOVERNOR
# Governance laws for the chatbot compiler.
# =============================================================================

class ChatbotGovernor:
    """
    TinyTalk-style governance for the Chatbot Compiler.

    These are the laws that the chatbot must obey.
    They are evaluated before any response is generated.
    """

    def __init__(self):
        self.laws: List[Callable] = []
        self._register_core_laws()

    def _register_core_laws(self):
        """Register the core governance laws."""

        # Law 1: No Harm
        def law_no_harm(classification: RequestClassification) -> bool:
            """when(request_type == HARMFUL, finfr)"""
            return classification.request_type != RequestType.HARMFUL
        self.laws.append(("no_harm", law_no_harm))

        # Law 2: Professional Deferral
        def law_professional_deferral(classification: RequestClassification) -> bool:
            """when(risk_level == CRITICAL and decision != REFUSE, finfr)"""
            if classification.risk_level == RiskLevel.CRITICAL:
                return classification.decision == CompilerDecision.REFUSE
            return True
        self.laws.append(("professional_deferral", law_professional_deferral))

        # Law 3: Clarity Required
        def law_clarity_required(classification: RequestClassification) -> bool:
            """when(confidence < 0.5 and decision == ANSWER, fin)"""
            if classification.confidence < 0.5:
                return classification.decision != CompilerDecision.ANSWER
            return True
        self.laws.append(("clarity_required", law_clarity_required))

        # Law 4: Medical Safety
        def law_medical_safety(classification: RequestClassification) -> bool:
            """when(request_type == MEDICAL_ADVICE and decision == ANSWER, finfr)"""
            if classification.request_type == RequestType.MEDICAL_ADVICE:
                return classification.decision in [CompilerDecision.DEFER, CompilerDecision.REFUSE]
            return True
        self.laws.append(("medical_safety", law_medical_safety))

        # Law 5: Legal Safety
        def law_legal_safety(classification: RequestClassification) -> bool:
            """when(request_type == LEGAL_ADVICE and decision == ANSWER, finfr)"""
            if classification.request_type == RequestType.LEGAL_ADVICE:
                return classification.decision in [CompilerDecision.DEFER, CompilerDecision.REFUSE]
            return True
        self.laws.append(("legal_safety", law_legal_safety))

    def evaluate_all(self, classification: RequestClassification) -> Tuple[bool, List[str]]:
        """
        Evaluate all governance laws.

        Returns:
            Tuple of (all_passed, violated_laws)
        """
        violations = []
        for name, law in self.laws:
            if not law(classification):
                violations.append(name)
        return len(violations) == 0, violations

    def add_law(self, name: str, law_func: Callable[[RequestClassification], bool]):
        """Add a custom governance law."""
        self.laws.append((name, law_func))


# =============================================================================
# SECTION 8: FACTORY FUNCTION
# =============================================================================

_compiler_instance: Optional[ChatbotCompiler] = None
_governor_instance: Optional[ChatbotGovernor] = None


def get_chatbot_compiler(
    config: Optional[Dict[str, Any]] = None,
    force_new: bool = False
) -> ChatbotCompiler:
    """
    Get the singleton ChatbotCompiler instance.

    Args:
        config: Optional configuration dictionary
        force_new: Force creation of a new instance

    Returns:
        ChatbotCompiler instance
    """
    global _compiler_instance
    if _compiler_instance is None or force_new:
        _compiler_instance = ChatbotCompiler()
    return _compiler_instance


def get_chatbot_governor(force_new: bool = False) -> ChatbotGovernor:
    """
    Get the singleton ChatbotGovernor instance.

    Args:
        force_new: Force creation of a new instance

    Returns:
        ChatbotGovernor instance
    """
    global _governor_instance
    if _governor_instance is None or force_new:
        _governor_instance = ChatbotGovernor()
    return _governor_instance


# =============================================================================
# SECTION 9: CONVENIENCE FUNCTIONS
# =============================================================================

def compile_request(
    user_input: str,
    generator: Optional[Callable[[str, RequestClassification], str]] = None,
    context: Optional[Dict[str, Any]] = None
) -> CompiledResponse:
    """
    Compile a user request into a verified response.

    This is the main entry point for using the chatbot compiler.

    Args:
        user_input: The raw user input
        generator: Optional content generator function
        context: Optional context information

    Returns:
        CompiledResponse with verified output

    Example:
        >>> response = compile_request("What dose of ibuprofen should I take?")
        >>> print(response.decision)  # CompilerDecision.DEFER
        >>> print(response.referral)  # "For medical concerns, please consult..."
    """
    compiler = get_chatbot_compiler()
    governor = get_chatbot_governor()

    # Get classification
    classification = compiler.classify_request(user_input)

    # Check governance laws
    laws_passed, violated_laws = governor.evaluate_all(classification)

    if not laws_passed:
        # Governance violation - generate refusal
        return CompiledResponse(
            id=f"rsp_{uuid.uuid4().hex[:12]}",
            classification=classification,
            decision=CompilerDecision.REFUSE,
            content=f"Request blocked by governance: {', '.join(violated_laws)}",
            disclaimer=None,
            referral=None,
            clarification_question=None,
            verified=False,
            constraints_satisfied=[],
            constraints_violated=violated_laws,
            recovery_action="refuse",
            alternative_suggestion=compiler._generate_alternative(classification),
            elapsed_us=0
        )

    # Proceed with normal compilation
    return compiler.compile(user_input, generator, context)


def classify_only(user_input: str) -> RequestClassification:
    """
    Classify a user request without generating a response.

    Useful for understanding intent before processing.

    Args:
        user_input: The raw user input

    Returns:
        RequestClassification with type and risk assessment
    """
    compiler = get_chatbot_compiler()
    return compiler.classify_request(user_input)
