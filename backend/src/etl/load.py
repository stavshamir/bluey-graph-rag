import csv
import os
from dataclasses import dataclass

from neo4j import GraphDatabase

uri = os.environ["NEO4J_URI"]
username = os.environ.get["NEO4J_USERNAME"]
password = os.environ.get["NEO4J_PASSWORD"]


@dataclass
class Property:
    name: str
    value: str | int

    @classmethod
    def from_header_and_value(cls, header: str, value: str) -> 'Property':
        split_header = header.split(':')
        _type = split_header[1] if len(split_header) == 2 else str

        if _type == 'int':
            value = int(value)

        return Property(split_header[0], value)


@dataclass
class Node:
    label: str
    semantic_id: str
    properties: list[Property]

    @classmethod
    def from_dict(cls, d: dict[str, str], label: str) -> 'Node':
        return cls(label=label, semantic_id=d['id'], properties=cls._build_properties(d))

    def build_create_statement(self):
        return f'CREATE (:{self.label} {{id: "{self.semantic_id}"{self._build_properties_placeholders()}}})'

    def properties_dict(self) -> dict[str, any]:
        return {
            p.name: p.value for p in self.properties
        }

    def _build_properties_for_create_statement(self) -> str:
        return ', ' + ', '.join(
            f'{p.name}: "{p.value}"' if type(p.value) is str else f'{p.name}: {p.value}' for p in self.properties)

    def _build_properties_placeholders(self) -> str:
        return ', ' + ', '.join(f'{p.name}: ${p.name}' for p in self.properties)

    @staticmethod
    def _build_properties(d: dict[str, str]) -> list[Property]:
        return [
            Property.from_header_and_value(key, value)
            for key, value
            in d.items()
            if key not in ['label', 'id']
        ]


@dataclass
class Edge:
    label: str
    from_id: str
    to_id: str
    properties: list[Property]

    @classmethod
    def from_dict(cls, d: dict[str, str]) -> 'Edge':
        return cls(label=d['label'], from_id=d['source_id'], to_id=d['target_id'], properties=cls._build_properties(d))

    def build_create_statement(self):
        return (
            f'MATCH (a), (b) '
            f'WHERE a.id="{self.from_id}" AND b.id="{self.to_id}" '
            f'CREATE (a)-[:{self.label} {{{self._build_properties_placeholders()}}}]->(b)'
        )

    def properties_dict(self) -> dict[str, any]:
        return {
            p.name: p.value for p in self.properties
        }

    def _build_properties_for_create_statement(self) -> str:
        return ', ' + ', '.join(
            f'{p.name}: "{p.value}"' if type(p.value) is str else f'{p.name}: {p.value}' for p in self.properties)

    def _build_properties_placeholders(self) -> str:
        return ', '.join(f'{p.name}: ${p.name}' for p in self.properties)

    @staticmethod
    def _build_properties(d: dict[str, str]) -> list[Property]:
        return [
            Property.from_header_and_value(key, value)
            for key, value
            in d.items()
            if key not in ['label', 'source_id', 'target_id']
        ]


def load_nodes(path, label: str):
    print(f'Loading nodes from {path}')
    with open(path, mode='r', encoding='utf-8') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            node = Node.from_dict(row, label)
            session.execute_write(lambda tx: tx.run(node.build_create_statement(), **node.properties_dict()))


def load_edges(path):
    print(f'Loading edges from {path}')
    with open(path, mode='r', encoding='utf-8') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            edge = Edge.from_dict(row)
            session.execute_write(lambda tx: tx.run(edge.build_create_statement(), **edge.properties_dict()))


def load_theme_embeddings(path: str):
    print('Loading theme embeddings')
    with open(path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for row in reader:
            theme_id = row[0]
            embedding = [float(v) for v in row[1:]]
            query = '''
            MATCH (t:Theme {id: $theme_id})
            SET t.embedding = $embedding
            '''
            session.execute_write(lambda tx: tx.run(query, theme_id=theme_id, embedding=embedding))


def create_theme_index():
    create_index_query = '''
    CREATE VECTOR INDEX theme_index IF NOT EXISTS
    FOR (t:Theme)
    ON t.embedding
    OPTIONS { indexConfig: {
     `vector.dimensions`: 1536,
     `vector.similarity_function`: 'cosine'
    }}
    '''

    print('Creating theme index')
    session.execute_write(lambda tx: tx.run(create_index_query))


if __name__ == '__main__':
    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        with driver.session() as session:
            session.execute_write(lambda tx: tx.run("MATCH (n) DETACH DELETE n"))  # Removes everything in the graph

            load_nodes('data/characters.csv', 'Character')
            load_nodes('data/episodes.csv', 'Episode')
            load_nodes('data/recap_parts.csv', 'RecapPart')
            load_nodes('data/themes.csv', 'Theme')
            #
            load_edges('data/transformed_relations.csv')
            load_edges('data/recap_edges.csv')
            load_edges('data/appearances.csv')
            load_edges('data/has_themes.csv')

            load_theme_embeddings('data/themes_embeddings.csv')
            create_theme_index()
