from dataclasses import dataclass


@dataclass
class Theme:
    episode_title: str
    episode_url: str
    semantic_id: str
    title: str
    description: str
    explanation: str
    supporting_quotes: list[str]


@dataclass
class ThemeResponse:
    theme: Theme
    score: float
    is_best_match: bool
    answer: str


@dataclass
class SimilarThemes:
    themes: list[ThemeResponse]


@dataclass
class Recap:
    episode_title: str
    parts: list[str]
