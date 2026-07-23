from fastapi import APIRouter
import random
from datetime import datetime

router = APIRouter(prefix="/market-price", tags=["market"])

@router.get("/{produce_name}")
def get_market_price(produce_name: str):
    """
    Fetches the latest market price for the given produce.
    Simulates fetching from a Government Agmarknet API.
    """
    produce_name = produce_name.capitalize()
    
    # Simulate API network delay or unavailable behavior in ~5% of cases
    if random.random() < 0.05:
        return {
            "success": False,
            "error": "Government Market API is temporarily unavailable. Please try again later."
        }
        
    # Generate realistic mock data based on produce
    # Prices in INR (₹) per kg
    base_prices = {
        "Tomato": 35,
        "Potato": 25,
        "Apple": 120,
        "Onion": 45
    }
    
    base = base_prices.get(produce_name, 50)
    
    # Randomize for daily fluctuation
    min_price = max(5, int(base * 0.8) + random.randint(-5, 5))
    max_price = int(base * 1.2) + random.randint(0, 10)
    avg_price = (min_price + max_price) // 2
    
    markets = ["Azadpur Mandi", "Vashi APMC", "Okhla Mandi", "Lasalgaon"]
    districts = ["New Delhi", "Mumbai", "South East Delhi", "Nashik"]
    states = ["Delhi", "Maharashtra", "Delhi", "Maharashtra"]
    
    idx = random.randint(0, 3)
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    return {
        "success": True,
        "data": {
            "produce_name": produce_name,
            "today_price": avg_price,
            "min_price": min_price,
            "max_price": max_price,
            "average_price": avg_price,
            "market_name": markets[idx],
            "district": districts[idx],
            "state": states[idx],
            "last_updated": today_str
        }
    }
