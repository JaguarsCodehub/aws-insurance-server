def calculate_quote(car_make: str, car_model: str, year: int, registration_number: str) -> float:
    base_premium = 500  # Base premium in pounds
    
    # Age factor: Older cars have higher premiums
    current_year = 2024
    age = current_year - year
    age_factor = min(age * 50, 1000)  # Maximum age increase of 1000
    
    # Make factor: Example premium adjustments based on make
    make_factors = {
        'bmw': 1.3,
        'mercedes': 1.3,
        'toyota': 1.0,
        'honda': 1.0,
        'ford': 1.1
    }
    make_factor = make_factors.get(car_make.lower(), 1.2)
    
    # Calculate final premium
    premium = (base_premium + age_factor) * make_factor
    
    return round(premium, 2)
