"""
ai/provider.py — Provider abstraction layer.

Architecture:
    BaseAIProvider defines the contract every provider must fulfil.
    Adding a new provider (Gemini, Claude, GPT-4, etc.) requires only:
      1. Subclassing BaseAIProvider.
      2. Implementing the four abstract methods.
      3. Passing the new class to IntelligenceService at construction time.
    No business logic in IntelligenceService needs to change.
"""

import re
import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Stopwords — used by LocalIntelligenceProvider for topic extraction
# ---------------------------------------------------------------------------
STOPWORDS = {
    'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
    'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
    'shall', 'can', 'need', 'dare', 'ought', 'used', 'it', 'its', 'this',
    'that', 'these', 'those', 'i', 'we', 'you', 'he', 'she', 'they', 'who',
    'which', 'what', 'as', 'if', 'while', 'although', 'because', 'since',
    'though', 'not', 'no', 'nor', 'so', 'yet', 'both', 'also', 'just',
    'than', 'then', 'when', 'where', 'how', 'all', 'each', 'more', 'most',
    'other', 'some', 'such', 'new', 'first', 'last', 'long', 'great',
    'little', 'own', 'right', 'big', 'high', 'different', 'small', 'large',
    'next', 'early', 'young', 'important', 'public', 'private', 'real',
    'best', 'free', 'us', 'our', 'their', 'his', 'her', 'its',
}

# Known technology/organization brands for entity detection
KNOWN_BRANDS = {
    'OpenAI', 'Microsoft', 'Google', 'Apple', 'Meta', 'Amazon', 'Tesla',
    'Nvidia', 'Intel', 'AMD', 'IBM', 'Oracle', 'Salesforce', 'Twitter',
    'Anthropic', 'DeepMind', 'xAI', 'Mistral', 'Hugging Face', 'Stability',
    'Palantir', 'Databricks', 'Snowflake', 'Netflix', 'Uber', 'Airbnb',
    'SpaceX', 'NASA', 'MIT', 'Stanford', 'Harvard', 'Berkeley',
    'Python', 'TensorFlow', 'PyTorch', 'Kubernetes', 'Docker', 'Linux',
    'ChatGPT', 'Gemini', 'Claude', 'Llama', 'GPT',
    'EU', 'USA', 'UK', 'China', 'India', 'Russia', 'Germany', 'Japan',
    'Congress', 'Senate', 'Pentagon', 'WHO', 'UN', 'NATO', 'IMF',
}


# ---------------------------------------------------------------------------
# Base contract
# ---------------------------------------------------------------------------

class BaseAIProvider:
    """
    Abstract base class defining the provider contract.
    All methods must return predictable Python primitives so that
    IntelligenceService remains completely provider-agnostic.
    """

    def summarize(self, text: str) -> str:
        raise NotImplementedError

    def extract_topics(self, text: str) -> list:
        raise NotImplementedError

    def extract_entities(self, text: str) -> list:
        raise NotImplementedError

    def generate_confidence(self, text: str, entity_count: int, topic_count: int) -> float:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Local (zero-cost) implementation
# ---------------------------------------------------------------------------

class LocalIntelligenceProvider(BaseAIProvider):
    """
    Fully local, zero-dependency intelligence provider.

    Algorithms:
        summarize      — TextRank-inspired sentence scoring by keyword frequency.
        extract_topics — Stopword-filtered unigram frequency ranking.
        extract_entities — Heuristic: known brand lookup + consecutive
                           title-cased word sequences.
        generate_confidence — Normalised composite score.
    """

    PROVIDER_NAME = 'local'

    # ------------------------------------------------------------------
    # summarize
    # ------------------------------------------------------------------

    def summarize(self, text: str) -> str:
        """
        TextRank-inspired extractive summarizer.
        Steps:
          1. Split text into sentences.
          2. Build a word-frequency map (excluding stopwords).
          3. Score each sentence as the sum of its word frequencies.
          4. Return the top-3 sentences in their original document order.
        """
        if not text or len(text.strip()) < 30:
            return text.strip() if text else ""

        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

        if not sentences:
            return text[:500]

        # Build word frequency map
        word_freq: dict = {}
        for sentence in sentences:
            for word in re.findall(r'\b[a-zA-Z]{3,}\b', sentence.lower()):
                if word not in STOPWORDS:
                    word_freq[word] = word_freq.get(word, 0) + 1

        # Score sentences
        scored = []
        for i, sentence in enumerate(sentences):
            score = sum(
                word_freq.get(w, 0)
                for w in re.findall(r'\b[a-zA-Z]{3,}\b', sentence.lower())
                if w not in STOPWORDS
            )
            scored.append((score, i, sentence))

        # Pick top-3, restore original order
        top = sorted(scored, key=lambda x: x[0], reverse=True)[:3]
        top_ordered = sorted(top, key=lambda x: x[1])
        return ' '.join(s for _, _, s in top_ordered)

    # ------------------------------------------------------------------
    # extract_topics
    # ------------------------------------------------------------------

    def extract_topics(self, text: str) -> list:
        """
        Returns top-5 meaningful keywords by term frequency after
        stopword removal and short-word filtering.
        """
        if not text:
            return []

        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        freq: dict = {}
        for word in words:
            if word not in STOPWORDS:
                freq[word] = freq.get(word, 0) + 1

        ranked = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [word.title() for word, _ in ranked[:5]]

    # ------------------------------------------------------------------
    # extract_entities
    # ------------------------------------------------------------------

    def extract_entities(self, text: str) -> list:
        """
        Hybrid entity extractor:
          Pass 1 — Exact match against KNOWN_BRANDS (case-sensitive).
          Pass 2 — Regex for consecutive title-cased words (≥ 2 tokens,
                   e.g. "Quantum Computing", "Federal Reserve").
        Returns up to 10 deduplicated entities, brands prioritised.
        """
        if not text:
            return []

        found = set()

        # Pass 1: known brands
        for brand in KNOWN_BRANDS:
            if brand in text:
                found.add(brand)

        # Pass 2: consecutive title-case sequences (2+ words)
        pattern = re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b')
        for match in pattern.finditer(text):
            entity = match.group(1)
            # Filter out sentence starters caught at the start of a line
            if len(entity) > 4:
                found.add(entity)

        # Brands first, then heuristic hits; cap at 10
        brands_found = [e for e in found if e in KNOWN_BRANDS]
        others_found = [e for e in found if e not in KNOWN_BRANDS]
        combined = brands_found + others_found
        return combined[:10]

    # ------------------------------------------------------------------
    # generate_confidence
    # ------------------------------------------------------------------

    def generate_confidence(self, text: str, entity_count: int, topic_count: int) -> float:
        """
        Composite confidence score in the range [0.0, 100.0].
        Formula (as specified):
            score = min(100, (text_length / 50) + (entity_count * 5) + (topic_count * 5))
        """
        text_length = len(text) if text else 0
        raw = (text_length / 50) + (entity_count * 5) + (topic_count * 5)
        return round(min(100.0, raw), 2)
