from openai import OpenAI, NOT_GIVEN


class LlmService:
    def __init__(self):
        self._client = OpenAI()

    def create_embedding(self, text: str) -> list[float]:
        text = text.replace("\n", " ")
        results = self._client.embeddings.create(input=[text], model="text-embedding-ada-002")
        return results.data[0].embedding

    def query_gpt4o_mini(self, prompt: str, requires_json_answer=True) -> str:
        completion = self._client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            response_format={"type": "json_object"} if requires_json_answer else NOT_GIVEN,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content
