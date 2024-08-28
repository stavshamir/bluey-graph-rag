import csv
import json
from collections import defaultdict
from typing import Literal

from openai import OpenAI
from pydantic import BaseModel

client = OpenAI()

Themes = Literal[
    'Emotional intelligence and dealing with emotions',
    'Life lessons and personal growth',
    'Imagination and play',
]


class Theme(BaseModel):
    theme: Themes
    title: str
    description: str
    explanation: str
    supporting_quotes: list[str]


class ThemesContainer(BaseModel):
    themes: list[Theme]


def query_gpt4o(prompt: str) -> str:
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content


enforce_schema_message_v1 = f'''
Reply with a valid json using the following schema:
{ThemesContainer.model_json_schema()}
'''

prompt_template_v1 = """
Analyze the provided episode recap:

```
{recap}
```
- For each of the themes provided below, determine if the theme is expressed in the recap.
- If it is represented:
  - Provide a title. Avoid using character names.
  - Provide a brief and succinct description of the theme. Avoid using characters name and try to be generalize the theme making it relatable not only in the context of the show.
  - Provide an explanation for your decision. The explanation may reference characters as needed.
  - Provide exact quotes from the recap to support you decision.
  
Allowed Themes:
- Emotional intelligence and dealing with emotions (describe which emotions are dealt with, by who and how)
- Life lessons and personal growth (describe the lesson learned, by who and how)
- Imagination and play (describe the game)
"""


def build_prompt_v1(recap: str) -> str:
    return prompt_template_v1.format(recap=recap) + enforce_schema_message_v1


with open('data/recap_parts.csv', encoding='utf-8', mode='r') as f:
    reader = csv.DictReader(f)
    episode_ids_to_recap_parts = defaultdict(list)
    for part in reader:
        episode_ids_to_recap_parts[part['episode_id']].append(part['text'])

with open('data/themes.jsonl', mode='a', encoding='utf-8') as f:
    for episode_id, parts in episode_ids_to_recap_parts.items():
        print(episode_id)
        recap = '\n\n'.join(parts)
        prompt_v1 = build_prompt_v1(recap)
        response = query_gpt4o(prompt_v1)
        d = json.loads(response)
        d['episode_id'] = episode_id
        f.write(json.dumps(d) + '\n')
