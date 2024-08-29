import csv

from openai import OpenAI

client = OpenAI()


def create_embedding(text: str) -> list[float]:
    results = client.embeddings.create(input=[text], model="text-embedding-ada-002")
    return results.data[0].embedding


def get_themes() -> dict[str, str]:
    with open('data/themes.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return {
            theme['id']: f'{theme["title"]}\n{theme["description"]}'
            for theme in reader
        }


def save_embeddings(embeddings: dict[str, list[float]]):
    with open('data/themes_embeddings.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id'] + [i for i in range(1536)])
        for theme_id, embedding in embeddings.items():
            writer.writerow([theme_id] + embedding)


if __name__ == '__main__':
    themes = get_themes()
    embeddings = {
        theme_id: create_embedding(theme)
        for theme_id, theme in themes.items()
    }
    save_embeddings(embeddings)
