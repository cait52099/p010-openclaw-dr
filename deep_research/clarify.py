"""Clarification gate for Deep Research."""

import json
from pathlib import Path
from typing import Any, Optional


class Clarifier:
    """
    Clarification gate:
    - topic < 20 chars triggers clarification
    - ambiguous topics trigger <= 3 questions
    """

    # Ambiguity indicators
    AMBIGUOUS_TERMS = {
        "it", "this", "that", "they", "them",
        "something", "anything", "what", "how",
    }

    SHORT_TOPICS = [
        "ai", "ml", "dl", "llm", "nlp",
        "cv", "ag", "ar", "vr", "mr",
        "web", "app", "db", "os", "api",
    ]

    def __init__(self):
        self.max_questions = 3
        self.min_topic_length = 20

    def needs_clarification(self, topic: str) -> bool:
        """
        Determine if a topic needs clarification.

        Returns True if:
        - topic is empty or too short (< 20 chars)
        - topic contains ambiguous terms
        - topic is in SHORT_TOPICS list
        """
        if not topic or len(topic.strip()) < self.min_topic_length:
            return True

        # Check for ambiguous terms
        topic_lower = topic.lower()
        words = topic_lower.split()

        # Contains ambiguous terms
        if any(term in self.AMBIGUOUS_TERMS for term in words):
            return True

        # Short known abbreviations
        if topic_lower in self.SHORT_TOPICS:
            return True

        return False

    def generate_questions(self, topic: str) -> list[str]:
        """
        Generate clarification questions for an ambiguous topic.

        Returns up to 3 questions.
        """
        questions = []

        if not topic or len(topic.strip()) < 5:
            questions.append("What specific topic would you like to research?")
            questions.append("What aspect or angle are you interested in?")
            questions.append("What is the purpose of this research?")
            return questions[:self.max_questions]

        # Topic-specific questions
        if len(topic) < self.min_topic_length:
            questions.append(
                f"Could you provide more context about '{topic}'? "
                f"What specifically would you like to learn?"
            )

        if any(term in topic.lower().split() for term in self.AMBIGUOUS_TERMS):
            questions.append(
                "Your topic seems vague. Could you be more specific about what you mean?"
            )

        # Always add scope question
        if len(questions) < self.max_questions:
            questions.append(
                "What depth of research do you need? (brief overview / comprehensive analysis)"
            )

        return questions[:self.max_questions]

    def clarify(
        self,
        topic: str,
        answers: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Perform clarification process.

        Args:
            topic: The research topic
            answers: Previous answers (for multi-step clarification)

        Returns:
            Dictionary with:
            - needs_clarification: bool
            - questions: list of questions to ask
            - clarified_topic: refined topic (if answered)
            - answers: provided answers
        """
        result = {
            "needs_clarification": self.needs_clarification(topic),
            "questions": [],
            "clarified_topic": topic,
            "answers": answers or [],
        }

        if result["needs_clarification"]:
            result["questions"] = self.generate_questions(topic)

        return result

    def save_clarify_json(
        self,
        output_path: Path,
        topic: str,
        questions: list[str],
        answers: list[str],
    ) -> None:
        """Save clarification data to clarify.json."""
        data = {
            "original_topic": topic,
            "questions": questions,
            "answers": answers,
            "final_topic": " ".join(answers) if answers else topic,
            "clarified": bool(answers),
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

    def load_clarify_json(self, input_path: Path) -> dict[str, Any]:
        """Load clarification data from clarify.json."""
        with open(input_path) as f:
            return json.load(f)
