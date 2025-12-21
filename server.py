import sys
from io import StringIO
import contextlib
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from src.simulator import Simulator

app = FastAPI(title="DiffServ Simulation API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development convenience
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimulationRequest(BaseModel):
    patterns: List[str]

class SimulationResponse(BaseModel):
    logs: List[str]
    results: List[Dict[str, Any]]

@app.post("/run_simulation", response_model=SimulationResponse)
async def run_simulation(request: SimulationRequest):
    try:
        # Validate patterns
        valid_chars = {'E', 'A', 'B'}
        normalized_patterns = []
        for p in request.patterns:
            p_upper = p.upper()
            if p_upper not in valid_chars:
                raise HTTPException(status_code=400, detail=f"Invalid pattern: {p}")
            normalized_patterns.append(p_upper)

        if not normalized_patterns:
            raise HTTPException(status_code=400, detail="No patterns provided")

        # Capture print output
        capture_io = StringIO()
        
        # Initialize and run simulator while capturing stdout
        with contextlib.redirect_stdout(capture_io):
            simulator = Simulator(normalized_patterns)
            simulator.run()
        
        # Get structured results
        results = simulator.get_results()
        
        # Get logs and split by line
        logs = capture_io.getvalue().splitlines()
        
        return {
            "logs": logs,
            "results": results
        }

    except Exception as e:
        import traceback
        traceback.print_exc() # Print to real stderr for debugging
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
