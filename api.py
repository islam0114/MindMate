# api.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn

from llm_bot import process_message, generate_weekly_report
from database import (
    init_db, 
    get_today_log, update_daily_data, get_all_logs, 
    get_weekly_logs, get_goals, save_goal, delete_goal, get_streak, save_log
)
from auth import init_users_table, register_user, login_user

# ==========================================
# Initialize Database & User Table
# ==========================================
init_db()
init_users_table()
print("✅ Database initialized and updated successfully.")

app = FastAPI(title="MindMate Backend API", version="2.1.0")

# ==========================================
# CORS Middleware Configuration
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# Data Models (Pydantic)
# ==========================================
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    user_id: int
    user_name: str
    user_text: str
    current_data: Dict[str, Any]
    chat_history: List[ChatMessage] = []

class ChatResponse(BaseModel):
    reply: str
    extracted_metrics: Dict[str, Any]
    mood: Dict[str, str]
    crisis_level: str

class ReportRequest(BaseModel):
    weekly_data: Dict[str, Any]

class AuthLogin(BaseModel):
    username: str
    password: str

class AuthRegister(BaseModel):
    username: str
    email: str
    password: str

class ManualDataUpdate(BaseModel):
    user_id: int
    data: Dict[str, Any]

class GoalRequest(BaseModel):
    user_id: int
    metric: str
    target: float
    priority: str = "متوسط"

# ==========================================
# Auth Endpoints
# ==========================================
@app.post("/api/auth/login")
def login(req: AuthLogin):
    success, result, uname = login_user(req.username, req.password)
    if not success:
        raise HTTPException(status_code=401, detail=result)
    return {"user_id": result, "username": uname}

@app.post("/api/auth/register")
def register(req: AuthRegister):
    success, result = register_user(req.username, req.email, req.password)
    if not success:
        raise HTTPException(status_code=400, detail=result)
    return {"message": "Account created successfully", "user_id": result}

# ==========================================
# Data & Dashboard Endpoints
# ==========================================
@app.get("/api/data/today/{user_id}")
def get_today_data(user_id: int):
    data = get_today_log(user_id)
    streak = get_streak(user_id)
    return {"today_log": data, "streak": streak}

@app.post("/api/data/update")
def update_manual_data(req: ManualDataUpdate):
    try:
        clean_data = {}
        for k, v in req.data.items():
            if v == "" or v is None:
                clean_data[k] = None
            else:
                try:
                    clean_data[k] = float(v)
                except (ValueError, TypeError):
                    clean_data[k] = v
                    
        update_daily_data(req.user_id, clean_data)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/logs/{user_id}")
def get_user_logs(user_id: int):
    logs = get_all_logs(user_id)
    return {"logs": logs}

# ==========================================
# Goals Endpoints
# ==========================================
@app.get("/api/data/goals/{user_id}")
def get_user_goals(user_id: int):
    goals = get_goals(user_id)
    return {"goals": goals}

@app.post("/api/data/goals")
def create_goal(req: GoalRequest):
    try:
        save_goal(req.user_id, req.metric, req.target, req.priority)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/data/goals/{user_id}/{metric}")
def remove_goal(user_id: int, metric: str):
    try:
        delete_goal(user_id, metric)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# AI Chat & Report Endpoints
# ==========================================
@app.post("/api/chat", response_model=ChatResponse)
def process_chat(request: ChatRequest):
    try:
        history = [{"role": msg.role, "content": msg.content} for msg in request.chat_history]
        result = process_message(
            user_text=request.user_text,
            current_data=request.current_data,
            chat_history=history,
            user_name=request.user_name,
            user_id=request.user_id
        )
        
        mood_summary = result.get("mood", {"emoji": "😐", "color": "#E0E0E080", "category": "طبيعي"})
        crisis_level = result.get("crisis_level", "none")
        
        current_data = request.current_data.copy()
        for k, v in result.get("extracted_metrics", {}).items():
            if v is not None:
                current_data[k] = v
                
        history.append({"role": "user", "content": request.user_text})
        history.append({"role": "assistant", "content": result.get("reply", "")})
        
        save_log(
            text=request.user_text, 
            response=result.get("reply", ""), 
            data_dict=current_data, 
            mood_summary=mood_summary, 
            chat_history_list=history, 
            crisis_level=crisis_level, 
            user_id=request.user_id
        )

        return ChatResponse(
            reply=result.get("reply", "حدث خطأ غير متوقع."),
            extracted_metrics=result.get("extracted_metrics", {}),
            mood=mood_summary,
            crisis_level=crisis_level
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/report")
def generate_report(request: ReportRequest):
    try:
        report = generate_weekly_report(request.weekly_data)
        return {"report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)