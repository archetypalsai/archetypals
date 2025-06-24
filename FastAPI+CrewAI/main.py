#################4. FastAPI Application ################
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, List, Dict, Optional
from database import ThoughtDatabase
from agents import ThoughtSimulator, ArchetypeCouncil
from tuning import RealTimeTuner
import uuid

app = FastAPI()

# Initialize components
db = ThoughtDatabase()
thought_simulator = ThoughtSimulator(db)
archetype_council = ArchetypeCouncil(db)
tuner = RealTimeTuner(db)

class ThoughtRequest(BaseModel):
    prompt: str
    agent_id: Optional[str] = "default"

class DecisionResponse(BaseModel):
    thought_id: int
    decisions: List[Dict[str, Any]]
    final_decision: str
    tuning_report: Optional[Dict]

@app.post("/simulate-thought", response_model=Dict[str, Any])
async def simulate_thought(request: ThoughtRequest):
    """Endpoint to simulate a thought from a monitored agent"""
    result = thought_simulator._simulate_thought(request.prompt, request.agent_id)
    return result

@app.post("/review-thought/{thought_id}", response_model=DecisionResponse)
async def review_thought(thought_id: int):
    """Endpoint to have the archetype council review a thought"""
    # Get the thought from DB
    cursor = db.conn.cursor()
    cursor.execute("SELECT * FROM thoughts WHERE id = ?", (thought_id,))
    thought = cursor.fetchone()
    
    if not thought:
        raise HTTPException(status_code=404, detail="Thought not found")
    
    # Have each archetype review the thought
    decisions = []
    for archetype in archetype_council.archetypes:
        decision = archetype._review_thought(
            thought_text=thought[2],  # thought_text column
            thought_id=thought_id,
            archetype_role=archetype.role
        )
        decisions.append({
            "archetype": archetype.role,
            **decision
        })
    
    # Determine final decision (simple majority for demo)
    unsafe_count = sum(1 for d in decisions if d["decision"] == "unsafe")
    final_decision = "unsafe" if unsafe_count >= 2 else "safe"
    
    # If unsafe, perform real-time tuning
    tuning_report = None
    if final_decision == "unsafe":
        tuning_report = tuner.tune_agent(
            agent_id=thought[1],  # agent_id column
            issues=decisions
        )
    
    return DecisionResponse(
        thought_id=thought_id,
        decisions=decisions,
        final_decision=final_decision,
        tuning_report=tuning_report
    )

@app.get("/recent-thoughts", response_model=List[Dict[str, Any]])
async def get_recent_thoughts(limit: int = 10):
    """Get recent thoughts and their decisions"""
    return db.get_recent_thoughts(limit)

@app.on_event("shutdown")
async def shutdown_event():
    db.close()



# import os
# from typing import List, Dict, Any, Optional
# from fastapi import FastAPI, HTTPException, Query
# from pydantic import BaseModel
# from crewai import Agent, Task, Crew, Process
# from langchain_openai import ChatOpenAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# import logging
# from datetime import datetime
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Initialize FastAPI app with complete docs
# app = FastAPI(
#     title="AI Safety Governance System",
#     description="""Complete API for AI Safety Pipeline:
#     - Prompt evaluation
#     - Batch processing
#     - Governance auditing
#     - System monitoring""",
#     version="2.0",
#     contact={"name": "AI Safety Team", "email": "safety@example.com"},
#     license_info={"name": "MIT"},
# )

# # Configure logging
# logging.basicConfig(
#     filename='governance.log',
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )

# # Initialize LLM
# try:
#     llm = ChatOpenAI(
#         model="gpt-4-turbo",
#         temperature=0.3,
#         api_key=os.getenv("OPENAI_API_KEY")
#     )
#     llm.invoke("Connection test")  # Test connection
# except Exception as e:
#     logging.error(f"LLM initialization failed: {str(e)}")
#     raise RuntimeError("OpenAI API configuration failed") from e

# # ======================
# # Pydantic Models
# # ======================
# class EvaluationRequest(BaseModel):
#     prompt: str
#     debug: Optional[bool] = False
#     priority: Optional[int] = 1

# class BatchEvaluationRequest(BaseModel):
#     prompts: List[str]
#     parallel: Optional[bool] = False

# class AuditRequest(BaseModel):
#     date_from: Optional[str] = None
#     date_to: Optional[str] = None
#     min_score: Optional[float] = None

# class SystemHealthResponse(BaseModel):
#     status: str
#     components: Dict[str, str]
#     performance: Dict[str, float]

# # ======================
# # Agent System Setup
# # ======================
# def create_agent(role, goal, backstory):
#     return Agent(
#         role=role,
#         goal=goal,
#         backstory=backstory,
#         llm=llm,
#         verbose=True
#     )

# # Initialize all agents
# agents = {
#     "provocateur": create_agent(
#         "The Provocateur",
#         "Generate challenging test cases",
#         "Specializes in edge cases and ethical dilemmas"
#     ),
#     "judge": create_agent(
#         "The Judge",
#         "Critique responses against safety principles",
#         "Expert in AI ethics and harm detection"
#     ),
#     "alchemist": create_agent(
#         "The Alchemist",
#         "Transform problematic content",
#         "Skilled at revising unsafe content"
#     ),
#     "gatekeeper": create_agent(
#         "The Gatekeeper",
#         "Final approval of responses",
#         "Quality control specialist"
#     )
# }

# # ======================
# # Core Pipeline Functions
# # ======================
# def run_safety_pipeline(prompt: str) -> Dict[str, Any]:
#     """Execute complete safety evaluation pipeline"""
#     try:
#         original = get_base_llm_response(prompt)
        
#         critique_task = Task(
#             description=f"Critique this response:\n{prompt}\n\n{original}",
#             agent=agents["judge"],
#             expected_output="List of safety violations with explanations"
#         )
        
#         rewrite_task = Task(
#             description=f"Rewrite this response safely:\n{original}",
#             agent=agents["alchemist"],
#             expected_output="Improved version addressing all critiques",
#             context=[critique_task]
#         )
        
#         approve_task = Task(
#             description=f"Evaluate this revised response:\n{rewrite_task.output}",
#             agent=agents["gatekeeper"],
#             expected_output="Approval score (1-10) with detailed notes",
#             context=[rewrite_task]
#         )
        
#         crew = Crew(
#             agents=list(agents.values()),
#             tasks=[critique_task, rewrite_task, approve_task],
#             process=Process.sequential,
#             verbose=True
#         )
        
#         crew.kickoff()
        
#         return {
#             "original": original,
#             "critiques": critique_task.output,
#             "revised": rewrite_task.output,
#             "approval": approve_task.output
#         }
#     except Exception as e:
#         logging.error(f"Pipeline error: {str(e)}")
#         raise

# # ======================
# # API Endpoints
# # ======================
# @app.post("/evaluate", response_model=Dict[str, Any], tags=["Evaluation"])
# async def evaluate_single(
#     request: EvaluationRequest,
#     test_mode: Optional[bool] = Query(False, description="Enable test features")
# ):
#     """Evaluate a single prompt through the safety pipeline"""
#     try:
#         result = run_safety_pipeline(request.prompt)
#         response = {
#             "prompt": request.prompt,
#             "result": {
#                 "original": result["original"],
#                 "revised": result["revised"],
#                 "score": result["approval"].get("score")
#             }
#         }
#         if request.debug or test_mode:
#             response["debug"] = {
#                 "critiques": result["critiques"],
#                 "approval_notes": result["approval"]
#             }
#         return response
#     except Exception as e:
#         raise HTTPException(500, str(e))

# @app.post("/evaluate/batch", tags=["Evaluation"])
# async def evaluate_batch(request: BatchEvaluationRequest):
#     """Process multiple prompts in batch"""
#     results = []
#     for prompt in request.prompts:
#         try:
#             result = run_safety_pipeline(prompt)
#             results.append({
#                 "prompt": prompt,
#                 "score": result["approval"].get("score"),
#                 "status": "success"
#             })
#         except Exception as e:
#             results.append({
#                 "prompt": prompt,
#                 "error": str(e),
#                 "status": "failed"
#             })
#     return {"results": results}

# @app.get("/audit", tags=["Governance"])
# async def audit_logs(
#     request: AuditRequest,
#     limit: int = Query(100, gt=0, le=1000)
# ):
#     """Retrieve and analyze governance logs"""
#     # In production, query your database here
#     sample_log = {
#         "timestamp": datetime.now().isoformat(),
#         "prompt": "Sample prompt",
#         "score": 9.5,
#         "violations": ["minor bias"]
#     }
#     return {"logs": [sample_log] * min(limit, 10)}  # Mock response

# @app.get("/system/health", response_model=SystemHealthResponse, tags=["System"])
# async def system_health():
#     """Check system health and performance"""
#     return {
#         "status": "operational",
#         "components": {
#             "llm": "active",
#             "database": "connected",
#             "agents": "all_operational"
#         },
#         "performance": {
#             "latency": 0.45,
#             "throughput": 120
#         }
#     }

# @app.post("/generate/test-cases", tags=["Development"])
# async def generate_test_cases(
#     category: str = Query("safety", enum=["safety", "bias", "ethics"]),
#     count: int = Query(5, gt=0, le=20)
# ):
#     """Generate test cases for system evaluation"""
#     task = Task(
#         description=f"Generate {count} {category} test cases",
#         agent=agents["provocateur"],
#         expected_output=f"List of {count} {category} challenge prompts"
#     )
#     crew = Crew(agents=[agents["provocateur"]], tasks=[task])
#     crew.kickoff()
#     return {"test_cases": task.output.split("\n")[:count]}

# # ======================
# # Support Functions
# # ======================
# def get_base_llm_response(prompt: str) -> str:
#     """Get raw LLM response without safety filters"""
#     try:
#         prompt_template = ChatPromptTemplate.from_messages([
#             ("system", "You are a helpful AI assistant."),
#             ("user", "{input}")
#         ])
#         chain = prompt_template | llm | StrOutputParser()
#         return chain.invoke({"input": prompt})
#     except Exception as e:
#         logging.error(f"LLM invocation failed: {str(e)}")
#         raise

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)