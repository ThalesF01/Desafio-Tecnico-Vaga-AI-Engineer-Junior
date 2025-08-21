# main.py — AI Assistant with Groq OpenAI-compatible API
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

from utils.config import load_config
from utils.math_utils import is_math_question, extract_expression
from calculator.evaluator import safe_eval, EvalError
from services.weather import WeatherClient, WeatherError
from services.currency import CurrencyClient, CurrencyError


# --- Load .env ---
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# --- Load config.json ---
config_path = Path(__file__).parent / "config.json"
cfg = load_config(config_path)

# --- Read env / config for LLM ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_BASE = os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1")
MODEL = os.getenv("GROQ_MODEL", cfg["llm"]["model"])
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", str(cfg["llm"]["temperature"])))
MAX_TOKENS = int(cfg["llm"]["max_tokens"])

if not GROQ_API_KEY:
    raise RuntimeError("Missing GROQ_API_KEY in .env")

# --- Instantiate OpenAI client for Groq ---
client = OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_API_BASE)

# --- Weather client ---
weather_client = WeatherClient(
    geocoding_url=cfg["weather"]["geocoding_url"],
    forecast_url=cfg["weather"]["forecast_url"],
    timeout_seconds=int(cfg["weather"]["timeout_seconds"]),
)

# --- Currency client ---
currency_client = CurrencyClient(timeout_seconds=10)

# --- UI messages ---
UI_MATH_MSG = cfg["ui"]["math_message"]
UI_LLM_MSG = cfg["ui"]["llm_message"]
UI_WEATHER_MSG = cfg["ui"]["weather_message"]
UI_CURRENCY_MSG = cfg["ui"]["currency_message"]

# --- Utilities ---
def timed(func, *args, **kwargs):
    start = time.perf_counter()
    try:
        out = func(*args, **kwargs)
        ok = True
        return out, ok, time.perf_counter() - start
    except Exception as e:
        return e, False, time.perf_counter() - start

def format_response(source, content, elapsed_time):
    return f"""
------------------------------------

Assistant Response

Source: {source}

{content}

(response time: {elapsed_time*1000:.0f} ms)

------------------------------------
"""

# --- Handlers ---
def ask_llm(question: str) -> str:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": question}],
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )
    return resp.choices[0].message.content.strip()

def handle_math(question: str) -> str:
    expr = extract_expression(question)
    if not expr:
        raise EvalError("Could not extract a valid math expression.")
    result = safe_eval(expr)
    if isinstance(result, float) and result.is_integer():
        result = int(result)
    return f"{expr} = {result}"

def handle_weather(question: str) -> str:
    loc_query = weather_client.extract_location(question)
    if not loc_query:
        raise WeatherError("Could not detect a location. Try: 'weather in <City>'.")
    loc = weather_client.geocode(loc_query)
    return weather_client.current_weather(loc)

def handle_currency(question: str) -> str:
    """Handle currency conversion using the CurrencyClient."""
    return currency_client.handle_query(question)

# --- Main ---
WELCOME_BANNER = """
╔══════════════════════════════════════════════╗
║       Welcome to the AI Assistant!           ║
╠══════════════════════════════════════════════╣
║ You can ask questions, perform calculations, ║
║ convert currencies, or check the weather.    ║
║                                              ║
║ Examples:                                    ║
║ • Who was Albert Einstein?                   ║
║ • What is 128 * 46?                          ║
║ • Weather in New York                        ║
║ • Convert 100 USD to BRL                     ║
╠══════════════════════════════════════════════╣
║ Type 'exit', 'quit', or 'sair' to leave.     ║
╚══════════════════════════════════════════════╝
"""

if __name__ == "__main__":
    print(WELCOME_BANNER)
    while True:
        try:
            q = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if not q:
            continue
        if q.lower() in ("exit", "quit", "sair"):
            break

        # 1) Math path
        if is_math_question(q):
            print(UI_MATH_MSG)
            result, ok, dt = timed(handle_math, q)
            print(format_response("🧮 Calculator", result if ok else f"Math error — {result}", dt))
            continue

        # 2) Weather path
        if weather_client.is_weather_query(q):
            print(UI_WEATHER_MSG)
            result, ok, dt = timed(handle_weather, q)
            print(format_response("☁️ Weather API", result if ok else f"Weather error — {result}", dt))
            continue

        # 3) Currency conversion
        if currency_client.is_currency_query(q):
            print(UI_CURRENCY_MSG)
            result, ok, dt = timed(handle_currency, q)
            print(format_response("💱 Currency API", result if ok else f"Currency error — {result}", dt))
            continue

        # 4) LLM path (fallback)
        print(UI_LLM_MSG)
        result, ok, dt = timed(ask_llm, q)
        print(format_response("💡 LLM", result if ok else f"LLM error — {result}", dt))