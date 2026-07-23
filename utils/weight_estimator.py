def estimate_weight(produce_type: str, size_score: float) -> dict:
    """
    Estimates the weight per piece and pieces per kg based on size_score.
    size_score ranges from 0-100 (from the AI model).
    """
    produce_type = produce_type.lower()
    
    # Average weights in grams based on size categories
    # Structure: { produce_type: { "Small": wt, "Medium": wt, "Large": wt } }
    base_weights = {
        "tomato": {"Small": 40, "Medium": 70, "Large": 120},
        "potato": {"Small": 50, "Medium": 100, "Large": 180},
        "apple": {"Small": 100, "Medium": 150, "Large": 200},
        "onion": {"Small": 40, "Medium": 80, "Large": 150},
    }
    
    # Fallback to a generic item if unknown
    weights = base_weights.get(produce_type, {"Small": 50, "Medium": 100, "Large": 150})
    
    # Map size_score to category
    if size_score < 40:
        size_category = "Small"
    elif size_score < 75:
        size_category = "Medium"
    else:
        size_category = "Large"
        
    avg_weight_g = weights[size_category]
    pieces_per_kg = round(1000 / avg_weight_g)
    
    return {
        "size_category": size_category,
        "average_weight_g": avg_weight_g,
        "pieces_per_kg": pieces_per_kg
    }
