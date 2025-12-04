# Healthcare Symptom Checker

A web application built using FastAPI and PostgreSQL that leverages a Large Language Model (LLM) to provide educational information based on user-provided symptoms. The application offers a user-friendly interface for checking symptoms and viewing a history of past queries.

## ✨ Features

* **Symptom Analysis:** Users can input symptoms and receive a structured JSON response from an AI model.
* **Safety-Focused Output:** The model is strictly instructed to provide possible *condition categories*, red flags, and general next steps, explicitly avoiding diagnoses or medical advice.
* **Query History:** Stores and displays the last 10 queries using a PostgreSQL database.
* **Modern Frontend:** Responsive design with a clean, dark-themed background and a scrollable history modal.

## ⚙️ Technologies Used

* **Backend Framework:** FastAPI (Python)
* **Database:** PostgreSQL
* **LLM Integration:** OpenAI Python Client (used to communicate with Gemini API)
* **Frontend:** HTML, CSS, JavaScript (Vanilla)
* **Environment Management:** `python-dotenv`

## 🚀 Setup and Installation

### Prerequisites

1.  Python 3.9+
2.  PostgreSQL Database instance

### 1. Environment Variables

Create a file named `.env` in the project root directory and populate it with your database and API credentials: