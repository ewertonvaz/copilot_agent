"""
This serves the "sample_agent" agent. This is an example of self-hosting an agent
through our FastAPI integration. However, you can also host in LangGraph platform.
"""

from fastapi import FastAPI
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from contextlib import asynccontextmanager
from copilotkit import LangGraphAGUIAgent
from ag_ui_langgraph import add_langgraph_fastapi_endpoint
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from sample_agent.agent import workflow
from sample_agent.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncPostgresSaver.from_conn_string(
        settings.database_url,
    ) as checkpointer:
        await checkpointer.setup()
        graph = workflow.compile(checkpointer=checkpointer)

        add_langgraph_fastapi_endpoint(
            app=app,
            agent=LangGraphAGUIAgent(
                name="sample_agent",
                description="An example agent to use as a starting point for your own agent.",
                graph=graph,
            ),
            path="/agents/sample_agent"
        )

        yield


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:3000",
    "http://localhost:3030",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

images_directory = Path(__file__).parent / "images"
app.mount("/images", StaticFiles(directory=str(images_directory)), name="images")


def main():
    """Run the uvicorn server."""
    uvicorn.run(
        "sample_agent.demo:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.dev_mode,
    )


if __name__ == "__main__":
    main()
