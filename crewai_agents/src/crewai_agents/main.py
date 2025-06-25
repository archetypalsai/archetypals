import os
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Optional
import logging
from crewai_agents.crew import constitutional_crew
from services.llm_service import AnythingLLMService
from middleware.logging import LoggingMiddleware
from middleware.auth import get_api_key
from config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description="Constitutional AI Validation Proxy for AnythingLLM",
    version="1.0.0"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)

# Security
api_key_header = APIKeyHeader(name="X-API-KEY")

# Models
class UserQuery(BaseModel):
    query: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class ValidationResponse(BaseModel):
    response: str
    is_approved: bool
    validation_details: Optional[dict] = None
    warnings: Optional[list] = None

# Services
llm_service = AnythingLLMService()

@app.post("/validate", response_model=ValidationResponse)
async def validate_response(
    query: UserQuery,
    request: Request,
    api_key: str = Depends(get_api_key)
) -> ValidationResponse:
    """
    Validate a user query through the constitutional AI pipeline.
    
    1. Get initial response from AnythingLLM
    2. Validate through CrewAI safety agents
    3. Return approved response or safety-modified version
    """
    try:
        # Step 1: Get initial LLM response
        llm_response = await llm_service.get_response(
            query.query,
            workspace_id=settings.ANYTHINGLLM_WORKSPACE_ID
        )
        
        # Step 2: Constitutional validation
        validation_result = constitutional_crew.validate_response(llm_response)
        
        if not validation_result["is_approved"]:
            logger.warning(
                f"Response rejected for query: {query.query}\n"
                f"Reasons: {validation_result['validation_results']}"
            )
            # Generate a safe alternative
            safe_response = await llm_service.get_safe_response(
                query.query,
                violations=validation_result["validation_results"]
            )
            
            return ValidationResponse(
                response=safe_response,
                is_approved=False,
                validation_details=validation_result["validation_results"],
                warnings=["Response modified for safety"]
            )
        
        return ValidationResponse(
            response=validation_result["final_response"],
            is_approved=True
        )
        
    except Exception as e:
        logger.error(f"Validation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred during response validation"
        )

@app.get("/health")
async def health_check():
    """Endpoint for health checks"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level="info" if settings.DEBUG else "warning"
    )


# #!/usr/bin/env python
# import sys
# import warnings

# from datetime import datetime

# from crewai_agents.crew import CrewaiAgents

# warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# # This main file is intended to be a way for you to run your
# # crew locally, so refrain from adding unnecessary logic into this file.
# # Replace with inputs you want to test with, it will automatically
# # interpolate any tasks and agents information

# def run():
#     """
#     Run the crew.
#     """
#     inputs = {
#         'topic': 'AI LLMs',
#         'current_year': str(datetime.now().year)
#     }
    
#     try:
#         CrewaiAgents().crew().kickoff(inputs=inputs)
#     except Exception as e:
#         raise Exception(f"An error occurred while running the crew: {e}")


# def train():
#     """
#     Train the crew for a given number of iterations.
#     """
#     inputs = {
#         "topic": "AI LLMs",
#         'current_year': str(datetime.now().year)
#     }
#     try:
#         CrewaiAgents().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

#     except Exception as e:
#         raise Exception(f"An error occurred while training the crew: {e}")

# def replay():
#     """
#     Replay the crew execution from a specific task.
#     """
#     try:
#         CrewaiAgents().crew().replay(task_id=sys.argv[1])

#     except Exception as e:
#         raise Exception(f"An error occurred while replaying the crew: {e}")

# def test():
#     """
#     Test the crew execution and returns the results.
#     """
#     inputs = {
#         "topic": "AI LLMs",
#         "current_year": str(datetime.now().year)
#     }
    
#     try:
#         CrewaiAgents().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

#     except Exception as e:
#         raise Exception(f"An error occurred while testing the crew: {e}")
