import json
import logging
from pathlib import Path
from fastapi import FastAPI, Request
import uvicorn

app = FastAPI(title="Incident Responder")

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("responder")

@app.post("/alerts")
async def receive_alerts(request: Request):
    data = await request.json()
    alerts = data.get("alerts", [])
    
    output_lines = []
    for alert in alerts:
        labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})
        alert_name = labels.get("alertname", "UnknownAlert")
        summary = annotations.get("summary", "")
        
        # Save incident details
        alert_file = LOG_DIR / f"{alert_name}.json"
        with open(alert_file, "w") as f:
            json.dump(alert, f, indent=2)
            
        if labels.get("test") == "true" or "no incident to fix" in summary.lower():
            response_text = "Test notification received. No incident to fix."
        else:
            response_text = f"Incident detected for {alert_name}. Agent triggered in headless mode."
            
        output_lines.append(response_text)
        logger.info(f"Agent output: {output_lines[-1]}")
        
    final_answer = output_lines[-1] if output_lines else "No alert received."
    return {"status": "ok", "agent_response": final_answer}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
