"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON CARTRIDGES
Media Generation through Verified Specification

The Newton Cartridge system generates verified specifications for media content.
Every specification is constraint-checked before generation.
Every output is deterministic and auditable.

Cartridge Types:
- Visual: SVG/image specifications
- Sound: Audio specifications
- Sequence: Video/animation specifications
- Data: Report specifications
- Rosetta: Code generation prompts

"The specification IS the verification. The constraint IS the instruction."

© 2025-2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import re
import hashlib
import time


# ═══════════════════════════════════════════════════════════════════════════════
# CARTRIDGE TYPES
# ═══════════════════════════════════════════════════════════════════════════════

class CartridgeType(Enum):
    """Types of media cartridges."""
    VISUAL = "visual"
    SOUND = "sound"
    SEQUENCE = "sequence"
    DATA = "data"
    ROSETTA = "rosetta"


class OutputFormat(Enum):
    """Output format specifications."""
    # Visual
    SVG = "svg"
    PNG_SPEC = "png_spec"

    # Sound
    WAV_SPEC = "wav_spec"
    MP3_SPEC = "mp3_spec"

    # Sequence
    MP4_SPEC = "mp4_spec"
    GIF_SPEC = "gif_spec"

    # Data
    JSON = "json"
    CSV = "csv"
    MARKDOWN = "markdown"
    HTML = "html"

    # Rosetta
    SWIFT_PROMPT = "swift_prompt"
    PYTHON_PROMPT = "python_prompt"
    TYPESCRIPT_PROMPT = "typescript_prompt"


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRAINTS
# ═══════════════════════════════════════════════════════════════════════════════

# Content safety patterns (shared across all cartridges)
SAFETY_PATTERNS = {
    "harm": {
        "name": "No Harm",
        "patterns": [
            r"(how to )?(make|build|create|construct).*\b(bomb|weapon|explosive|poison)\b",
            r"(how to )?(kill|murder|harm|hurt|injure|assassinate)",
            r"(how to )?(suicide|self.harm)",
            r"\b(i want to|i need to|help me) (kill|murder|harm|hurt)",
        ]
    },
    "medical": {
        "name": "Medical Bounds",
        "patterns": [
            r"what (medication|drug|dosage|prescription) should (i|you) take",
            r"diagnose (my|this|the)",
            r"prescribe (me|a)",
        ]
    },
    "legal": {
        "name": "Legal Bounds",
        "patterns": [
            r"(how to )?(evade|avoid|cheat).*(tax|irs)",
            r"(how to )?(launder|hide|offshore) money",
            r"(how to )?(forge|fake|counterfeit)",
        ]
    },
    "security": {
        "name": "Security",
        "patterns": [
            r"(how to )?(hack|crack|break into|exploit|bypass)",
            r"\b(steal password|phishing|malware|ransomware)\b",
        ]
    }
}

# Visual-specific constraints
VISUAL_CONSTRAINTS = {
    "dimensions": {"min": 1, "max_width": 4096, "max_height": 4096},
    "elements": {"max_count": 1000},
    "colors": {"max_palette": 256},
    "patterns": [
        r"\b(offensive|inappropriate|explicit|nsfw)\b.*\b(image|graphic|visual)\b",
        r"\b(copy|steal|plagiarize)\b.*\b(logo|brand|trademark)\b",
        r"\b(deepfake|fake identity|impersonate)\b",
    ]
}

# Sound-specific constraints
SOUND_CONSTRAINTS = {
    "duration": {"min_ms": 1, "max_ms": 300000},  # 5 minutes max
    "frequency": {"min_hz": 1, "max_hz": 22050},
    "sample_rates": [22050, 44100, 48000, 96000],
    "patterns": [
        r"\b(subliminal|hidden)\b.*\b(message|audio)\b",
        r"\b(harmful|damaging|dangerous)\b.*\b(frequency|sound|tone)\b",
        r"\b(hypnotic|brainwash|mind control)\b",
    ]
}

# Sequence-specific constraints
SEQUENCE_CONSTRAINTS = {
    "duration": {"min_seconds": 0.1, "max_seconds": 600},  # 10 minutes max
    "fps": {"min": 1, "max": 120},
    "resolution": {"max_width": 7680, "max_height": 4320},  # 8K max
    "patterns": [
        r"\b(seizure|epilepsy)\b.*\b(inducing|triggering|cause)\b",
        r"\b(rapid|strobing)\b.*\b(flash|flicker|strobe)\b",
        r"\b(deepfake|fake identity)\b.*\b(video|footage)\b",
    ]
}

# Data-specific constraints
DATA_CONSTRAINTS = {
    "rows": {"max": 100000},
    "columns": {"max": 1000},
    "formats": ["json", "csv", "markdown", "html"],
    "patterns": [
        r"\b(fake|fabricate|falsify)\b.*\b(data|statistics|results|numbers)\b",
        r"\b(manipulate|skew|bias)\b.*\b(numbers|metrics|data)\b",
        r"\b(misleading|deceptive)\b.*\b(chart|graph|visualization)\b",
    ]
}

# Rosetta (code generation) constraints
ROSETTA_CONSTRAINTS = {
    "platforms": ["ios", "ipados", "macos", "watchos", "visionos", "tvos", "web", "android"],
    "patterns": [
        r"\b(malware|virus|trojan|backdoor|spyware)\b",
        r"\b(steal|exfiltrate)\b.*\b(data|credentials|passwords)\b",
        r"\b(bypass|disable)\b.*\b(security|authentication|encryption)\b",
        r"\b(keylogger|screen capture|spy)\b.*\b(without consent)\b",
    ],
    "app_store": [
        r"\b(gambling|casino|betting)\b.*\b(real money|cash)\b",
        r"\b(cryptocurrency|crypto)\b.*\b(mining)\b",
        r"\b(adult|explicit|nsfw)\b.*\b(content)\b",
    ]
}


# ═══════════════════════════════════════════════════════════════════════════════
# RESULT TYPES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ConstraintResult:
    """Result of constraint verification."""
    passed: bool
    constraint_name: str
    violations: List[str] = field(default_factory=list)
    message: str = ""


@dataclass
class CartridgeResult:
    """Result of cartridge compilation."""
    verified: bool
    cartridge_type: CartridgeType
    spec: Optional[Dict[str, Any]] = None
    constraints: Dict[str, Any] = field(default_factory=dict)
    fingerprint: str = ""
    elapsed_us: int = 0
    timestamp: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "verified": self.verified,
            "cartridge_type": self.cartridge_type.value,
            "spec": self.spec,
            "constraints": self.constraints,
            "fingerprint": self.fingerprint,
            "elapsed_us": self.elapsed_us,
            "timestamp": self.timestamp
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRAINT CHECKER
# ═══════════════════════════════════════════════════════════════════════════════

class ConstraintChecker:
    """Verifies content against safety and cartridge-specific constraints."""

    @staticmethod
    def check_safety(text: str, categories: Optional[List[str]] = None) -> ConstraintResult:
        """Check text against safety patterns."""
        text_lower = text.lower()
        categories = categories or list(SAFETY_PATTERNS.keys())
        violations = []

        for category in categories:
            if category not in SAFETY_PATTERNS:
                continue

            constraint = SAFETY_PATTERNS[category]
            for pattern in constraint["patterns"]:
                if re.search(pattern, text_lower):
                    violations.append(f"{constraint['name']}: {pattern}")
                    break

        return ConstraintResult(
            passed=len(violations) == 0,
            constraint_name="safety",
            violations=violations,
            message="Safety check passed" if not violations else f"Safety violations: {len(violations)}"
        )

    @staticmethod
    def check_patterns(text: str, patterns: List[str], constraint_name: str) -> ConstraintResult:
        """Check text against a list of patterns."""
        text_lower = text.lower()
        violations = []

        for pattern in patterns:
            if re.search(pattern, text_lower):
                violations.append(pattern)

        return ConstraintResult(
            passed=len(violations) == 0,
            constraint_name=constraint_name,
            violations=violations,
            message=f"{constraint_name} check passed" if not violations else f"{constraint_name} violations: {len(violations)}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# VISUAL CARTRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class VisualSpec:
    """Specification for visual content."""
    width: int = 800
    height: int = 600
    max_elements: int = 100
    color_palette: Optional[List[str]] = None


class VisualCartridge:
    """
    Visual Cartridge: SVG/Image Specification Generator

    Generates verified specifications for visual content with:
    - Dimension constraints (max 4096x4096)
    - Element count limits (max 1000)
    - Color palette bounds (max 256 colors)
    - Content safety verification
    """

    ELEMENT_PATTERNS = {
        "circle": r"\b(circle|dot|point|round|sphere|orb)\b",
        "rect": r"\b(rectangle|square|box|card|panel|frame)\b",
        "line": r"\b(line|stroke|path|border|edge|rule)\b",
        "text": r"\b(text|label|title|heading|caption|paragraph)\b",
        "polygon": r"\b(triangle|polygon|shape|star|hexagon)\b",
        "ellipse": r"\b(ellipse|oval|egg)\b",
        "path": r"\b(curve|bezier|arc|wave)\b",
        "image": r"\b(image|picture|photo|icon|logo)\b",
        "gradient": r"\b(gradient|fade|blend|transition)\b",
    }

    STYLE_PATTERNS = {
        "minimal": r"\b(minimal|minimalist|simple|clean|sparse)\b",
        "detailed": r"\b(detailed|complex|intricate|ornate)\b",
        "modern": r"\b(modern|contemporary|sleek|flat)\b",
        "retro": r"\b(retro|vintage|classic|old school)\b",
        "organic": r"\b(organic|natural|flowing|fluid)\b",
        "geometric": r"\b(geometric|angular|sharp|structured)\b",
    }

    COLOR_PATTERNS = {
        "monochrome": r"\b(monochrome|black and white|grayscale|single color)\b",
        "vibrant": r"\b(vibrant|colorful|bright|saturated)\b",
        "pastel": r"\b(pastel|soft|muted|light)\b",
        "dark": r"\b(dark|deep|rich|bold)\b",
        "warm": r"\b(warm|orange|red|yellow|sunset)\b",
        "cool": r"\b(cool|blue|green|teal|ocean)\b",
    }

    def compile(
        self,
        intent: str,
        width: int = 800,
        height: int = 600,
        max_elements: int = 100,
        color_palette: Optional[List[str]] = None
    ) -> CartridgeResult:
        """Compile visual intent into SVG specification."""
        start_us = time.perf_counter_ns() // 1000

        # Clamp dimensions
        width = max(1, min(width, VISUAL_CONSTRAINTS["dimensions"]["max_width"]))
        height = max(1, min(height, VISUAL_CONSTRAINTS["dimensions"]["max_height"]))
        max_elements = min(max_elements, VISUAL_CONSTRAINTS["elements"]["max_count"])

        # Limit color palette
        if color_palette and len(color_palette) > VISUAL_CONSTRAINTS["colors"]["max_palette"]:
            color_palette = color_palette[:VISUAL_CONSTRAINTS["colors"]["max_palette"]]

        # Check constraints
        safety_check = ConstraintChecker.check_safety(intent)
        visual_check = ConstraintChecker.check_patterns(
            intent, VISUAL_CONSTRAINTS["patterns"], "visual"
        )

        verified = safety_check.passed and visual_check.passed

        spec = None
        if verified:
            # Parse visual elements from intent
            elements = self._parse_elements(intent)
            style = self._parse_style(intent)
            color_scheme = self._parse_colors(intent)

            spec = {
                "type": "svg",
                "format": OutputFormat.SVG.value,
                "viewBox": f"0 0 {width} {height}",
                "width": width,
                "height": height,
                "elements": elements[:max_elements],
                "element_count": len(elements[:max_elements]),
                "style": {
                    "theme": style,
                    "background": "#ffffff",
                    "stroke": "#000000",
                    "fill": "#e0e0e0",
                    "stroke_width": 2,
                    "color_scheme": color_scheme
                },
                "palette": color_palette or self._generate_palette(color_scheme),
                "intent_hash": hashlib.sha256(intent.encode()).hexdigest()[:16].upper()
            }

        elapsed_us = (time.perf_counter_ns() // 1000) - start_us

        return CartridgeResult(
            verified=verified,
            cartridge_type=CartridgeType.VISUAL,
            spec=spec,
            constraints={
                "safety": {"passed": safety_check.passed, "violations": safety_check.violations},
                "visual": {"passed": visual_check.passed, "violations": visual_check.violations},
                "bounds": {"width": width, "height": height, "max_elements": max_elements}
            },
            fingerprint=hashlib.sha256(f"{intent}{width}{height}".encode()).hexdigest()[:12].upper(),
            elapsed_us=elapsed_us,
            timestamp=int(time.time() * 1000)
        )

    def _parse_elements(self, intent: str) -> List[str]:
        """Parse visual elements from intent."""
        intent_lower = intent.lower()
        elements = []

        for elem_type, pattern in self.ELEMENT_PATTERNS.items():
            if re.search(pattern, intent_lower):
                elements.append(elem_type)

        return elements if elements else ["rect", "text"]

    def _parse_style(self, intent: str) -> str:
        """Parse visual style from intent."""
        intent_lower = intent.lower()

        for style, pattern in self.STYLE_PATTERNS.items():
            if re.search(pattern, intent_lower):
                return style

        return "modern"

    def _parse_colors(self, intent: str) -> str:
        """Parse color scheme from intent."""
        intent_lower = intent.lower()

        for scheme, pattern in self.COLOR_PATTERNS.items():
            if re.search(pattern, intent_lower):
                return scheme

        return "vibrant"

    def _generate_palette(self, scheme: str) -> List[str]:
        """Generate a color palette based on scheme."""
        palettes = {
            "monochrome": ["#000000", "#333333", "#666666", "#999999", "#CCCCCC", "#FFFFFF"],
            "vibrant": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD"],
            "pastel": ["#FFB3BA", "#BAFFC9", "#BAE1FF", "#FFFFBA", "#FFDfBA", "#E0BBE4"],
            "dark": ["#1A1A2E", "#16213E", "#0F3460", "#533483", "#E94560", "#000000"],
            "warm": ["#FF6B35", "#F7C59F", "#EFEFD0", "#004E89", "#1A659E", "#FF9F1C"],
            "cool": ["#0077B6", "#00B4D8", "#90E0EF", "#CAF0F8", "#03045E", "#023E8A"],
        }
        return palettes.get(scheme, palettes["vibrant"])


# ═══════════════════════════════════════════════════════════════════════════════
# SOUND CARTRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

class SoundCartridge:
    """
    Sound Cartridge: Audio Specification Generator

    Generates verified specifications for audio content with:
    - Duration limits (max 5 minutes)
    - Frequency bounds (1 Hz - 22050 Hz)
    - Sample rate validation
    - Content safety verification
    """

    SOUND_PATTERNS = {
        "tone": r"\b(tone|beep|note|pitch|sine|pure)\b",
        "melody": r"\b(melody|tune|music|song|jingle)\b",
        "effect": r"\b(effect|sfx|sound|noise|whoosh|click)\b",
        "voice": r"\b(voice|speech|spoken|narration|vocal)\b",
        "ambient": r"\b(ambient|background|atmosphere|environment|nature)\b",
        "beat": r"\b(beat|drum|rhythm|percussion|tempo)\b",
        "chord": r"\b(chord|harmony|polyphonic)\b",
    }

    MOOD_PATTERNS = {
        "upbeat": r"\b(upbeat|happy|cheerful|energetic|lively)\b",
        "calm": r"\b(calm|relaxing|peaceful|serene|gentle)\b",
        "dramatic": r"\b(dramatic|intense|powerful|epic|cinematic)\b",
        "mysterious": r"\b(mysterious|eerie|suspense|dark|ominous)\b",
        "playful": r"\b(playful|fun|whimsical|bouncy|quirky)\b",
    }

    def compile(
        self,
        intent: str,
        duration_ms: int = 5000,
        min_frequency: float = 20.0,
        max_frequency: float = 20000.0,
        sample_rate: int = 44100
    ) -> CartridgeResult:
        """Compile sound intent into audio specification."""
        start_us = time.perf_counter_ns() // 1000

        # Clamp parameters
        duration_ms = max(
            SOUND_CONSTRAINTS["duration"]["min_ms"],
            min(duration_ms, SOUND_CONSTRAINTS["duration"]["max_ms"])
        )
        min_frequency = max(min_frequency, SOUND_CONSTRAINTS["frequency"]["min_hz"])
        max_frequency = min(max_frequency, SOUND_CONSTRAINTS["frequency"]["max_hz"])

        if sample_rate not in SOUND_CONSTRAINTS["sample_rates"]:
            sample_rate = 44100

        # Check constraints
        safety_check = ConstraintChecker.check_safety(intent)
        sound_check = ConstraintChecker.check_patterns(
            intent, SOUND_CONSTRAINTS["patterns"], "sound"
        )

        verified = safety_check.passed and sound_check.passed

        spec = None
        if verified:
            # Parse sound characteristics
            sound_types = self._parse_sound_types(intent)
            mood = self._parse_mood(intent)

            spec = {
                "type": "audio",
                "format": OutputFormat.WAV_SPEC.value,
                "duration_ms": duration_ms,
                "duration_seconds": round(duration_ms / 1000, 2),
                "sample_rate": sample_rate,
                "bit_depth": 16,
                "channels": 2,
                "frequency_range": {
                    "min_hz": min_frequency,
                    "max_hz": max_frequency
                },
                "sound_types": sound_types,
                "mood": mood,
                "waveforms": self._suggest_waveforms(sound_types),
                "intent_hash": hashlib.sha256(intent.encode()).hexdigest()[:16].upper()
            }

        elapsed_us = (time.perf_counter_ns() // 1000) - start_us

        return CartridgeResult(
            verified=verified,
            cartridge_type=CartridgeType.SOUND,
            spec=spec,
            constraints={
                "safety": {"passed": safety_check.passed, "violations": safety_check.violations},
                "sound": {"passed": sound_check.passed, "violations": sound_check.violations},
                "bounds": {
                    "duration_ms": duration_ms,
                    "frequency_range": [min_frequency, max_frequency],
                    "sample_rate": sample_rate
                }
            },
            fingerprint=hashlib.sha256(f"{intent}{duration_ms}{sample_rate}".encode()).hexdigest()[:12].upper(),
            elapsed_us=elapsed_us,
            timestamp=int(time.time() * 1000)
        )

    def _parse_sound_types(self, intent: str) -> List[str]:
        """Parse sound types from intent."""
        intent_lower = intent.lower()
        types = []

        for sound_type, pattern in self.SOUND_PATTERNS.items():
            if re.search(pattern, intent_lower):
                types.append(sound_type)

        return types if types else ["tone"]

    def _parse_mood(self, intent: str) -> str:
        """Parse mood from intent."""
        intent_lower = intent.lower()

        for mood, pattern in self.MOOD_PATTERNS.items():
            if re.search(pattern, intent_lower):
                return mood

        return "neutral"

    def _suggest_waveforms(self, sound_types: List[str]) -> List[str]:
        """Suggest waveforms based on sound types."""
        waveform_map = {
            "tone": ["sine"],
            "melody": ["sine", "triangle"],
            "effect": ["sawtooth", "noise"],
            "voice": ["complex"],
            "ambient": ["noise", "sine"],
            "beat": ["square", "noise"],
            "chord": ["sine", "triangle"],
        }

        waveforms = set()
        for sound_type in sound_types:
            waveforms.update(waveform_map.get(sound_type, ["sine"]))

        return list(waveforms)


# ═══════════════════════════════════════════════════════════════════════════════
# SEQUENCE CARTRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

class SequenceCartridge:
    """
    Sequence Cartridge: Video/Animation Specification Generator

    Generates verified specifications for video content with:
    - Duration limits (max 10 minutes)
    - Frame rate bounds (1-120 fps)
    - Resolution limits (max 8K)
    - Safety verification (no seizure-inducing content)
    """

    SEQUENCE_TYPES = {
        "video": r"\b(video|film|movie|clip|footage)\b",
        "animation": r"\b(animation|animated|motion graphics|animate)\b",
        "slideshow": r"\b(slideshow|presentation|slides|carousel)\b",
        "timelapse": r"\b(timelapse|time-lapse|sped up)\b",
        "loop": r"\b(loop|looping|seamless|repeating)\b",
    }

    TRANSITION_PATTERNS = {
        "fade": r"\b(fade|dissolve|crossfade)\b",
        "cut": r"\b(cut|hard cut|jump)\b",
        "wipe": r"\b(wipe|slide|push)\b",
        "zoom": r"\b(zoom|scale|punch in)\b",
        "rotate": r"\b(rotate|spin|turn)\b",
    }

    def compile(
        self,
        intent: str,
        duration_seconds: float = 30.0,
        fps: int = 30,
        width: int = 1920,
        height: int = 1080,
        max_scenes: int = 10
    ) -> CartridgeResult:
        """Compile sequence intent into video specification."""
        start_us = time.perf_counter_ns() // 1000

        # Clamp parameters
        duration_seconds = max(
            SEQUENCE_CONSTRAINTS["duration"]["min_seconds"],
            min(duration_seconds, SEQUENCE_CONSTRAINTS["duration"]["max_seconds"])
        )
        fps = max(SEQUENCE_CONSTRAINTS["fps"]["min"], min(fps, SEQUENCE_CONSTRAINTS["fps"]["max"]))
        width = min(width, SEQUENCE_CONSTRAINTS["resolution"]["max_width"])
        height = min(height, SEQUENCE_CONSTRAINTS["resolution"]["max_height"])
        max_scenes = min(max_scenes, 100)

        # Check constraints
        safety_check = ConstraintChecker.check_safety(intent)
        sequence_check = ConstraintChecker.check_patterns(
            intent, SEQUENCE_CONSTRAINTS["patterns"], "sequence"
        )

        verified = safety_check.passed and sequence_check.passed

        spec = None
        if verified:
            # Parse sequence type and transitions
            sequence_type = self._parse_sequence_type(intent)
            transitions = self._parse_transitions(intent)
            total_frames = int(duration_seconds * fps)

            spec = {
                "type": sequence_type,
                "format": OutputFormat.MP4_SPEC.value,
                "duration_seconds": duration_seconds,
                "fps": fps,
                "total_frames": total_frames,
                "resolution": {
                    "width": width,
                    "height": height,
                    "aspect_ratio": f"{width}:{height}"
                },
                "max_scenes": max_scenes,
                "transitions": transitions,
                "codec": "h264",
                "container": "mp4",
                "bitrate_suggestion": self._suggest_bitrate(width, height, fps),
                "keyframe_interval": fps * 2,  # Keyframe every 2 seconds
                "intent_hash": hashlib.sha256(intent.encode()).hexdigest()[:16].upper()
            }

        elapsed_us = (time.perf_counter_ns() // 1000) - start_us

        return CartridgeResult(
            verified=verified,
            cartridge_type=CartridgeType.SEQUENCE,
            spec=spec,
            constraints={
                "safety": {"passed": safety_check.passed, "violations": safety_check.violations},
                "sequence": {"passed": sequence_check.passed, "violations": sequence_check.violations},
                "bounds": {
                    "duration_seconds": duration_seconds,
                    "fps": fps,
                    "resolution": f"{width}x{height}",
                    "max_scenes": max_scenes
                }
            },
            fingerprint=hashlib.sha256(f"{intent}{duration_seconds}{fps}{width}".encode()).hexdigest()[:12].upper(),
            elapsed_us=elapsed_us,
            timestamp=int(time.time() * 1000)
        )

    def _parse_sequence_type(self, intent: str) -> str:
        """Parse sequence type from intent."""
        intent_lower = intent.lower()

        for seq_type, pattern in self.SEQUENCE_TYPES.items():
            if re.search(pattern, intent_lower):
                return seq_type

        return "animation"

    def _parse_transitions(self, intent: str) -> List[str]:
        """Parse transitions from intent."""
        intent_lower = intent.lower()
        transitions = []

        for transition, pattern in self.TRANSITION_PATTERNS.items():
            if re.search(pattern, intent_lower):
                transitions.append(transition)

        return transitions if transitions else ["cut"]

    def _suggest_bitrate(self, width: int, height: int, fps: int) -> str:
        """Suggest bitrate based on resolution and fps."""
        pixels = width * height

        if pixels >= 3840 * 2160:  # 4K+
            base = 35000
        elif pixels >= 1920 * 1080:  # 1080p
            base = 8000
        elif pixels >= 1280 * 720:  # 720p
            base = 5000
        else:
            base = 2500

        # Adjust for high frame rate
        if fps > 30:
            base = int(base * 1.5)

        return f"{base}kbps"


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CARTRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

class DataCartridge:
    """
    Data Cartridge: Report/Data Specification Generator

    Generates verified specifications for data reports with:
    - Row limits (max 100,000)
    - Format validation (JSON, CSV, Markdown, HTML)
    - Statistical analysis
    - Content safety verification
    """

    REPORT_PATTERNS = {
        "financial": r"\b(financial|revenue|profit|expense|budget|balance|income)\b",
        "analytics": r"\b(analytics|metrics|kpi|performance|conversion)\b",
        "summary": r"\b(summary|overview|report|digest|recap)\b",
        "comparison": r"\b(comparison|compare|versus|vs|benchmark)\b",
        "trend": r"\b(trend|growth|change|over time|historical)\b",
        "inventory": r"\b(inventory|stock|supply|warehouse)\b",
        "user": r"\b(user|customer|audience|demographic)\b",
    }

    VISUALIZATION_PATTERNS = {
        "chart": r"\b(chart|graph|plot)\b",
        "bar": r"\b(bar chart|bar graph|histogram)\b",
        "line": r"\b(line chart|line graph|trend line)\b",
        "pie": r"\b(pie chart|donut|proportion)\b",
        "table": r"\b(table|grid|spreadsheet)\b",
        "heatmap": r"\b(heatmap|heat map|density)\b",
    }

    def compile(
        self,
        intent: str,
        data: Optional[Dict[str, Any]] = None,
        output_format: str = "json",
        max_rows: int = 1000,
        include_statistics: bool = True
    ) -> CartridgeResult:
        """Compile data intent into report specification."""
        start_us = time.perf_counter_ns() // 1000

        # Validate format
        if output_format not in DATA_CONSTRAINTS["formats"]:
            output_format = "json"

        # Clamp rows
        max_rows = min(max_rows, DATA_CONSTRAINTS["rows"]["max"])

        # Check constraints
        safety_check = ConstraintChecker.check_safety(intent)
        data_check = ConstraintChecker.check_patterns(
            intent, DATA_CONSTRAINTS["patterns"], "data"
        )

        verified = safety_check.passed and data_check.passed

        spec = None
        if verified:
            # Parse report type and visualizations
            report_type = self._parse_report_type(intent)
            visualizations = self._parse_visualizations(intent)

            spec = {
                "type": "report",
                "report_type": report_type,
                "format": output_format,
                "max_rows": max_rows,
                "include_statistics": include_statistics,
                "sections": ["header", "summary", "data", "visualizations", "footer"],
                "visualizations": visualizations,
                "data_provided": data is not None,
                "intent_hash": hashlib.sha256(intent.encode()).hexdigest()[:16].upper()
            }

            # Calculate statistics if data provided
            if include_statistics and data:
                spec["statistics"] = self._calculate_statistics(data)

        elapsed_us = (time.perf_counter_ns() // 1000) - start_us

        return CartridgeResult(
            verified=verified,
            cartridge_type=CartridgeType.DATA,
            spec=spec,
            constraints={
                "safety": {"passed": safety_check.passed, "violations": safety_check.violations},
                "data": {"passed": data_check.passed, "violations": data_check.violations},
                "bounds": {"max_rows": max_rows, "format": output_format}
            },
            fingerprint=hashlib.sha256(f"{intent}{output_format}{max_rows}".encode()).hexdigest()[:12].upper(),
            elapsed_us=elapsed_us,
            timestamp=int(time.time() * 1000)
        )

    def _parse_report_type(self, intent: str) -> str:
        """Parse report type from intent."""
        intent_lower = intent.lower()

        for report_type, pattern in self.REPORT_PATTERNS.items():
            if re.search(pattern, intent_lower):
                return report_type

        return "general"

    def _parse_visualizations(self, intent: str) -> List[str]:
        """Parse visualization types from intent."""
        intent_lower = intent.lower()
        visualizations = []

        for viz_type, pattern in self.VISUALIZATION_PATTERNS.items():
            if re.search(pattern, intent_lower):
                visualizations.append(viz_type)

        return visualizations if visualizations else ["table"]

    def _calculate_statistics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate basic statistics from data."""
        numeric_values = []

        for value in data.values():
            if isinstance(value, (int, float)):
                numeric_values.append(value)
            elif isinstance(value, list):
                numeric_values.extend([x for x in value if isinstance(x, (int, float))])

        if not numeric_values:
            return {"message": "No numeric data found"}

        n = len(numeric_values)
        total = sum(numeric_values)
        sorted_values = sorted(numeric_values)

        return {
            "count": n,
            "sum": round(total, 4),
            "mean": round(total / n, 4),
            "min": round(min(numeric_values), 4),
            "max": round(max(numeric_values), 4),
            "median": round(sorted_values[n // 2], 4) if n % 2 == 1 else round((sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2, 4),
            "range": round(max(numeric_values) - min(numeric_values), 4)
        }


# ═══════════════════════════════════════════════════════════════════════════════
# ROSETTA COMPILER
# ═══════════════════════════════════════════════════════════════════════════════

class RosettaCompiler:
    """
    Rosetta Compiler: Code Generation Prompt Generator

    Compiles natural language app descriptions into structured prompts
    for code generation systems (Swift, Python, TypeScript).

    Verifies against:
    - Security constraints (no malware)
    - App Store guidelines
    - Platform-specific requirements
    """

    PLATFORM_PATTERNS = {
        "ios": r"\b(iphone|ios|mobile app)\b",
        "ipados": r"\b(ipad|ipados|tablet)\b",
        "macos": r"\b(mac|macos|desktop)\b",
        "watchos": r"\b(watch|watchos|wearable)\b",
        "visionos": r"\b(vision|visionos|spatial|ar app)\b",
        "tvos": r"\b(tv|tvos|apple tv)\b",
        "web": r"\b(web|website|browser|react|vue|angular)\b",
        "android": r"\b(android|kotlin|java mobile)\b",
    }

    COMPONENT_PATTERNS = {
        "list": r"\b(list|table|collection|feed|timeline)\b",
        "form": r"\b(form|input|settings|preferences|profile)\b",
        "detail": r"\b(detail|view|show|display|page)\b",
        "navigation": r"\b(tab|menu|sidebar|drawer|navigation)\b",
        "map": r"\b(map|location|directions|places)\b",
        "media": r"\b(photo|video|camera|gallery|player)\b",
        "chart": r"\b(chart|graph|analytics|statistics|dashboard)\b",
        "auth": r"\b(login|signup|auth|register|account)\b",
        "chat": r"\b(chat|message|conversation|inbox)\b",
        "search": r"\b(search|filter|find|browse)\b",
    }

    APP_TYPE_PATTERNS = {
        "utility": r"\b(utility|tool|calculator|converter|timer)\b",
        "social": r"\b(social|community|share|friends|followers)\b",
        "productivity": r"\b(productivity|task|todo|notes|calendar)\b",
        "media": r"\b(photo|video|music|podcast|streaming)\b",
        "health": r"\b(health|fitness|wellness|meditation|sleep)\b",
        "finance": r"\b(finance|budget|expense|investment|banking)\b",
        "education": r"\b(education|learn|study|course|quiz)\b",
        "lifestyle": r"\b(lifestyle|recipe|travel|weather|news)\b",
        "game": r"\b(game|play|puzzle|arcade|trivia)\b",
    }

    FRAMEWORK_KEYWORDS = {
        "health": ["HealthKit", "HealthKitUI"],
        "location": ["CoreLocation", "MapKit"],
        "media": ["AVFoundation", "PhotosUI", "MusicKit"],
        "ml": ["CoreML", "Vision", "NaturalLanguage"],
        "ar": ["ARKit", "RealityKit"],
        "payments": ["StoreKit", "PassKit"],
        "notifications": ["UserNotifications"],
        "auth": ["AuthenticationServices", "LocalAuthentication"],
        "data": ["CoreData", "SwiftData", "CloudKit"],
    }

    def compile(
        self,
        intent: str,
        target_platform: str = "ios",
        version: str = "18.0",
        language: str = "swift"
    ) -> CartridgeResult:
        """Compile app intent into code generation prompt."""
        start_us = time.perf_counter_ns() // 1000

        # Validate platform
        target_platform = target_platform.lower()
        if target_platform not in ROSETTA_CONSTRAINTS["platforms"]:
            target_platform = "ios"

        # Check constraints
        safety_check = ConstraintChecker.check_safety(intent)
        rosetta_check = ConstraintChecker.check_patterns(
            intent, ROSETTA_CONSTRAINTS["patterns"], "security"
        )
        app_store_check = ConstraintChecker.check_patterns(
            intent, ROSETTA_CONSTRAINTS["app_store"], "app_store"
        )

        verified = safety_check.passed and rosetta_check.passed and app_store_check.passed

        spec = None
        if verified:
            # Parse app structure
            parsed = self._parse_intent(intent)
            parsed["platform"] = target_platform
            parsed["version"] = version

            # Generate prompt
            prompt = self._generate_prompt(intent, parsed, language)

            spec = {
                "type": "code_prompt",
                "format": self._get_output_format(language),
                "platform": target_platform,
                "version": version,
                "language": language,
                "parsed": parsed,
                "prompt": prompt,
                "frameworks": parsed["frameworks"],
                "components": parsed["components"],
                "app_type": parsed["app_type"],
                "warnings": self._get_warnings(intent),
                "intent_hash": hashlib.sha256(intent.encode()).hexdigest()[:16].upper()
            }

        elapsed_us = (time.perf_counter_ns() // 1000) - start_us

        return CartridgeResult(
            verified=verified,
            cartridge_type=CartridgeType.ROSETTA,
            spec=spec,
            constraints={
                "safety": {"passed": safety_check.passed, "violations": safety_check.violations},
                "security": {"passed": rosetta_check.passed, "violations": rosetta_check.violations},
                "app_store": {"passed": app_store_check.passed, "violations": app_store_check.violations}
            },
            fingerprint=hashlib.sha256(f"{intent}{target_platform}{language}".encode()).hexdigest()[:12].upper(),
            elapsed_us=elapsed_us,
            timestamp=int(time.time() * 1000)
        )

    def _parse_intent(self, intent: str) -> Dict[str, Any]:
        """Parse app intent into structured components."""
        intent_lower = intent.lower()

        # Detect platform
        platform = "ios"
        for plat, pattern in self.PLATFORM_PATTERNS.items():
            if re.search(pattern, intent_lower):
                platform = plat
                break

        # Detect components
        components = []
        for component, pattern in self.COMPONENT_PATTERNS.items():
            if re.search(pattern, intent_lower):
                components.append(component)

        if not components:
            components = ["list", "detail"]

        # Detect app type
        app_type = "utility"
        for atype, pattern in self.APP_TYPE_PATTERNS.items():
            if re.search(pattern, intent_lower):
                app_type = atype
                break

        # Detect frameworks
        frameworks = ["SwiftUI"]
        framework_keywords = {
            "health": r"\b(health|fitness|workout|steps|heart rate)\b",
            "location": r"\b(map|location|gps|directions|nearby)\b",
            "media": r"\b(photo|video|camera|music|audio)\b",
            "ml": r"\b(ml|ai|recognize|detect|classify|predict)\b",
            "ar": r"\b(ar|augmented|3d|spatial)\b",
            "payments": r"\b(payment|purchase|subscription|in-app)\b",
            "notifications": r"\b(notification|reminder|alert|push)\b",
            "auth": r"\b(login|auth|face id|touch id|biometric)\b",
            "data": r"\b(save|store|sync|cloud|database)\b",
        }

        for category, pattern in framework_keywords.items():
            if re.search(pattern, intent_lower):
                frameworks.extend(self.FRAMEWORK_KEYWORDS.get(category, []))

        # Remove duplicates while preserving order
        frameworks = list(dict.fromkeys(frameworks))

        return {
            "platform": platform,
            "app_type": app_type,
            "components": components,
            "frameworks": frameworks,
            "tokens": len(intent.split())
        }

    def _generate_prompt(self, intent: str, parsed: Dict[str, Any], language: str) -> str:
        """Generate structured code generation prompt."""

        component_specs = "\n".join(f"{i+1}. {comp.title()}View" for i, comp in enumerate(parsed["components"]))
        framework_list = "\n".join(f"- {fw}" for fw in parsed["frameworks"])

        if language == "swift":
            return f"""TARGET: {parsed['platform'].upper()} {parsed['version']}
FRAMEWORK: {parsed['frameworks'][0]}
APP_TYPE: {parsed['app_type']}
DATE: {time.strftime('%Y-%m-%d')}

REQUIREMENTS:
{intent}

ARCHITECTURE:
- Pattern: MVVM
- State: @Observable (iOS 17+) or ObservableObject
- Navigation: NavigationStack

FRAMEWORKS_REQUIRED:
{framework_list}

SCREENS:
{component_specs}

DESIGN_SYSTEM:
- Typography: SF Pro (system default)
- Icons: SF Symbols
- Colors: Use semantic colors (e.g., .primary, .secondary, .accent)
- Spacing: Use standard SwiftUI spacing (8pt grid)

CONSTRAINTS:
- App Store Guidelines: VERIFY
- Human Interface Guidelines: COMPLY
- Privacy: DECLARE_ALL_USAGE
- Accessibility: SUPPORT_VOICEOVER

OUTPUT_FORMAT:
Generate complete, compilable Swift code with:
1. Data models
2. View models
3. Views (SwiftUI)
4. Navigation structure
5. Preview providers

CODE_STYLE:
- Use Swift 5.9+ syntax
- Prefer async/await for concurrency
- Use property wrappers appropriately
- Include MARK comments for sections"""

        elif language == "python":
            return f"""TARGET: {parsed['platform'].upper()}
FRAMEWORK: FastAPI + Pydantic
APP_TYPE: {parsed['app_type']}
DATE: {time.strftime('%Y-%m-%d')}

REQUIREMENTS:
{intent}

ARCHITECTURE:
- Pattern: Repository + Service Layer
- Validation: Pydantic models
- Async: asyncio throughout

SCREENS/ENDPOINTS:
{component_specs}

CONSTRAINTS:
- Security: OWASP Top 10 aware
- Type hints: Required throughout
- Documentation: Docstrings required

OUTPUT_FORMAT:
Generate complete, runnable Python code with:
1. Pydantic models
2. Service layer
3. API endpoints
4. Tests"""

        else:  # typescript
            return f"""TARGET: {parsed['platform'].upper()}
FRAMEWORK: React + TypeScript
APP_TYPE: {parsed['app_type']}
DATE: {time.strftime('%Y-%m-%d')}

REQUIREMENTS:
{intent}

ARCHITECTURE:
- Pattern: Component + Hooks
- State: React Query or Zustand
- Styling: Tailwind CSS

COMPONENTS:
{component_specs}

CONSTRAINTS:
- TypeScript strict mode
- Accessibility: WCAG 2.1 AA
- Performance: Memoization where needed

OUTPUT_FORMAT:
Generate complete, type-safe TypeScript code with:
1. Type definitions
2. React components
3. Custom hooks
4. Tests"""

    def _get_output_format(self, language: str) -> str:
        """Get output format for language."""
        formats = {
            "swift": OutputFormat.SWIFT_PROMPT.value,
            "python": OutputFormat.PYTHON_PROMPT.value,
            "typescript": OutputFormat.TYPESCRIPT_PROMPT.value
        }
        return formats.get(language, OutputFormat.SWIFT_PROMPT.value)

    def _get_warnings(self, intent: str) -> List[str]:
        """Get warnings based on intent."""
        warnings = []
        intent_lower = intent.lower()

        warning_patterns = {
            r"\b(health|healthkit)\b": "HealthKit requires special entitlements and privacy descriptions",
            r"\b(location|gps)\b": "Location services require NSLocationWhenInUseUsageDescription",
            r"\b(camera|photo)\b": "Camera/Photos require NSCameraUsageDescription or NSPhotoLibraryUsageDescription",
            r"\b(notification|push)\b": "Push notifications require APNs configuration",
            r"\b(payment|purchase)\b": "In-app purchases require StoreKit configuration and App Store review",
            r"\b(biometric|face id|touch id)\b": "Biometric auth requires NSFaceIDUsageDescription",
        }

        for pattern, warning in warning_patterns.items():
            if re.search(pattern, intent_lower):
                warnings.append(warning)

        return warnings


# ═══════════════════════════════════════════════════════════════════════════════
# CARTRIDGE MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class CartridgeManager:
    """
    Central manager for all Newton cartridges.

    Provides unified interface for cartridge compilation
    with automatic type detection and routing.
    """

    def __init__(self):
        self.visual = VisualCartridge()
        self.sound = SoundCartridge()
        self.sequence = SequenceCartridge()
        self.data = DataCartridge()
        self.rosetta = RosettaCompiler()

    def compile_visual(self, intent: str, **kwargs) -> CartridgeResult:
        """Compile visual specification."""
        return self.visual.compile(intent, **kwargs)

    def compile_sound(self, intent: str, **kwargs) -> CartridgeResult:
        """Compile sound specification."""
        return self.sound.compile(intent, **kwargs)

    def compile_sequence(self, intent: str, **kwargs) -> CartridgeResult:
        """Compile sequence specification."""
        return self.sequence.compile(intent, **kwargs)

    def compile_data(self, intent: str, **kwargs) -> CartridgeResult:
        """Compile data specification."""
        return self.data.compile(intent, **kwargs)

    def compile_rosetta(self, intent: str, **kwargs) -> CartridgeResult:
        """Compile code generation prompt."""
        return self.rosetta.compile(intent, **kwargs)

    def auto_compile(self, intent: str, **kwargs) -> CartridgeResult:
        """
        Automatically detect cartridge type and compile.

        Analyzes intent to determine the most appropriate cartridge.
        """
        intent_lower = intent.lower()

        # Detection patterns
        visual_patterns = r"\b(image|picture|graphic|svg|visual|icon|logo|illustration|draw|design)\b"
        sound_patterns = r"\b(sound|audio|music|tone|melody|beep|voice|sfx)\b"
        sequence_patterns = r"\b(video|animation|movie|clip|slideshow|motion|animate)\b"
        code_patterns = r"\b(app|application|code|build|create|develop|implement|program)\b"
        data_patterns = r"\b(report|data|analytics|statistics|chart|graph|table|csv|json)\b"

        if re.search(visual_patterns, intent_lower):
            return self.compile_visual(intent, **kwargs)
        elif re.search(sound_patterns, intent_lower):
            return self.compile_sound(intent, **kwargs)
        elif re.search(sequence_patterns, intent_lower):
            return self.compile_sequence(intent, **kwargs)
        elif re.search(code_patterns, intent_lower):
            return self.compile_rosetta(intent, **kwargs)
        elif re.search(data_patterns, intent_lower):
            return self.compile_data(intent, **kwargs)
        else:
            # Default to visual for creative intents
            return self.compile_visual(intent, **kwargs)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

# Singleton instance
_cartridge_manager: Optional[CartridgeManager] = None


def get_cartridge_manager() -> CartridgeManager:
    """Get or create the global CartridgeManager instance."""
    global _cartridge_manager
    if _cartridge_manager is None:
        _cartridge_manager = CartridgeManager()
    return _cartridge_manager


__all__ = [
    # Types
    'CartridgeType',
    'OutputFormat',

    # Results
    'ConstraintResult',
    'CartridgeResult',

    # Checker
    'ConstraintChecker',

    # Cartridges
    'VisualCartridge',
    'SoundCartridge',
    'SequenceCartridge',
    'DataCartridge',
    'RosettaCompiler',

    # Manager
    'CartridgeManager',
    'get_cartridge_manager',

    # Constraints (for external use)
    'SAFETY_PATTERNS',
    'VISUAL_CONSTRAINTS',
    'SOUND_CONSTRAINTS',
    'SEQUENCE_CONSTRAINTS',
    'DATA_CONSTRAINTS',
    'ROSETTA_CONSTRAINTS',
]
