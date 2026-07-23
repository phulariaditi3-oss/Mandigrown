def get_storage_recommendation(produce_type: str) -> dict:
    """
    Returns storage recommendations for a given produce type.
    """
    produce_type = produce_type.lower()
    
    recs = {
        "tomato": {
            "temperature": "12–15°C",
            "shelf_life": "7 Days",
            "tips": "Store at room temperature until fully ripe. Keep away from direct sunlight. Do not refrigerate unripe tomatoes as it halts the ripening process and ruins flavor."
        },
        "potato": {
            "temperature": "7–10°C",
            "shelf_life": "3–5 Weeks",
            "tips": "Store in a cool, dark, and well-ventilated place. Keep away from onions as they emit gases that cause potatoes to sprout faster."
        },
        "apple": {
            "temperature": "0–4°C",
            "shelf_life": "4–8 Weeks",
            "tips": "Store in the crisper drawer of the refrigerator. Apples emit ethylene gas, so keep them away from other ethylene-sensitive produce."
        },
        "onion": {
            "temperature": "7–10°C",
            "shelf_life": "1–2 Months",
            "tips": "Store in a cool, dry, dark, and well-ventilated place. Do not store in plastic bags; use mesh bags or wire baskets."
        }
    }
    
    # Fallback for unknown produce
    return recs.get(produce_type, {
        "temperature": "Cool, dry place",
        "shelf_life": "Varies",
        "tips": "Ensure proper ventilation and keep away from direct moisture."
    })
