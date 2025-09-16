# Sample FRA patta holder data
fra_holders = [
    {"name": "Ravi", "land_size": 1.5, "water_index": 0.3, "income": 30000},
    {"name": "Meena", "land_size": 0.8, "water_index": 0.7, "income": 15000},
    {"name": "Sita", "land_size": 2.2, "water_index": 0.2, "income": 50000},
]

# Decision rules for scheme recommendations
def recommend_schemes(holder):
    schemes = []
    if holder["land_size"] < 1.0:
        schemes.append("PM-KISAN (income support)")
    if holder["water_index"] < 0.4:
        schemes.append("Jal Jeevan Mission (water conservation)")
    if holder["income"] < 20000:
        schemes.append("MGNREGA (employment support)")
    if holder["land_size"] > 2.0:
        schemes.append("PM Gati Shakti (infrastructure support)")
    return schemes

# Generate recommendations
for h in fra_holders:
    rec = recommend_schemes(h)
    print(f"Farmer: {h['name']}")
    print("Recommended Schemes:", ", ".join(rec) if rec else "No specific schemes")
    print("-" * 40)
