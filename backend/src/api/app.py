import logging
import os
from dataclasses import asdict
from dataclasses import dataclass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.services.graph import GraphService
from api.services.llm import LlmService
from api.services.themes import ThemesService

uri = os.environ["NEO4J_URI"]
username = os.environ["NEO4J_USERNAME"]
password = os.environ["NEO4J_PASSWORD"]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://stavshamir.github.io"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=['*']
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)


@dataclass
class FindSimilarThemesRequest:
    theme: str


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
    logger.info(f"Received request: {request.theme}")
    themes = asdict(themes_service.find_similar_themes(request.theme))
    logger.info(f"Returning response for '{request.theme}': {themes}")
    return themes
