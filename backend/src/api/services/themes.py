import json

from backend.src.api.models import SimilarThemes, ThemeWithScore
from backend.src.api.services.graph import GraphService
from backend.src.api.services.llm import LlmService

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

    def find_similar_themes(self, theme: str, k=5) -> SimilarThemes:
        theme_embedding = self._llm_service.create_embedding(theme)
        candidate_themes = self._graph_service.find_similar_themes(theme_embedding, k)
        selected_themes = self._select_most_similar_themes(theme, candidate_themes)
        return SimilarThemes(candidate_themes, selected_themes)

    def get_theme_answer(self, theme: str, similar_theme_id) -> str:
        similar_theme = self._graph_service.find_theme_by_id(similar_theme_id)
        recap_text = self._graph_service.find_recap_by_theme_id(similar_theme_id)
        prompt = _THEME_ANSWER_PROMPT.format(
            requested_theme=theme,
            text=recap_text,
            selected_theme_title=similar_theme.title,
            selected_theme_description=similar_theme.description,
            selected_theme_explanation=similar_theme.explanation
        )
        return self._llm_service.query_gpt4o_mini(prompt, requires_json_answer=False)

    def _select_most_similar_themes(self, theme: str, candidate_themes: list[ThemeWithScore]) -> list[ThemeWithScore]:
        candidates_json = json.dumps([
            {
                'id': c.theme.semantic_id,
                'title': c.theme.title,
                'description': c.theme.description,
                'explanation': c.theme.explanation
            }
            for c in candidate_themes
        ])
        prompt = _REFINE_PROMPT_TEMPLATE.format(requested_theme=theme, candidate_themes=candidates_json)
        answer = json.loads(self._llm_service.query_gpt4o_mini(prompt))
        return list(filter(lambda x: x.theme.semantic_id in answer['ids'], candidate_themes))
