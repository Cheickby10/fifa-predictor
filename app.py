import os
import json
import random
import numpy as np
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict
import uvicorn
from collections import Counter

app = FastAPI()

# Données FIFA
TEAMS = {
    "Real Madrid": {"attack": 87, "defense": 85, "overall": 86},
    "Barcelona": {"attack": 86, "defense": 84, "overall": 86},
    "Manchester City": {"attack": 88, "defense": 85, "overall": 87},
    "Liverpool": {"attack": 86, "defense": 84, "overall": 85},
    "Bayern Munich": {"attack": 87, "defense": 85, "overall": 86},
    "PSG": {"attack": 87, "defense": 83, "overall": 85},
    "Juventus": {"attack": 83, "defense": 85, "overall": 84},
    "Chelsea": {"attack": 82, "defense": 84, "overall": 83},
    "Manchester United": {"attack": 83, "defense": 82, "overall": 83},
    "Milan": {"attack": 84, "defense": 83, "overall": 83}
}

class PredictRequest(BaseModel):
    home: str
    away: str

def predict_match(home: str, away: str) -> Dict:
    """Prédiction rapide et précise"""
    if home not in TEAMS or away not in TEAMS:
        return {"error": "Équipe non trouvée"}
    
    # Poisson amélioré
    lambda_home = max(0.3, (TEAMS[home]["attack"] + (100 - TEAMS[away]["defense"])) / 100 * 1.8 * 1.15)
    lambda_away = max(0.3, (TEAMS[away]["attack"] + (100 - TEAMS[home]["defense"])) / 100 * 1.8 * 0.9)
    
    # Simulation
    home_wins = draw = away_wins = 0
    scores = Counter()
    
    for _ in range(5000):
        h = np.random.poisson(lambda_home)
        a = np.random.poisson(lambda_away)
        scores[f"{h}-{a}"] += 1
        if h > a: home_wins += 1
        elif h == a: draw += 1
        else: away_wins += 1
    
    top_scores = [{"score": k, "prob": round(v/5000*100, 2)} for k, v in scores.most_common(5)]
    
    return {
        "match": f"{home} vs {away}",
        "predictions": {
            "home_win": round(home_wins/5000*100, 1),
            "draw": round(draw/5000*100, 1),
            "away_win": round(away_wins/5000*100, 1)
        },
        "expected_goals": {
            "home": round(lambda_home, 2),
            "away": round(lambda_away, 2)
        },
        "top_scores": top_scores,
        "confidence": min(85, 70 + abs(TEAMS[home]["overall"] - TEAMS[away]["overall"])),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
def home():
    return {"message": "FIFA Predictor API", "status": "online"}

@app.get("/teams")
def get_teams():
    return {"teams": list(TEAMS.keys())}

@app.post("/predict")
def predict(data: PredictRequest):
    return predict_match(data.home, data.away)

@app.get("/predict/{home}/{away}")
def predict_get(home: str, away: str):
    return predict_match(home, away)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)