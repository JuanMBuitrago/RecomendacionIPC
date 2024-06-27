# RecomendacionIPC

This is a FastAPI-based web application that provides product recommendations based on a given prompt and brand. The application uses TF-IDF vectorization and cosine similarity to find the most relevant products.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Example Request](#example-request)

## Installation

1. **Clone the repository**:
    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```

2. **Create and activate a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. **Run the FastAPI application**:
    ```bash
    uvicorn main:app --reload
    ```

2. **Access the application**:
    Open your browser and go to `http://127.0.0.1:8000`.

## API Endpoints

### GET `/recomendacion`

Get product recommendations based on a prompt and brand.

**Query Parameters**:
- `prompt` (str): The search prompt.
- `marca` (str): The brand of the products.

**Response**:
- Returns a list of recommended products with their codes, availability, and cost.

Example response:
```json
[
    {
        "Codigo": "Code1",
        "Existencia": 10,
    },
    {
        "Codigo": "Code2",
        "Existencia": 5,
    }
]
