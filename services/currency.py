import requests
import re
from typing import Tuple, Optional
import json


class CurrencyError(Exception):
    """Exception raised for currency conversion errors."""
    pass


class CurrencyClient:
    def __init__(self, timeout_seconds=10):
        self.timeout_seconds = timeout_seconds
    
    def is_currency_query(self, text: str) -> bool:
        """Check if the text is a currency conversion query."""
        text_lower = text.lower()
        
        # Padrões que indicam conversão de moeda
        patterns = [
            r"convert\s+\d+",
            r"\d+\s+[a-z]{3}\s+(?:to|in)\s+[a-z]{3}",
            r"how\s+much\s+is\s+\d+",
            r"quanto\s+(?:é|vale)\s+\d+",
            r"converter\s+\d+"
        ]
        
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def extract_conversion_data(self, text: str) -> Optional[Tuple[float, str, str]]:
        """Extract amount, from_currency, and to_currency from text."""
        
        # Padrões para diferentes formatos de consulta
        patterns = [
            # "convert 100 USD to BRL", "100 USD to BRL"
            r"(?:convert\s+)?(\d+(?:\.\d+)?)\s+([A-Za-z]{3})\s+(?:to|in)\s+([A-Za-z]{3})",
            # "how much is 100 USD in BRL"
            r"how\s+much\s+is\s+(\d+(?:\.\d+)?)\s+([A-Za-z]{3})\s+in\s+([A-Za-z]{3})",
            # "quanto é 100 USD em BRL", "quanto vale 100 USD em BRL"
            r"quanto\s+(?:é|vale)\s+(\d+(?:\.\d+)?)\s+([A-Za-z]{3})\s+em\s+([A-Za-z]{3})",
            # "converter 100 USD para BRL"
            r"converter\s+(\d+(?:\.\d+)?)\s+([A-Za-z]{3})\s+para\s+([A-Za-z]{3})"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = float(match.group(1))
                from_cur = match.group(2).upper()
                to_cur = match.group(3).upper()
                return amount, from_cur, to_cur
        
        return None
    
    def convert(self, amount: float, from_currency: str, to_currency: str) -> str:
        """Convert currency using free APIs with fallback options."""
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        # Se as moedas são iguais, retornar diretamente
        if from_currency == to_currency:
            return f"{amount} {from_currency} = {amount} {to_currency} (Same currency)"
        
        # Tentar APIs em ordem de preferência
        apis_to_try = [
            self._try_exchangerate_api,
            self._try_fixer_free,
            self._try_currencyapi_free,
            self._try_hardcoded_rates
        ]
        
        last_error = None
        
        for api_func in apis_to_try:
            try:
                return api_func(amount, from_currency, to_currency)
            except Exception as e:
                last_error = str(e)
                continue
        
        # Se todas falharam
        raise CurrencyError(f"All currency conversion methods failed. Last error: {last_error}")
    
    def _try_exchangerate_api(self, amount: float, from_cur: str, to_cur: str) -> str:
        """Usar exchangerate-api.com (100% gratuita)"""
        url = f"https://api.exchangerate-api.com/v4/latest/{from_cur}"
        
        resp = requests.get(url, timeout=self.timeout_seconds)
        resp.raise_for_status()
        
        data = resp.json()
        
        if "rates" not in data or to_cur not in data["rates"]:
            raise CurrencyError(f"Currency {to_cur} not supported")
        
        rate = data["rates"][to_cur]
        result = amount * rate
        
        return f"{amount} {from_cur} = {result:.2f} {to_cur} (Rate: {rate:.6f})"
    
    def _try_fixer_free(self, amount: float, from_cur: str, to_cur: str) -> str:
        """Usar fixer.io versão gratuita limitada"""
        # Fixer gratuito só permite EUR como base
        if from_cur != "EUR":
            # Precisamos converter via EUR
            url1 = "https://api.fixer.io/latest?base=EUR"
            resp1 = requests.get(url1, timeout=self.timeout_seconds)
            resp1.raise_for_status()
            data1 = resp1.json()
            
            if not data1.get("success", True):
                raise CurrencyError("Fixer API limit reached")
            
            if from_cur not in data1["rates"] or to_cur not in data1["rates"]:
                raise CurrencyError("Currency not supported by Fixer free tier")
            
            # Converter: from_cur -> EUR -> to_cur
            from_to_eur = 1 / data1["rates"][from_cur]  # from_cur para EUR
            eur_to_to = data1["rates"][to_cur]          # EUR para to_cur
            rate = from_to_eur * eur_to_to
        else:
            # EUR como base, conversão direta
            url = f"https://api.fixer.io/latest?base=EUR&symbols={to_cur}"
            resp = requests.get(url, timeout=self.timeout_seconds)
            resp.raise_for_status()
            data = resp.json()
            
            if not data.get("success", True):
                raise CurrencyError("Fixer API limit reached")
            
            rate = data["rates"][to_cur]
        
        result = amount * rate
        return f"{amount} {from_cur} = {result:.2f} {to_cur} (Rate: {rate:.6f})"
    
    def _try_currencyapi_free(self, amount: float, from_cur: str, to_cur: str) -> str:
        """Usar currencyapi.com versão gratuita"""
        url = f"https://api.currencyapi.com/v3/latest?base_currency={from_cur}&currencies={to_cur}"
        
        resp = requests.get(url, timeout=self.timeout_seconds)
        resp.raise_for_status()
        
        data = resp.json()
        
        if "data" not in data or to_cur not in data["data"]:
            raise CurrencyError("CurrencyAPI free tier limit reached")
        
        rate = data["data"][to_cur]["value"]
        result = amount * rate
        
        return f"{amount} {from_cur} = {result:.2f} {to_cur} (Rate: {rate:.6f})"
    
    def _try_hardcoded_rates(self, amount: float, from_cur: str, to_cur: str) -> str:
        """Usar taxas hardcoded como último recurso (aproximadas)"""
        
        # Taxas aproximadas em relação ao USD (atualizadas periodicamente)
        usd_rates = {
            "USD": 1.0,
            "EUR": 0.85,
            "GBP": 0.73,
            "JPY": 110.0,
            "BRL": 5.0,
            "CAD": 1.25,
            "AUD": 1.35,
            "CHF": 0.92,
            "CNY": 6.4,
            "INR": 74.0
        }
        
        if from_cur not in usd_rates or to_cur not in usd_rates:
            raise CurrencyError(f"Currency pair {from_cur}/{to_cur} not supported in fallback rates")
        
        # Converter via USD
        from_to_usd = 1 / usd_rates[from_cur]  # from_cur para USD
        usd_to_to = usd_rates[to_cur]          # USD para to_cur
        rate = from_to_usd * usd_to_to
        
        result = amount * rate
        
        return f"{amount} {from_cur} = {result:.2f} {to_cur} (Approx. rate: {rate:.6f}) [OFFLINE]"
    
    def handle_query(self, text: str) -> str:
        """Handle a currency conversion query from text."""
        conversion_data = self.extract_conversion_data(text)
        
        if not conversion_data:
            raise CurrencyError(
                "Could not parse currency query. "
                "Try formats like: 'convert 100 USD to BRL' or '100 USD to EUR'"
            )
        
        amount, from_cur, to_cur = conversion_data
        return self.convert(amount, from_cur, to_cur)