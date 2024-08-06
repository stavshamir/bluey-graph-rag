import os
from dataclasses import asdict
from dataclasses import dataclass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.graph import GraphService
from services.llm import LlmService
from services.themes import ThemesService

uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
username = os.environ.get("NEO4J_USERNAME", "neo4j")
password = os.environ.get("NEO4J_PASSWORD", "stavshamir")

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@dataclass
class FindSimilarThemesRequest:
    theme: str


@dataclass
class ThemeAnswerRequest:
    theme: str
    similar_theme_id: str


graph_service = GraphService(uri, username, password)
llm_service = LlmService()
themes_service = ThemesService(graph_service, llm_service)


@app.on_event("startup")
async def startup_event():
    graph_service.connect()


@app.on_event("shutdown")
async def shutdown_event():
    graph_service.close()


@app.post("/themes/find_similar")
async def find_similar_themes(request: FindSimilarThemesRequest):
    return asdict(themes_service.find_similar_themes(request.theme))


@app.post("/themes/answer")
async def theme_answer(request: ThemeAnswerRequest) -> str:
    return themes_service.get_theme_answer(request.theme, request.similar_theme_id)
