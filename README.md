# Baseline Classifier

> **TL;DR** A minimal FastAPI service that receives chat messages, stores them in Postgres and replies with a **random** probability that a bot is present in the dialog.  
> Use it as a starting point for the **You are Bot**—replace the random predictor with your own model and climb the leaderboard!

---

## Table of Contents
1. [Key Features](#key-features)  
2. [Tech Stack](#tech-stack)  
3. [Folder Structure](#folder-structure)  
4. [Quick Start](#quick-start)  
   * [Local run (Python venv)](#local-run-python-venv)  
   * [Docker / Docker Compose](#docker--docker-compose)  
5. [API Reference](#api-reference)  
6. [Registering Your Classifier](#registering-your-classifier)  
7. [Development & Contribution](#development--contribution)  
8. [Authors](#authors)

---

## Key Features
| What | Why |
|------|-----|
| **`/predict` endpoint** | Receives a message and returns a probability that the dialog involves a bot |
| **FastAPI + Uvicorn** | Asynchronous HTTP service that is easy to extend |
| **PostgreSQL storage** | Persists incoming messages & predictions (useful for retraining/monitoring) |
| **Docker-first workflow** | Same image can be tested locally and pushed to the competition platform |
| **Random baseline** | Forces you to implement real inference logic 🚀 |

---

## Tech Stack
* **Python 3.9**  
* **FastAPI 0.95+** & **Uvicorn 0.22+**  
* **Transformers 4.31** – installed but **not yet used** (ready for your model)  
* **PostgreSQL 15** (via official Docker image)  
* **Docker & Docker Compose v3.9**

---

## Folder Structure
```text
baseline_classifier/
├── src/
│   ├── config.py          # DB & service settings
│   ├── database.py        # SQLAlchemy session + models
│   ├── main.py            # FastAPI application
│   ├── model_inference.py # ⬅️ put your ML code here
│   ├── schemas.py         # Pydantic IO schemas
│   └── .gitkeep
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
└── README.md
```


## Quick Start

### Local run (Python venv)

```bash
# 1 Clone repository
git clone <YOUR_FORK_URL>
cd baseline_classifier

# 2 Create virtual environment
python3.9 -m venv .venv
source .venv/bin/activate

# 3 Install dependencies
pip install -r requirements.txt

# 4 Export DB credentials (or define them in .env)
export DB_USER=student DB_PASSWORD=student_pass \
       DB_HOST=localhost DB_PORT=5432 DB_NAME=chat_db

# 5 Launch local Postgres (or use docker-compose up -d postgres)
docker run --rm -p 5432:5432 \
  -e POSTGRES_USER=$DB_USER \
  -e POSTGRES_PASSWORD=$DB_PASSWORD \
  -e POSTGRES_DB=$DB_NAME postgres:latest

# 6 Start the service
uvicorn src.main:app --reload
```

Service will be available at http://127.0.0.1:8000


### Docker / Docker Compose

```bash
# Build image
docker build -t baseline-classifier .

# Or spin up full stack (Postgres + service)
docker compose up --build
```


## API Reference

### POST /predict

Predict whether this is a message from bot.

```json
{
  "text": "Hi, how are you?",
  "dialog_id": "0f2d4682-d939-4af6-beb9-880a5da202a2",
  "id": "13ab658b-8463-4410-a747-33ea2dfb7b68",
  "participant_index": 0
}
```

### Response (Prediction)
```json
{
  "id": "814c9637-5f4a-4633-84d2-f86c7fa62a48",
  "message_id": "13ab658b-8463-4410-a747-33ea2dfb7b68",
  "dialog_id": "0f2d4682-d939-4af6-beb9-880a5da202a2",
  "participant_index": 0,
  "is_bot_probability": 0.42
}
```

is_bot_probability is currently uniformly random in [0, 1].
Replace the implementation in src/model_inference.py with your model.

## Registering Your Classifier
	1.	Fork this repo and hack away — swap the random logic for a model of your choice.
	2.	Build & push the Docker image to any registry accessible from the hackathon platform.
	3.	On the youare.bot site go to “Register classifier" and paste the image reference.
	4.	Make sure your container exposes /predict on port 443 (already done in docker-compose.yaml).
	5.	As soon as the health check passes, your classifier will appear on the leaderboard.

For the detailed step-by-step guide see the zoomcamp portal.

⸻

## Development & Contribution
	•	Create a feature branch off main.
	•	Follow PEP-8 & auto-format with black.
	•	Add type hints; if you add endpoints, extend schemas.py.

⸻

## Authors
	•	👤 github.com/aguschin
	•	👤 github.com/semchinov
	•	👤 github.com/Funnycats14


Happy hacking & good luck on the leaderboard! 🎉
