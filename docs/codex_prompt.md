# NutriMind Codex Prompt

Goal:
Create a cross-platform application (React Native + FastAPI backend) that merges Apple Health fitness data with user food tracking via text, barcode, and photo to power an AI Nutritionist that offers real-time, personalized guidance.

---

## 1. System Overview

App Name: NutriMind  
Architecture Summary:
- Frontend: React Native (iOS + Android)
- Backend: FastAPI + PostgreSQL (or Firestore)
- AI Components:
  - Vision model for photo-based meal recognition
  - NLP parser for text/voice food entry
  - GPT-based "AI Nutritionist" for insights
- Auth: Apple Sign-In → JWT (Bearer)
- External APIs: Apple HealthKit, OpenFoodFacts, USDA FoodData Central

---

## 2. Data Model Overview

| Table        | Fields                                                                                     | Purpose                                  |
|--------------|--------------------------------------------------------------------------------------------|------------------------------------------|
| users        | id, email, name, age, height, weight, goalCalories, goalProtein, created_at                | User profile and settings                |
| meals        | id, user_id, timestamp, meal_type, food_items[], total_calories, macros (protein, carbs, fat), source (photo/text/barcode) | Logged meals                             |
| photos       | id, meal_id, image_url, recognition_results, portion_estimate                              | Meal photo data                          |
| fitness_data | id, user_id, timestamp, steps, active_kcal, heart_rate, sleep_hours                        | Synced Apple Health metrics              |
| feedback     | id, user_id, timestamp, feedback_text, ai_model_version                                    | AI responses to user data                |

---

## 3. Authentication

### JWT Auth Flow
- `POST /auth/apple` — exchange Apple Sign-In token for backend JWT.
- All subsequent requests require `Authorization: Bearer <token>` header.

---

## 4. Endpoint Definitions

### 4.1 `POST /auth/apple`
Exchange Apple Sign-In credential for a backend session token.

**Request**
```json
{
  "apple_identity_token": "string"
}
```

**Response 200**
```json
{
  "access_token": "jwt_token",
  "token_type": "bearer",
  "user": {
    "id": 12,
    "email": "user@example.com",
    "name": "Evan"
  }
}
```

**Errors**
- 400 `invalid_token`
- 500 `internal_error`

---

### 4.2 `POST /syncHealth`
Ingest Apple Health data (steps, workouts, calories burned, etc.).

**Auth:** Bearer token required.

**Request**
```json
{
  "date": "2025-11-02",
  "steps": 8900,
  "active_kcal": 640,
  "heart_rate_avg": 78,
  "sleep_hours": 7.2,
  "weight": 259.1
}
```

**Response 200**
```json
{
  "message": "Health data synced successfully",
  "record_id": 4412
}
```

**Errors**
- 400 `missing_field`
- 401 `unauthorized`
- 500 `internal_error`

---

### 4.3 `POST /addMeal`
Log a new meal via text, photo, or barcode.

**Auth:** Bearer token required.  
**Content-Type:** `multipart/form-data` (if photo) or `application/json`.

**Request**
```json
{
  "meal_type": "lunch",
  "timestamp": "2025-11-02T12:30:00Z",
  "input_method": "photo",
  "photo_url": "https://s3.amazonaws.com/nutrimind/meal123.jpg",
  "food_items": [
    { "name": "bean chili", "quantity": "1 cup" },
    { "name": "parmesan cheese", "quantity": "1 tbsp" }
  ]
}
```

**Response 200**
```json
{
  "meal_id": 1003,
  "total_calories": 420,
  "macros": { "protein": 25, "carbs": 35, "fat": 18 },
  "analysis_source": "AI image recognition",
  "feedback_summary": "Solid protein intake. A bit high in sodium."
}
```

**Errors**
- 400 `invalid_input`
- 401 `unauthorized`
- 413 `file_too_large`
- 500 `internal_error`

---

### 4.4 `POST /analyzePhoto`
Upload a meal photo for visual recognition and portion estimation.

**Auth:** Bearer token required.  
**Content-Type:** `multipart/form-data`

**Request**
```
file: image.jpg
```

**Response 200**
```json
{
  "predictions": [
    { "food": "spaghetti", "confidence": 0.93, "calories_est": 520 },
    { "food": "meatballs", "confidence": 0.87, "calories_est": 320 }
  ],
  "total_estimated_calories": 840
}
```

**Errors**
- 400 `no_image_found`
- 415 `unsupported_media_type`
- 500 `model_error`

---

### 4.5 `POST /aiFeedback`
Generate AI-driven nutrition advice combining meal + fitness data.

**Auth:** Bearer token required.

**Request**
```json
{
  "context": {
    "user_profile": {
      "age": 45,
      "height_cm": 183,
      "weight_kg": 117,
      "goal_calories": 1800,
      "goal_protein": 150
    },
    "recent_meals": [
      { "meal_type": "breakfast", "calories": 350, "protein": 20 },
      { "meal_type": "lunch", "calories": 650, "protein": 40 }
    ],
    "fitness_data": {
      "steps": 9200,
      "active_kcal": 640,
      "heart_rate_avg": 78
    }
  }
}
```

**Response 200**
```json
{
  "feedback": "You're on track today. You're slightly low on carbs—consider adding fruit or oats tomorrow morning.",
  "total_intake": {
    "calories": 1000,
    "protein": 60,
    "carbs": 90,
    "fat": 25
  },
  "ai_model_version": "gpt5-nutrition-1.1"
}
```

**Errors**
- 400 `invalid_context`
- 401 `unauthorized`
- 429 `rate_limited`
- 500 `ai_service_error`

---

### 4.6 `GET /dailySummary`
Retrieve aggregated intake + expenditure for a given day.

**Auth:** Bearer token required.  
**Query Parameters:** `date=YYYY-MM-DD`

**Response 200**
```json
{
  "date": "2025-11-02",
  "calories_in": 1675,
  "calories_out": 640,
  "macros": { "protein": 120, "carbs": 140, "fat": 55 },
  "balance": "+1035 kcal",
  "feedback": "Good balance. Protein target nearly met."
}
```

**Errors**
- 400 `invalid_date`
- 401 `unauthorized`
- 404 `no_data_found`

---

### 4.7 `GET /weeklySummary`
Return weekly trend data and AI highlights.

**Auth:** Bearer token required.

**Response 200**
```json
{
  "week_start": "2025-10-27",
  "week_end": "2025-11-02",
  "avg_calories_in": 1820,
  "avg_calories_out": 620,
  "weight_change": -1.2,
  "ai_summary": "Your protein intake was consistent, but fiber averaged 17g/day—aim for 25g+ next week."
}
```

---

## 5. Error Handling

| Code | Meaning                             | Typical Response                                             |
|------|-------------------------------------|--------------------------------------------------------------|
| 400  | Bad Request – missing/invalid data  | {"error":"invalid_input","message":"Missing calories field"} |
| 401  | Unauthorized – missing/expired token| {"error":"unauthorized","message":"Invalid or expired JWT"} |
| 404  | Not Found – record missing          | {"error":"not_found","message":"Meal not found"}          |
| 415  | Unsupported Media Type              | {"error":"unsupported_format"}                              |
| 429  | Too Many Requests                   | {"error":"rate_limited","retry_after":60}                  |
| 500  | Internal Server Error               | {"error":"server_error"}                                    |

---

## 6. AI Integration Guidelines
- `ai_service.py` should expose `generate_feedback(context)` which calls an LLM API.
- Use OpenAI or local Codex model endpoint.
- Include `temperature = 0.4` for consistent feedback tone.
- Cache responses for repeated queries within 24 hours to reduce API load.

---

## 7. Expected Output from Codex

When you feed this prompt to a Codex tool, request code generation for:
- `main.py` (FastAPI entrypoint)
- `models.py` (Pydantic schemas + SQLAlchemy models)
- `routes/` (directory with each endpoint as a module)
- `ai_service.py` (LLM interface)
- `database.py` (DB engine + session manager)
- `README.md` (setup, environment vars, run instructions)

