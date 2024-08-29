import os
from dataclasses import asdict
from dataclasses import dataclass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.graph import GraphService
from services.llm import LlmService
from services.themes import ThemesService

uri = os.environ["NEO4J_URI"]
username = os.environ["NEO4J_USERNAME"]
password = os.environ["NEO4J_PASSWORD"]

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://stavshamir.github.io/bluey-graph-rag/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=['*']
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


@app.get("/")
async def health():
    return 'healthy'


@app.post("/themes/find_similar")
async def find_similar_themes(request: FindSimilarThemesRequest):
    return asdict(themes_service.find_similar_themes(request.theme))
