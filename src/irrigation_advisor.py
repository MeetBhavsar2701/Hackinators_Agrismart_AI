import random

def get_irrigation_advice(class_label: str, temperature: float = None, humidity: float = None):
    """
    Generates dynamic irrigation advice based on the detected crop disease,
    temperature, and humidity.
    """
    # Parse crop and disease status
    parts = class_label.split("___")
    crop = parts[0].replace("_", " ") if len(parts) > 0 else "Unknown Crop"
    disease = parts[1].replace("_", " ") if len(parts) > 1 else "Unknown"
    
    is_healthy = "healthy" in disease.lower()
    is_fungal = any(f in disease.lower() for f in ["blight", "mold", "rot", "spot", "mildew", "rust", "scab"])
    
    # Generate synthetic metrics if not provided (typical growing season values)
    if temperature is None:
        temperature = round(random.uniform(22.0, 32.0), 1)
    if humidity is None:
        humidity = round(random.uniform(40.0, 85.0), 1)
        
    advice = f"Current field conditions: Temp {temperature}°C, Humidity {humidity}%.\n\n"
    
    if is_healthy:
        if humidity > 80:
            advice += f"High humidity detected. Reduce overhead watering to prevent fungal onset in {crop}."
        elif temperature > 30:
            advice += f"High temperatures detected. Increase irrigation frequency for {crop}, preferably in early morning."
        else:
            advice += f"Conditions are optimal for {crop}. Maintain standard watering schedule based on soil moisture."
            
    elif is_fungal:
        advice += (
            f"Fungal pathogen detected ({disease}). "
            "IMMEDIATELY halt overhead irrigation and sprinklers! "
            "Water only at the base (drip irrigation) to keep the canopy dry. "
        )
        if humidity > 70:
            advice += "High ambient humidity is exacerbating the spread. Ensure proper plant spacing for airflow."
            
    else:
        # Bacterial or Viral
        advice += (
            f"Disease detected ({disease}). "
            "Maintain consistent soil moisture to reduce plant stress. "
            "Avoid working in the field when foliage is wet to prevent mechanical spread."
        )
        
    return {
        "crop": crop,
        "temperature": temperature,
        "humidity": humidity,
        "advice": advice
    }
