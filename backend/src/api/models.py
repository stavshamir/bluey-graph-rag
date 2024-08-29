from dataclasses import dataclass


@dataclass
class Theme:
    semantic_id: str
    episode_title: str
    episode_url: str
    title: str
    description: str
    explanation: str
    supporting_quotes: list[str]
    recap: str


@dataclass
class ThemeResponse:
    semantic_id: str
    episode_title: str
    episode_url: str
    title: str
    description: str
    explanation: str
    supporting_quotes: list[str]


@dataclass
class SimilarTheme:
    theme: ThemeResponse
    score: float
    is_best_match: bool
    answer: str


@dataclass
class SimilarThemes:
    themes: list[SimilarTheme]


@dataclass
class Recap:
    episode_title: str
    parts: list[str]
