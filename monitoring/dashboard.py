from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, List
import uvicorn
from utils.logger import log

app = FastAPI(title="Nifty Trading Bot Dashboard")

# Global state (in production, use Redis or database)
trading_state = {
    'status': 'stopped',
    'current_position': 0,
    'daily_pnl': 0,
    'daily_trades': 0,
    'last_signal': None,
    'orders': [],
    'equity_curve': []
}

@app.get("/")
async def root():
    return {"message": "Nifty Trading Bot API", "status": "running"}

@app.get("/status")
async def get_status():
    """Get current trading status"""
    return JSONResponse(content=trading_state)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from datetime import datetime
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/metrics")
async def get_metrics():
    """Get trading metrics"""
    return {
        'daily_pnl': trading_state['daily_pnl'],
        'daily_trades': trading_state['daily_trades'],
        'current_position': trading_state['current_position'],
        'total_orders': len(trading_state['orders'])
    }

@app.get("/orders")
async def get_orders():
    """Get order history"""
    return {'orders': trading_state['orders']}

@app.get("/equity")
async def get_equity_curve():
    """Get equity curve"""
    return {'equity_curve': trading_state['equity_curve']}

@app.post("/stop")
async def stop_trading():
    """Stop trading"""
    trading_state['status'] = 'stopped'
    log.warning("Trading stopped via API")
    return {"message": "Trading stopped", "status": "stopped"}

@app.post("/start")
async def start_trading():
    """Start trading"""
    trading_state['status'] = 'running'
    log.info("Trading started via API")
    return {"message": "Trading started", "status": "running"}

def update_state(key: str, value):
    """Update trading state"""
    trading_state[key] = value

def run_dashboard(host: str = "0.0.0.0", port: int = 8000):
    """Run FastAPI dashboard"""
    log.info(f"Starting dashboard on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    import pandas as pd
    run_dashboard()
