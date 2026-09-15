def get_expert_advice(class_label: str):
    """
    Provides comprehensive actionable advice for a given crop disease.
    Uses offline heuristics for immediate availability without API keys.
    """
    parts = class_label.split("___")
    crop = parts[0].replace("_", " ") if len(parts) > 0 else "Crop"
    disease = parts[1].replace("_", " ").lower() if len(parts) > 1 else "unknown condition"
    
    if "healthy" in disease:
        return {
            "title": f"Healthy {crop}",
            "overview": "Your crop shows no visible signs of disease.",
            "action_plan": [
                "Continue standard fertilization schedule.",
                "Maintain optimal irrigation practices.",
                "Monitor weekly for any early signs of pests or lesions."
            ]
        }
        
    advice = {
        "title": f"{crop} - {disease.title()}",
        "overview": f"A potential infection of {disease} has been detected on your {crop}.",
        "action_plan": []
    }
    
    # Fungal
    if any(f in disease for f in ["blight", "mold", "rot", "spot", "mildew", "rust", "scab"]):
        advice["overview"] += " This is a fungal pathogen that spreads rapidly in moist conditions."
        advice["action_plan"].extend([
            "Remove and destroy infected leaves/plants immediately. Do NOT compost them.",
            "Apply a copper-based or sulfur-based fungicide as a first line of defense.",
            "Ensure proper spacing between plants to maximize airflow and reduce humidity.",
            "Rotate crops next season to prevent soil-borne reinfection."
        ])
    # Viral
    elif "virus" in disease or "mosaic" in disease:
        advice["overview"] += " This is a viral infection, which is typically incurable and spread by insects (vectors)."
        advice["action_plan"].extend([
            "Uproot and burn/destroy the infected plant immediately to save the rest of the field.",
            "Inspect surrounding plants for aphids, whiteflies, or thrips (common viral vectors).",
            "Apply neem oil or insecticidal soap to control the vector insect population.",
            "Disinfect all pruning tools with a 10% bleach solution before touching healthy plants."
        ])
    # Bacterial
    elif "bacterial" in disease:
        advice["overview"] += " This is a bacterial infection that often enters through wounds or natural plant openings."
        advice["action_plan"].extend([
            "Avoid working in the field when foliage is wet (bacteria spread easily in water droplets).",
            "Apply a copper bactericide (though prevention is more effective than cure).",
            "Prune infected parts using sterilized shears.",
            "Avoid excessive nitrogen fertilization, which promotes soft, vulnerable growth."
        ])
    else:
        # Generic fallback
        advice["action_plan"].extend([
            "Isolate the affected area if possible.",
            "Consult a local agricultural extension office for a definitive lab test.",
            "Avoid using broad-spectrum chemicals until the exact pathogen is confirmed."
        ])
        
    return advice
