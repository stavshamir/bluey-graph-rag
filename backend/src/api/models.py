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
class ThemeWithScore:
    theme: Theme
    score: float


@dataclass
class SimilarThemes:
    candidate_themes: list[ThemeWithScore]
    selected_themes: list[ThemeWithScore]


@dataclass
class Recap:
    episode_title: str
    parts: list[str]
