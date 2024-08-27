from neo4j import GraphDatabase

from backend.src.api.models import Theme, Recap


class GraphService:
    def __init__(self, uri: str, username: str, password: str):
        self._uri = uri
        self._username = username
        self._password = password
        self._driver = None

    def connect(self):
        if not self._driver:
            self._driver = GraphDatabase.driver(self._uri, auth=(self._username, self._password))

    def close(self):
        if self._driver:
            self._driver.close()
            self._driver = None

    def find_similar_themes(self, vector: list[float], k=5) -> list[(Theme, float)]:
        with self._driver.session():
            cypher = f'''
            CALL db.index.vector.queryNodes("theme_index", {k}, {vector})
            YIELD node, score
            MATCH (node)<-[:HAS_THEME]-(e:Episode)
            RETURN DISTINCT 
                e.title AS episode_title,
                e.wiki_url AS episode_url,
                node.id AS semantic_id,
                node.title AS title,
                node.description AS description,
                node.explanation AS explanation,
                node.supporting_quotes as supporting_quotes,
                score
            '''

            def to_theme_with_score(d: dict) -> (Theme, float):
                return Theme(
                    episode_title=d['episode_title'],
                    episode_url=d['episode_url'],
                    semantic_id=d['semantic_id'],
                    title=d['title'],
                    description=d['description'],
                    explanation=d['explanation'],
                    supporting_quotes=d['supporting_quotes'].split(';'),
                ), d['score']

            records, _, _ = self._driver.execute_query(query_=cypher, database_="neo4j")
            return [to_theme_with_score(r.data()) for r in records]

    def find_recap_by_theme_id(self, theme_semantic_id: str) -> Recap:
        with self._driver.session():
            cypher = f'''
            MATCH (:Theme {{id: "{theme_semantic_id}"}})<-[:HAS_THEME]-(e:Episode)-[:HAS_RECAP_PART]->(r: RecapPart)
            RETURN r.text AS text, e.title AS episode_title
            ORDER BY r.index
            '''

            records, _, _ = self._driver.execute_query(query_=cypher, database_="neo4j")
            results = [r.data() for r in records]
            return Recap(
                episode_title=results[0]['episode_title'],
                parts=[r['text'] for r in results]
            )

    def find_theme_by_id(self, theme_semantic_id: str) -> Theme:
        with self._driver.session():
            cypher = f'''
            MATCH (t:Theme {{id: "{theme_semantic_id}"}})
            RETURN t LIMIT 1
            '''

            records, _, _ = self._driver.execute_query(query_=cypher, database_="neo4j")
            d = [r.data()['t'] for r in records][0]
            return Theme(
                episode_title='',
                episode_url='',
                semantic_id=d['id'],
                title=d['title'],
                description=d['description'],
                explanation=d['explanation'],
                supporting_quotes=d['supporting_quotes'].split(';'),
            )
