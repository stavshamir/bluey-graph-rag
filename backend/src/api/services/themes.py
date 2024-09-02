import json

from api.models import SimilarThemes, Theme, SimilarTheme, ThemeResponse
from api.services.graph import GraphService
from api.services.llm import LlmService

_REFINE_PROMPT_TEMPLATE = '''
Below is a short text describing a theme (requested theme) and a list of candidate similar themes.
Return a list containing the ids of the candidate themes that are most similar to the requested theme.
Return a json array containing only the ids and nothing else. 
Here is an example response: {{"ids": ["Theme:Episode:The_Weekend:Emotions"}}

Requested theme: {requested_theme}

Candidates:
{candidate_themes}
'''

_THEME_ANSWER_PROMPT = '''
How is the theme "{requested_theme}" expressed in the text below?

Text:
{text}

---

Someone else previously analyzed this text and came up with the following relevant information which you can use in your answer.
Theme title: {selected_theme_title}
Theme description: {selected_theme_description}
Explanation: {selected_theme_explanation}

---

Response with three succinct sentences.
'''


class ThemesService:
    def __init__(self, graph_service: GraphService, llm_service: LlmService):
        self._graph_service = graph_service
        self._llm_service = llm_service

    def find_similar_themes(self, theme: str, k=3) -> SimilarThemes:
        theme_embedding = self._llm_service.create_embedding(theme)
        similar_themes = self._graph_service.find_similar_themes(theme_embedding, k)
        return SimilarThemes(self._build_themes_response(theme, similar_themes))

    def get_theme_answer(self, theme: str, similar_theme: Theme) -> str:
        prompt = _THEME_ANSWER_PROMPT.format(
            requested_theme=theme,
            text=similar_theme.recap,
            selected_theme_title=similar_theme.title,
            selected_theme_description=similar_theme.description,
            selected_theme_explanation=similar_theme.explanation
        )
        return self._llm_service.query_gpt4o_mini(prompt, requires_json_answer=False)

    def _build_themes_response(self, theme: str, similar_themes: list[(Theme, float)]) -> list[SimilarTheme]:
        best_match_themes = self._get_best_match_theme_id(theme, [t for t, _ in similar_themes])
        return [
            SimilarTheme(
                theme=ThemeResponse(
                    semantic_id=t.semantic_id,
                    episode_title=t.episode_title,
                    episode_url=t.episode_url,
                    title=t.title,
                    description=t.description,
                    explanation=t.explanation,
                    supporting_quotes=t.supporting_quotes
                ),
                score=s,
                is_best_match=t.semantic_id in best_match_themes,
                answer=self.get_theme_answer(theme, t)
            )
            for t, s in similar_themes
        ]

    def _get_best_match_theme_id(self, theme: str, similar_themes: list[Theme]) -> list[str]:
        candidates_json = json.dumps([
            {
                'id': t.semantic_id,
                'title': t.title,
                'description': t.description,
                'explanation': t.explanation
            }
            for t in similar_themes
        ])
        prompt = _REFINE_PROMPT_TEMPLATE.format(requested_theme=theme, candidate_themes=candidates_json)
        answer = json.loads(self._llm_service.query_gpt4o_mini(prompt))
        return answer['ids']
