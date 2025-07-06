# app.py - Stealth Notion AI Bot Web Interface
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import threading
import time
import logging
from datetime import datetime
import main  # your main.py logic

app = FastAPI(title="System Monitor", docs_url=None, redoc_url=None)

# Global state for monitoring
bot_status = {
    "running": False,
    "last_check": None,
    "total_processed": 0,
    "last_error": None,
    "start_time": None
}

def start_bot():
    """Start the bot in background thread"""
    global bot_status
    bot_status["running"] = True
    bot_status["start_time"] = datetime.now()
    
    def bot_runner():
        try:
            main.continuous_polling()
        except Exception as e:
            logging.error(f"Bot crashed: {e}")
            bot_status["last_error"] = str(e)
            bot_status["running"] = False
    
    thread = threading.Thread(target=bot_runner, daemon=True)
    thread.start()
    return thread

@app.get("/", response_class=HTMLResponse)
def read_root():
    """Stealth homepage - looks like a system monitor"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>System Monitor</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
            .running { background: #d4edda; color: #155724; }
            .stopped { background: #f8d7da; color: #721c24; }
            .metric { display: inline-block; margin: 10px; padding: 10px; background: #f8f9fa; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>System Monitor</h1>
            <div class="status running">Service Status: Active</div>
            <div class="metric">Uptime: <span id="uptime">--</span></div>
            <div class="metric">Last Check: <span id="lastcheck">--</span></div>
            <div class="metric">Processed: <span id="processed">--</span></div>
            <script>
                function updateStatus() {
                    fetch('/status')
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById('uptime').textContent = data.uptime || '--';
                            document.getElementById('lastcheck').textContent = data.last_check || '--';
                            document.getElementById('processed').textContent = data.total_processed || '0';
                        });
                }
                updateStatus();
                setInterval(updateStatus, 30000);
            </script>
        </div>
    </body>
    </html>
    """

@app.get("/status")
def get_status():
    """Get bot status (stealth endpoint)"""
    global bot_status
    
    if bot_status["start_time"]:
        uptime = datetime.now() - bot_status["start_time"]
        uptime_str = str(uptime).split('.')[0]  # Remove microseconds
    else:
        uptime_str = None
    
    return {
        "status": "active" if bot_status["running"] else "inactive",
        "uptime": uptime_str,
        "last_check": bot_status["last_check"],
        "total_processed": bot_status["total_processed"],
        "last_error": bot_status["last_error"]
    }

@app.post("/start")
def start_service():
    """Start the service (stealth endpoint)"""
    global bot_status
    if not bot_status["running"]:
        start_bot()
        return {"message": "Service started"}
    return {"message": "Service already running"}

@app.post("/stop")
def stop_service():
    """Stop the service (stealth endpoint)"""
    global bot_status
    bot_status["running"] = False
    return {"message": "Service stopped"}

# Start the bot automatically when the app starts
@app.on_event("startup")
async def startup_event():
    start_bot()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)