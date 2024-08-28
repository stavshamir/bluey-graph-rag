import csv
import json
import re


def save_csv(filename: str, items: list[dict]):
    with open(f'data/{filename}.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=items[0].keys())
        writer.writeheader()
        for item in items:
            writer.writerow(item)


def create_recap_edges():
    with open('data/recap_parts.csv', encoding='utf-8', mode='r') as f:
        reader = csv.DictReader(f)
        return [
            {
                'source_id': line['episode_id'],
                'label': 'HAS_RECAP_PART',
                'target_id': line['id']
            }
            for line in reader
        ]


class RelationTransformer:
    def __init__(self):
        self.relative_relation_types = [
            'father',
            'mother',
            'brother',
            'sister',
            'husband',
            'wife',
            'daughter',
            'son'
        ]

    def get_new_label(self, relation_type: str) -> str | None:
        for t in self.relative_relation_types:
            if bool(re.search(fr'(?<![-\w])\b{t}\b(?![-\w])', relation_type)) and 'law' not in relation_type:
                return f'IS_{t.upper()}_OF'
        return None

    def transform_relation(self):
        with open('data/relations.csv', encoding='utf-8', mode='r') as f:
            reader = csv.DictReader(f)
            new_relations = []
            for relation in reader:
                relation_label = relation['label']
                relation_type = relation['relation_type']

                if relation_label == 'IS_RELATIVE_OF':
                    new_label = self.get_new_label(relation_type)
                    if new_label:
                        new_relations.append({
                            'source_id': relation['source_id'],
                            'label': new_label,
                            'target_id': relation['target_id'],
                        })
                else:
                    new_relations.append({
                        'source_id': relation['source_id'],
                        'label': relation['label'],
                        'target_id': relation['target_id'],
                    })

            return new_relations


class ThemeTransformer:
    @staticmethod
    def get_theme_title(t):
        return {
            'Emotional intelligence and dealing with emotions': 'Emotions',
            'Life lessons and personal growth': 'Lessons',
            'Imagination and play': 'Imagination'
        }[t]

    @staticmethod
    def transform_themes():
        theme_nodes = []
        has_theme_edges = []

        with open('data/themes.jsonl', mode='r') as f:
            for line in f.readlines():
                d = json.loads(line)
                episode_id = d['episode_id']
                for theme in d['themes']:
                    theme_id = f'Theme:{episode_id}:{ThemeTransformer.get_theme_title(theme["theme"])}'
                    theme_node = {
                        'id': theme_id,
                        'episode_id': episode_id,
                        'type': ThemeTransformer.get_theme_title(theme["theme"]),
                        'title': theme['title'],
                        'description': theme["description"],
                        'explanation': theme['explanation'],
                        'supporting_quotes': '; '.join(theme['supporting_quotes'])
                    }
                    theme_nodes.append(theme_node)

                    has_theme_edges.append({
                        'source_id': episode_id,
                        'label': 'HAS_THEME',
                        'target_id': theme_id
                    })

            return theme_nodes, has_theme_edges


if __name__ == '__main__':
    recap_edges = create_recap_edges()
    save_csv('recap_edges', recap_edges)

    transformed_relations = RelationTransformer().transform_relation()
    save_csv('transformed_relations', transformed_relations)

    themes, has_theme_edges = ThemeTransformer().transform_themes()
    save_csv('themes', themes)
    save_csv('has_themes', has_theme_edges)
