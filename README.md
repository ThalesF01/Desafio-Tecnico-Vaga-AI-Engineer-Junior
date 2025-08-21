# AI Assistant – Groq OpenAI-Compatible

## Overview

This project is an **AI-powered assistant** that combines multiple functionalities in a single interface. The assistant can:

* Answer general knowledge questions using a **Groq OpenAI-compatible model**.
* Perform **mathematical calculations** using a local calculator.
* Retrieve **current weather information** via Open-Meteo API.
* Convert **currencies** using ExchangeRate API.

It demonstrates the integration of a **Large Language Model (LLM)** with external tools and local utilities, providing a robust multi-functional assistant.

---

## Features

### 1. Large Language Model (LLM)

* Uses **Groq’s OpenAI-compatible API** to answer questions.
* Example: *“Who was Albert Einstein?”*.
* Handles fallback when no other tool is applicable.

### 2. Calculator

* Evaluates mathematical expressions safely.
* Example: *“128 \* 46”*.
* Ensures proper integer/floating point results.

### 3. Weather

* Detects queries like *“Weather in New York”*.
* Uses **Nominatim** for geocoding and **Open-Meteo** for weather.
* Returns temperature, wind speed, and description.

### 4. Currency Conversion

* Handles queries like *“Convert 100 USD to BRL”*.
* Uses **ExchangeRate API** to retrieve real-time conversion rates.
* Provides clear results and handles errors gracefully.

---

## Project Structure

```text
project-root/
├─ main.py                 # Entry point: reads user input and routes to the correct tool
├─ config.json             # Configuration for LLM, APIs, and UI messages
├─ .env                    # Sensitive environment variables (API keys)
├─ utils/
│  ├─ config.py            # Loads config.json
│  └─ math_utils.py        # Detects math questions and extracts expressions
├─ calculator/
│  └─ evaluator.py         # Safely evaluates mathematical expressions
├─ services/
│  ├─ weather.py           # Weather API client with geocoding and forecast
│  └─ currency.py          # Currency conversion API client
└─ README.md
```

---

## Note about `.env`

All sensitive information, such as your `GROQ_API_KEY`, should be placed in the `.env` file. **Do not commit this file to your repository.**

Example:

```env
GROQ_API_KEY=<your-api-key>
GROQ_API_BASE=https://api.groq.com/openai/v1
GROQ_MODEL=compound-beta-mini
```

---

## How It Works (Decision Logic)

1. **User Input**
   The assistant continuously waits for user input.

2. **Decision Flow**
   Based on the user input, the assistant selects the correct tool:

   * Math question → Calculator
   * Weather query → Weather API
   * Currency conversion → Currency API
   * Other/general question → Groq LLM

3. **Response Formatting**
   Each tool returns a formatted response including elapsed time.
   Example:

```text
------------------------------------
Assistant Response
Source: 💱 Currency API
100 USD = 512.34 BRL
(response time: 500 ms)
------------------------------------
```

---

## Installation & Execution

### Clone the repository

```bash
git clone https://github.com/ThalesF01/Desafio-Tecnico-Vaga-AI-Engineer-Junior.git
cd Desafio-Tecnico-Vaga-AI-Engineer-Junior
```

### Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Set environment variables in `.env`

```env
GROQ_API_KEY=<your-api-key>
GROQ_API_BASE=https://api.groq.com/openai/v1
GROQ_MODEL=compound-beta-mini
```

### Run the assistant

```bash
python main.py
```

---

## What I Learned

* How to **integrate a Groq LLM** into a Python project.
* How to **use APIs safely** and handle errors (weather, currency).
* How to **organize code modularly**, separating concerns (calculator, weather, LLM, utils).
* How to **design a decision flow** for selecting the right tool based on user input.

---

## What I Would Do With More Time

* Implement a **frontend interface** for a better user experience.
* Build **advanced context management (memory)** to remember past conversations.
* Create **more complex LLM interactions**, including multi-turn Q\&A and dynamic reasoning.
* Add more **“superpowers”**, e.g., news summaries, scheduling tasks, or reminders.
* Improve **natural language parsing** for currency and math questions (support more formats, words, and symbols).
