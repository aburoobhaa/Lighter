from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import json
import os
from datetime import datetime, timedelta
from functools import wraps 
from flask import send_from_directory


# ==================== APP CONFIGURATION ====================
app = Flask(__name__)
app.secret_key = "lightermade"

BASE_DIR = os.path.dirname(__file__)
USERS_FILE = os.path.join(BASE_DIR, "users.json")
DATA_DIR = os.path.join(BASE_DIR, "data")


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def user_file(username, data_type="data"):
    """Returns path for user's JSON file (data or goal)."""
    filename = f"{username.lower()}_{data_type}.json"
    return os.path.join(DATA_DIR, filename)
# ==================== CONSTANTS ====================
USERS = {
    "Boo": "boo@lighter",
    "Kudi": "kudi@lighter"
}

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

MEAL_TYPES = ["breakfast", "lunch", "dinner", "snack"]

FOOD_DATA = {
    # Traditional South Indian Breakfast
    "idli": {"cal": 35, "unit": "per piece"},
    "dosa": {"cal": 133, "unit": "per piece"},
    "masala dosa": {"cal": 250, "unit": "per piece"},
    "vada": {"cal": 97, "unit": "per piece"},
    "upma": {"cal": 180, "unit": "per bowl"},
    "pongal": {"cal": 250, "unit": "per bowl"},
    "uttapam": {"cal": 200, "unit": "per piece"},
    "pesarattu": {"cal": 150, "unit": "per piece"},
    "paniyaram": {"cal": 45, "unit": "per piece"},
    "appam": {"cal": 120, "unit": "per piece"},
    
    # Rice & Grains
    "rice": {"cal": 200, "unit": "per bowl"},
    "brown rice": {"cal": 170, "unit": "per bowl"},
    "lemon rice": {"cal": 180, "unit": "per bowl"},
    "tamarind rice": {"cal": 280, "unit": "per bowl"},
    "curd rice": {"cal": 150, "unit": "per bowl"},
    "bisibelebath": {"cal": 300, "unit": "per bowl"},
    "pulao": {"cal": 200, "unit": "per bowl"},
    "biryani": {"cal": 300, "unit": "per bowl"},
    "chapati": {"cal": 100, "unit": "per piece"},
    "roti": {"cal": 90, "unit": "per piece"},
    "paratha": {"cal": 150, "unit": "per piece"},
    "naan": {"cal": 260, "unit": "per piece"},
    "puri": {"cal": 120, "unit": "per piece"},
    "poori": {"cal": 120, "unit": "per piece"},
    
    # Curries & Gravies
    "sambar": {"cal": 50, "unit": "per cup"},
    "rasam": {"cal": 40, "unit": "per cup"},
    "dal": {"cal": 120, "unit": "per cup"},
    "dal makhani": {"cal": 250, "unit": "per cup"},
    "chole": {"cal": 200, "unit": "per cup"},
    "rajma": {"cal": 180, "unit": "per cup"},
    "kadhi": {"cal": 100, "unit": "per cup"},
    "korma": {"cal": 220, "unit": "per cup"},
    "paneer butter masala": {"cal": 280, "unit": "per cup"},
    "palak paneer": {"cal": 200, "unit": "per cup"},
    
    # Poriyal (South Indian Stir-fry)
    "beans poriyal": {"cal": 80, "unit": "per bowl"},
    "cabbage poriyal": {"cal": 60, "unit": "per bowl"},
    "carrot poriyal": {"cal": 70, "unit": "per bowl"},
    "potato poriyal": {"cal": 120, "unit": "per bowl"},
    "beetroot poriyal": {"cal": 75, "unit": "per bowl"},
    "brinjal poriyal": {"cal": 90, "unit": "per bowl"},
    
    # Dairy
    "curd": {"cal": 100, "unit": "per bowl"},
    "buttermilk": {"cal": 40, "unit": "per glass"},
    "paneer": {"cal": 265, "unit": "per 100g"},
    "ghee": {"cal": 120, "unit": "per tablespoon"},
    "milk": {"cal": 150, "unit": "per cup"},
    
    # Beverages
    "filter coffee": {"cal": 80, "unit": "per cup"},
    "tea": {"cal": 70, "unit": "per cup"},
    "masala chai": {"cal": 90, "unit": "per cup"},
    "badam milk": {"cal": 200, "unit": "per glass"},
    "rose milk": {"cal": 180, "unit": "per glass"},
    "water": {"cal": 0, "unit": "per glass"},
    "coconut water": {"cal": 45, "unit": "per cup"},
    
    # Snacks & Fried Items
    "samosa": {"cal": 252, "unit": "per piece"},
    "pakora": {"cal": 50, "unit": "per piece"},
    "bonda": {"cal": 80, "unit": "per piece"},
    "bajji": {"cal": 70, "unit": "per piece"},
    "muruku": {"cal": 120, "unit": "per piece (big)"},
    "kai murukku": {"cal": 110, "unit": "per piece"},
    "ribbon pakoda": {"cal": 140, "unit": "per 25g"},
    "mixture": {"cal": 180, "unit": "per 28g"},
    "banana chips": {"cal": 150, "unit": "per 28g"},
    "appalam": {"cal": 149, "unit": "per piece"},
    "papad": {"cal": 149, "unit": "per piece"},
    "vadaam": {"cal": 80, "unit": "per piece"},
    
    # Dry Fruits
    "badam": {"cal": 7, "unit": "per piece"},
    "pistah": {"cal": 4, "unit": "per piece"},
    "cashew": {"cal": 9, "unit": "per piece"},
    "walnut": {"cal": 26, "unit": "per half"},
    "raisins": {"cal": 3, "unit": "per piece"},
    "dates": {"cal": 23, "unit": "per piece"},
    "dried figs": {"cal": 20, "unit": "per piece"},
    "dried apricot": {"cal": 8, "unit": "per piece"},
    "prunes": {"cal": 20, "unit": "per piece"},
    
    # Sweets & Desserts
    "sugar candy": {"cal": 10, "unit": "per piece (2-4g)"},
    "athirasam": {"cal": 180, "unit": "per piece"},
    "jalebi": {"cal": 150, "unit": "per piece"},
    "gulab jamun": {"cal": 150, "unit": "per piece"},
    "rasgulla": {"cal": 106, "unit": "per piece"},
    "ladoo": {"cal": 180, "unit": "per piece"},
    "mysore pak": {"cal": 200, "unit": "per piece"},
    "halwa": {"cal": 250, "unit": "per 100g"},
    "payasam": {"cal": 200, "unit": "per cup"},
    "kheer": {"cal": 200, "unit": "per cup"},
    "kesari": {"cal": 180, "unit": "per serving"},
    "peda": {"cal": 100, "unit": "per piece"},
    "barfi": {"cal": 120, "unit": "per piece"},
    
    # Snacks - Healthy
    "makhana": {"cal": 35, "unit": "per 10g"},
    "roasted chana": {"cal": 120, "unit": "per 30g"},
    "groundnuts": {"cal": 170, "unit": "per 30g"},
    "peanuts": {"cal": 166, "unit": "per 30g"},
    
    # Chutneys & Condiments
    "coconut chutney": {"cal": 80, "unit": "per 2 tbsp"},
    "tomato chutney": {"cal": 40, "unit": "per 2 tbsp"},
    "mint chutney": {"cal": 15, "unit": "per 2 tbsp"},
    "coriander chutney": {"cal": 20, "unit": "per 2 tbsp"},
    "peanut chutney": {"cal": 90, "unit": "per 2 tbsp"},
    "pickle": {"cal": 15, "unit": "per tsp"},
    
    # Cold Drinks
    "coca cola": {"cal": 140, "unit": "per 330ml can"},
    "pepsi": {"cal": 150, "unit": "per 330ml can"},
    "sprite": {"cal": 140, "unit": "per 330ml can"},
    "fanta": {"cal": 160, "unit": "per 330ml can"},
    "lassi": {"cal": 180, "unit": "per glass"},
    "mango lassi": {"cal": 220, "unit": "per glass"},
    
    # Additional Items
    "kachori": {"cal": 150, "unit": "per piece"},
    "dhokla": {"cal": 160, "unit": "per 100g"},
    "idiyappam": {"cal": 120, "unit": "per serving"},
    "sevai": {"cal": 150, "unit": "per cup"},
    "kozhukattai": {"cal": 90, "unit": "per piece"},
}


# ==================== UTILITY FUNCTIONS ====================
def get_user_file(kind):
    """Returns per-user JSON file based on logged-in username and type."""
    user = session["user"].lower()
    return os.path.join(DATA_DIR, f"{user}_{kind}.json")


def read_json(file):
    """Read JSON data from file."""
    if not os.path.exists(file):
        return {}
    try:
        with open(file, "r") as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except json.JSONDecodeError:
        return {}


def write_json(file, data):
    """Write JSON data to file."""
    with open(file, "w") as f:
        json.dump(data, f, indent=4)


# ==================== DECORATORS ====================
def login_required(f):
    """Custom login required decorator."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


# ==================== AUTHENTICATION ROUTES ====================
@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in USERS and USERS[username] == password:
            session["user"] = username
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """Handle user logout."""
    session.pop("user", None)
    return redirect(url_for("login"))


# ==================== MAIN ROUTES ====================
@app.route("/")
@app.route("/home")
@login_required
def home():
    user = session["user"]

    # File paths (we use "meals" because /log writes to get_user_file("meals"))
    MEAL_FILE = get_user_file("meals")   # e.g. boo_meals.json
    GOAL_FILE = get_user_file("goal")    # e.g. boo_goal.json

    # Load JSON safely (returns {} when file missing/empty)
    meal_data = read_json(MEAL_FILE) or {}
    goal_data = read_json(GOAL_FILE) or {}

    # Today's date string
    today = datetime.now().strftime("%Y-%m-%d")

    # Meals logged for today (list)
    today_meals = meal_data.get(today, [])

    # Summary calculations
    consumed = sum(int(meal.get("calories", 0)) for meal in today_meals)
    target = goal_data.get("daily_goal", 0)
    remaining = target - consumed

    return render_template(
        "home.html",
        foods=FOOD_DATA,
        today=today,
        today_meals=today_meals,
        consumed=consumed,
        target=target,
        remaining=remaining
    )


@app.route('/update_today', methods=['POST'])
def update_today():
    data = request.json
    with open("data/boo_meals.json", "w") as f:
        json.dump(data, f, indent=4)
    return jsonify({"status": "success"})

@app.route('/data/<path:filename>')
def serve_data(filename):
    return send_from_directory('data', filename)


@app.route('/boo_meals.json')
def serve_boo_meals():
    base_path = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(base_path, "boo_meals.json")

# ---------- Replace the old dashboard() with this ----------
@app.route("/dashboard")
@login_required
def dashboard():
    """Dashboard with statistics, streak, latest weight and goal tracking."""
    DATA_FILE = get_user_file("meals")
    WEIGHT_FILE = get_user_file("weights")
    GOAL_FILE = get_user_file("goals")

    meal_data = read_json(DATA_FILE)           # { "2025-11-08": [ {...}, ... ], ... }
    weight_data = read_json(WEIGHT_FILE) or {} # { "2025-11-08": 67.3, ... }
    goal_data = read_json(GOAL_FILE) or {}     # { "daily_goal": 1800, ... }

    calories_per_day = {}
    goal_hits = {}

    # Build calories_per_day and goal_hits for each date present in meal_data
    for date, meals in meal_data.items():
        total = sum(int(m.get("calories", 0)) for m in meals)
        calories_per_day[date] = total

        if goal_data and "daily_goal" in goal_data:
            goal = goal_data["daily_goal"]
            # If goal_type exists, use logic similar to existing app
            if goal_data.get("goal_type") == "lose":
                goal_hits[date] = total <= goal
            else:
                goal_hits[date] = total >= goal

    # Today's date
    today_dt = datetime.now()
    today = today_dt.strftime("%Y-%m-%d")

    # Today's calories consumed (0 if none)
    consumed_today = calories_per_day.get(today, 0)

    # Today's goal (if set)
    target = goal_data.get("daily_goal", 0)

    # Compute streak: consecutive days up to today where meal_data[date] exists and is non-empty
    streak = 0
    check_date = today_dt
    while True:
        d = check_date.strftime("%Y-%m-%d")
        meals = meal_data.get(d, [])
        if meals and len(meals) > 0:
            streak += 1
            check_date = check_date - timedelta(days=1)
        else:
            break

    # Latest weight (most recent date in weight_data)
    latest_weight = None
    latest_weight_date = None
    if weight_data:
        # sort dates and pick the latest
        try:
            sorted_dates = sorted(weight_data.keys())
            latest_weight_date = sorted_dates[-1]
            latest_weight = weight_data[latest_weight_date]
        except Exception:
            # fallback: pick max key lexicographically
            latest_weight_date = max(weight_data.keys())
            latest_weight = weight_data[latest_weight_date]

    return render_template(
        "dashboard.html",
        calories=calories_per_day,
        weights=weight_data,
        goals=goal_data,
        goal_hits=goal_hits,
        datetime=datetime,
        streak=streak,
        latest_weight=latest_weight,
        latest_weight_date=latest_weight_date,
        consumed=consumed_today,
        target=target
    )
# ---------- end replacement ----------



@app.route("/tracker")
@login_required
def tracker():
    """Meal tracking page."""
    DATA_FILE = get_user_file("meals")
    data = read_json(DATA_FILE)
    return render_template("tracker.html", data=data)


# ==================== API ENDPOINTS ====================
@app.route("/calculate", methods=["POST"])
@login_required
def calculate():
    """Calculate calories for a food item."""
    data = request.get_json()
    food = data["food"].lower()
    amount = float(data["amount"])
    meal_type = data["meal"]

    if food not in FOOD_DATA:
        return jsonify({"error": "Food not found"}), 400

    info = FOOD_DATA[food]
    base_cal = info["cal"]
    unit = info["unit"]

    if "per" in unit and "g" in unit:
        base_g = int(unit.split("per")[1].strip().replace("g", ""))
        total_cal = round((amount / base_g) * base_cal, 2)
    elif "piece" in unit or "cup" in unit or "bowl" in unit:
        total_cal = round(amount * base_cal, 2)
    else:
        total_cal = base_cal

    return jsonify({
        "meal": meal_type,
        "food": food,
        "amount": amount,
        "unit": unit,
        "calories": total_cal
    })


@app.route("/log", methods=["POST"])
@login_required
def log_meal():
    """Log a meal entry."""
    DATA_FILE = get_user_file("meals")
    entry = request.get_json()
    date = entry.get("date") or datetime.now().strftime("%Y-%m-%d")
    data = read_json(DATA_FILE)

    if date not in data:
        data[date] = []
    data[date].append(entry)

    write_json(DATA_FILE, data)
    return jsonify({"message": "Meal logged successfully"})


@app.route("/log_weight", methods=["POST"])
@login_required
def log_weight():
    """Log weight entry."""
    WEIGHT_FILE = get_user_file("weights")
    entry = request.get_json()
    date = entry.get("date") or datetime.now().strftime("%Y-%m-%d")
    weight = entry.get("weight")

    weights = read_json(WEIGHT_FILE)
    weights[date] = weight
    write_json(WEIGHT_FILE, weights)

    return jsonify({"message": "Weight logged successfully"})


@app.route("/set_goal", methods=["POST"])
@login_required
def set_goal():
    """Set weight loss/gain goal."""
    GOAL_FILE = get_user_file("goals")
    entry = request.get_json()
    current_weight = float(entry.get("current_weight"))
    goal_type = entry.get("goal_type")  # 'lose' or 'gain'
    goal_rate = float(entry.get("goal_rate"))  # e.g., 0.5 kg/week

    # Estimate TDEE (simple version)
    # 1 kg fat ≈ 7700 kcal
    # To lose 0.5kg/week → 3850 kcal/week deficit → ~550 kcal/day
    calorie_adjustment = goal_rate * 1100  # 0.5kg ≈ 550 kcal/day
    base_tdee = 2200  # average maintenance for moderate activity

    if goal_type == "lose":
        daily_goal = base_tdee - calorie_adjustment
    else:
        daily_goal = base_tdee + calorie_adjustment

    goal_data = {
        "current_weight": current_weight,
        "goal_type": goal_type,
        "goal_rate": goal_rate,
        "daily_goal": round(daily_goal, 0)
    }

    write_json(GOAL_FILE, goal_data)
    return jsonify({"message": "Goal saved successfully", "goal": goal_data})


# ==================== RUN APPLICATION ====================
if __name__ == "__main__":
    app.run(debug=True)