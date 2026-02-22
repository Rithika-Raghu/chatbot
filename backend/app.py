from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import json
import datetime
import requests
import re
import random
import string
import base64
from datetime import timedelta

app = Flask(__name__)
CORS(app)

# Initialize Groq client
client = OpenAI(
    api_key="Your Api Key",
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "llama-3.3-70b-versatile"

# Define ALL tools
tools = [
    # TIME & DATE TOOLS
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Get current date and time",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_age",
            "description": "Calculate age from birth date",
            "parameters": {
                "type": "object",
                "properties": {
                    "birth_date": {"type": "string", "description": "Birth date in YYYY-MM-DD format"}
                },
                "required": ["birth_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "days_until",
            "description": "Calculate days until a future date",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Target date in YYYY-MM-DD format"}
                },
                "required": ["date"]
            }
        }
    },
    
    # MATH TOOLS
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Calculate mathematical expressions",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Math expression like '2+2' or '10*5'"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "is_prime",
            "description": "Check if a number is prime",
            "parameters": {
                "type": "object",
                "properties": {
                    "number": {"type": "integer", "description": "Number to check"}
                },
                "required": ["number"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "factorial",
            "description": "Calculate factorial of a number",
            "parameters": {
                "type": "object",
                "properties": {
                    "number": {"type": "integer", "description": "Number for factorial"}
                },
                "required": ["number"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fibonacci",
            "description": "Generate Fibonacci sequence",
            "parameters": {
                "type": "object",
                "properties": {
                    "count": {"type": "integer", "description": "How many numbers to generate"}
                },
                "required": ["count"]
            }
        }
    },
    
    # INFORMATION TOOLS
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"}
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_wikipedia",
            "description": "Search Wikipedia for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_random_fact",
            "description": "Get a random interesting fact",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_joke",
            "description": "Get a random joke",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_quote",
            "description": "Get an inspirational quote",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    
    # TEXT TOOLS
    {
        "type": "function",
        "function": {
            "name": "count_words",
            "description": "Count words in text",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to count words in"}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reverse_text",
            "description": "Reverse text",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to reverse"}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "text_to_uppercase",
            "description": "Convert text to uppercase",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to convert"}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "text_to_lowercase",
            "description": "Convert text to lowercase",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to convert"}
                },
                "required": ["text"]
            }
        }
    },
    
    # CONVERSION TOOLS
    {
        "type": "function",
        "function": {
            "name": "convert_currency",
            "description": "Convert currency (mock exchange rates)",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number", "description": "Amount to convert"},
                    "from_currency": {"type": "string", "description": "Source currency (USD, EUR, INR, etc)"},
                    "to_currency": {"type": "string", "description": "Target currency"}
                },
                "required": ["amount", "from_currency", "to_currency"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "convert_temperature",
            "description": "Convert temperature between units",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {"type": "number", "description": "Temperature value"},
                    "from_unit": {"type": "string", "description": "Source unit (C, F, K)"},
                    "to_unit": {"type": "string", "description": "Target unit (C, F, K)"}
                },
                "required": ["value", "from_unit", "to_unit"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "encode_base64",
            "description": "Encode text to Base64",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to encode"}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "decode_base64",
            "description": "Decode Base64 to text",
            "parameters": {
                "type": "object",
                "properties": {
                    "encoded": {"type": "string", "description": "Base64 encoded string"}
                },
                "required": ["encoded"]
            }
        }
    },
    
    # RANDOM/FUN TOOLS
    {
        "type": "function",
        "function": {
            "name": "roll_dice",
            "description": "Roll dice",
            "parameters": {
                "type": "object",
                "properties": {
                    "sides": {"type": "integer", "description": "Number of sides on the dice (default 6)"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "flip_coin",
            "description": "Flip a coin",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_password",
            "description": "Generate a random password",
            "parameters": {
                "type": "object",
                "properties": {
                    "length": {"type": "integer", "description": "Password length (default 12)"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "random_number",
            "description": "Generate random number in range",
            "parameters": {
                "type": "object",
                "properties": {
                    "min": {"type": "integer", "description": "Minimum value"},
                    "max": {"type": "integer", "description": "Maximum value"}
                },
                "required": ["min", "max"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "magic_8ball",
            "description": "Get a Magic 8-Ball answer",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }
]

# ============================================
# TOOL IMPLEMENTATIONS
# ============================================

# TIME & DATE TOOLS
def get_time():
    now = datetime.datetime.now()
    return {
        "tool": "Clock ⏰",
        "input": "Current time",
        "output": now.strftime('%A, %B %d, %Y at %I:%M:%S %p'),
        "success": True
    }

def calculate_age(birth_date):
    try:
        birth = datetime.datetime.strptime(birth_date, '%Y-%m-%d')
        today = datetime.datetime.now()
        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        return {
            "tool": "Age Calculator 🎂",
            "input": birth_date,
            "output": f"You are {age} years old",
            "success": True
        }
    except:
        return {"tool": "Age Calculator 🎂", "input": birth_date, "output": "Invalid date format", "success": False}

def days_until(date):
    try:
        target = datetime.datetime.strptime(date, '%Y-%m-%d')
        today = datetime.datetime.now()
        days = (target - today).days
        return {
            "tool": "Countdown ⏳",
            "input": date,
            "output": f"{days} days until {date}" if days >= 0 else f"{abs(days)} days ago",
            "success": True
        }
    except:
        return {"tool": "Countdown ⏳", "input": date, "output": "Invalid date", "success": False}

# MATH TOOLS
def calculator(expression):
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return {"tool": "Calculator 🧮", "input": expression, "output": f"{expression} = {result}", "success": True}
    except Exception as e:
        return {"tool": "Calculator 🧮", "input": expression, "output": f"Error: {str(e)}", "success": False}

def is_prime(number):
    if number < 2:
        result = "No"
    else:
        for i in range(2, int(number ** 0.5) + 1):
            if number % i == 0:
                result = "No"
                break
        else:
            result = "Yes"
    return {"tool": "Prime Checker 🔢", "input": str(number), "output": f"{number} is prime: {result}", "success": True}

def factorial(number):
    if number < 0:
        return {"tool": "Factorial ❗", "input": str(number), "output": "Error: Negative number", "success": False}
    result = 1
    for i in range(1, number + 1):
        result *= i
    return {"tool": "Factorial ❗", "input": str(number), "output": f"{number}! = {result}", "success": True}

def fibonacci(count):
    if count <= 0:
        return {"tool": "Fibonacci 🔢", "input": str(count), "output": "Count must be positive", "success": False}
    fib = [0, 1]
    for i in range(2, min(count, 20)):
        fib.append(fib[-1] + fib[-2])
    return {"tool": "Fibonacci 🔢", "input": str(count), "output": str(fib[:count]), "success": True}

# INFORMATION TOOLS
def get_weather(city):
    weather_db = {
        "Chennai": {"temp": "32°C", "condition": "Sunny ☀️", "humidity": "70%"},
        "Mumbai": {"temp": "28°C", "condition": "Cloudy ☁️", "humidity": "80%"},
        "Delhi": {"temp": "25°C", "condition": "Clear 🌤️", "humidity": "45%"},
        "Bangalore": {"temp": "26°C", "condition": "Partly Cloudy ⛅", "humidity": "60%"},
        "New York": {"temp": "15°C", "condition": "Rainy 🌧️", "humidity": "65%"},
        "London": {"temp": "12°C", "condition": "Foggy 🌫️", "humidity": "85%"},
        "Tokyo": {"temp": "20°C", "condition": "Clear 🌤️", "humidity": "55%"},
    }
    city_title = city.title()
    data = weather_db.get(city_title, {"temp": "25°C", "condition": "Unknown ❓", "humidity": "60%"})
    return {
        "tool": "Weather Service 🌤️",
        "input": city,
        "output": f"{city_title}: {data['temp']}, {data['condition']}, Humidity: {data['humidity']}",
        "success": True
    }

def search_wikipedia(query):
    try:
        # Properly capitalize the query for Wikipedia
        formatted_query = "_".join(word.capitalize() for word in query.strip().split())
        
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{formatted_query}"
        
        # Wikipedia requires a User-Agent header
        headers = {
            'User-Agent': 'ChatbotApp/1.0 (Educational Purpose; contact@example.com)',
            'Accept': 'application/json'
        }
        
        print(f"  📚 Fetching: {url}")
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"  📚 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if it's a disambiguation page
            if data.get('type') == 'disambiguation':
                return {
                    "tool": "Wikipedia 📚",
                    "input": query,
                    "output": f"Multiple results found for '{query}'. Please be more specific.",
                    "success": False
                }
            
            extract = data.get('extract', '')
            
            if extract:
                summary = extract[:500] + "..." if len(extract) > 500 else extract
                return {
                    "tool": "Wikipedia 📚",
                    "input": query,
                    "output": summary,
                    "success": True
                }
            else:
                return {
                    "tool": "Wikipedia 📚",
                    "input": query,
                    "output": "No information found",
                    "success": False
                }
                
        elif response.status_code == 404:
            # Try alternative formats
            alternatives = [
                query.replace(' ', '_'),  # Original with underscores
                query.title().replace(' ', '_'),  # Title case
                query.upper().replace(' ', '_')   # Upper case
            ]
            
            for alt_query in alternatives:
                url_alt = f"https://en.wikipedia.org/api/rest_v1/page/summary/{alt_query}"
                response_alt = requests.get(url_alt, headers=headers, timeout=10)
                
                if response_alt.status_code == 200:
                    data = response_alt.json()
                    extract = data.get('extract', '')
                    if extract:
                        summary = extract[:500] + "..." if len(extract) > 500 else extract
                        return {
                            "tool": "Wikipedia 📚",
                            "input": query,
                            "output": summary,
                            "success": True
                        }
            
            return {
                "tool": "Wikipedia 📚",
                "input": query,
                "output": f"No Wikipedia article found for '{query}'",
                "success": False
            }
            
        else:
            return {
                "tool": "Wikipedia 📚",
                "input": query,
                "output": f"Wikipedia returned error {response.status_code}",
                "success": False
            }
            
    except requests.exceptions.Timeout:
        return {
            "tool": "Wikipedia 📚",
            "input": query,
            "output": "Wikipedia request timed out. Please try again.",
            "success": False
        }
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return {
            "tool": "Wikipedia 📚",
            "input": query,
            "output": f"Search error: {str(e)}",
            "success": False
        }

def get_random_fact():
    facts = [
        "Honey never spoils. Archaeologists have found 3000-year-old honey in Egyptian tombs that's still edible!",
        "Octopuses have three hearts and blue blood.",
        "A day on Venus is longer than its year.",
        "Bananas are berries, but strawberries aren't.",
        "The human brain uses 20% of the body's energy despite being only 2% of its weight.",
        "There are more stars in the universe than grains of sand on all Earth's beaches.",
        "A group of flamingos is called a 'flamboyance'.",
        "Sharks existed before trees. Sharks: 400M years, Trees: 350M years."
    ]
    fact = random.choice(facts)
    return {"tool": "Random Fact 🤓", "input": "Get fact", "output": fact, "success": True}

def get_joke():
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the scarecrow win an award? He was outstanding in his field!",
        "What do you call a fake noodle? An impasta!",
        "Why don't eggs tell jokes? They'd crack each other up!",
        "What did the ocean say to the beach? Nothing, it just waved!",
        "Why did the math book look sad? Because it had too many problems!",
        "What do you call a bear with no teeth? A gummy bear!"
    ]
    joke = random.choice(jokes)
    return {"tool": "Joke Machine 😂", "input": "Tell joke", "output": joke, "success": True}

def get_quote():
    quotes = [
        "The only way to do great work is to love what you do. - Steve Jobs",
        "Innovation distinguishes between a leader and a follower. - Steve Jobs",
        "Life is 10% what happens to you and 90% how you react to it. - Charles R. Swindoll",
        "The best time to plant a tree was 20 years ago. The second best time is now. - Chinese Proverb",
        "Don't watch the clock; do what it does. Keep going. - Sam Levenson",
        "Success is not final, failure is not fatal: It is the courage to continue that counts. - Winston Churchill"
    ]
    quote = random.choice(quotes)
    return {"tool": "Quote Generator 💭", "input": "Get quote", "output": quote, "success": True}

# TEXT TOOLS
def count_words(text):
    words = len(text.split())
    chars = len(text)
    return {"tool": "Word Counter 📝", "input": text[:50], "output": f"Words: {words}, Characters: {chars}", "success": True}

def reverse_text(text):
    return {"tool": "Text Reverser 🔄", "input": text, "output": text[::-1], "success": True}

def text_to_uppercase(text):
    return {"tool": "Uppercase Converter 🔤", "input": text, "output": text.upper(), "success": True}

def text_to_lowercase(text):
    return {"tool": "Lowercase Converter 🔡", "input": text, "output": text.lower(), "success": True}

# CONVERSION TOOLS
def convert_currency(amount, from_currency, to_currency):
    rates = {
        "USD": 1.0, "EUR": 0.85, "GBP": 0.73, "INR": 83.0, "JPY": 110.0,
        "AUD": 1.35, "CAD": 1.25, "CNY": 6.5
    }
    from_rate = rates.get(from_currency.upper(), 1.0)
    to_rate = rates.get(to_currency.upper(), 1.0)
    result = (amount / from_rate) * to_rate
    return {
        "tool": "Currency Converter 💱",
        "input": f"{amount} {from_currency}",
        "output": f"{amount} {from_currency} = {result:.2f} {to_currency}",
        "success": True
    }

def convert_temperature(value, from_unit, to_unit):
    from_unit = from_unit.upper()
    to_unit = to_unit.upper()
    
    if from_unit == 'F':
        celsius = (value - 32) * 5/9
    elif from_unit == 'K':
        celsius = value - 273.15
    else:
        celsius = value
    
    if to_unit == 'F':
        result = celsius * 9/5 + 32
    elif to_unit == 'K':
        result = celsius + 273.15
    else:
        result = celsius
    
    return {
        "tool": "Temperature Converter 🌡️",
        "input": f"{value}°{from_unit}",
        "output": f"{value}°{from_unit} = {result:.2f}°{to_unit}",
        "success": True
    }

def encode_base64(text):
    encoded = base64.b64encode(text.encode()).decode()
    return {"tool": "Base64 Encoder 🔐", "input": text, "output": encoded, "success": True}

def decode_base64(encoded):
    try:
        decoded = base64.b64decode(encoded).decode()
        return {"tool": "Base64 Decoder 🔓", "input": encoded, "output": decoded, "success": True}
    except:
        return {"tool": "Base64 Decoder 🔓", "input": encoded, "output": "Invalid Base64", "success": False}

# RANDOM/FUN TOOLS
def roll_dice(sides=6):
    result = random.randint(1, sides)
    return {"tool": f"Dice Roller 🎲", "input": f"{sides}-sided dice", "output": f"You rolled: {result}", "success": True}

def flip_coin():
    result = random.choice(["Heads", "Tails"])
    return {"tool": "Coin Flip 🪙", "input": "Flip coin", "output": f"Result: {result}", "success": True}

def generate_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(random.choice(chars) for _ in range(length))
    return {"tool": "Password Generator 🔑", "input": f"Length: {length}", "output": password, "success": True}

def random_number(min, max):
    result = random.randint(min, max)
    return {"tool": "Random Number 🎰", "input": f"{min} to {max}", "output": f"Random number: {result}", "success": True}

def magic_8ball():
    answers = [
        "Yes, definitely!", "It is certain.", "Without a doubt.", "You may rely on it.",
        "As I see it, yes.", "Most likely.", "Outlook good.", "Signs point to yes.",
        "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
        "Cannot predict now.", "Concentrate and ask again.",
        "Don't count on it.", "My reply is no.", "My sources say no.",
        "Outlook not so good.", "Very doubtful."
    ]
    answer = random.choice(answers)
    return {"tool": "Magic 8-Ball 🎱", "input": "Shake", "output": answer, "success": True}

# Function mapping
available_functions = {
    "get_time": get_time,
    "calculate_age": calculate_age,
    "days_until": days_until,
    "calculator": calculator,
    "is_prime": is_prime,
    "factorial": factorial,
    "fibonacci": fibonacci,
    "get_weather": get_weather,
    "search_wikipedia": search_wikipedia,
    "get_random_fact": get_random_fact,
    "get_joke": get_joke,
    "get_quote": get_quote,
    "count_words": count_words,
    "reverse_text": reverse_text,
    "text_to_uppercase": text_to_uppercase,
    "text_to_lowercase": text_to_lowercase,
    "convert_currency": convert_currency,
    "convert_temperature": convert_temperature,
    "encode_base64": encode_base64,
    "decode_base64": decode_base64,
    "roll_dice": roll_dice,
    "flip_coin": flip_coin,
    "generate_password": generate_password,
    "random_number": random_number,
    "magic_8ball": magic_8ball
}

# ============================================
# SMART FALLBACK DETECTION
# ============================================

def detect_and_execute_tool(user_message):
    """Smart fallback: detect intent and execute tools directly"""
    msg = user_message.lower()
    
    # Wikipedia
    if any(word in msg for word in ['who is', 'what is', 'tell me about', 'search for', 'wikipedia', 'who are']):
        query = re.sub(r'(who is|who are|what is|what are|tell me about|search for|search|wikipedia|on wikipedia|\?)', '', user_message, flags=re.IGNORECASE)
        query = query.strip()
        if query:
            return search_wikipedia(query)
    
    # Weather
    if 'weather' in msg or 'temperature' in msg:
        cities = ['chennai', 'mumbai', 'delhi', 'bangalore', 'kolkata', 'hyderabad', 
                  'new york', 'london', 'tokyo', 'paris']
        for city in cities:
            if city in msg:
                return get_weather(city.title())
        return get_weather('Chennai')
    
    # Calculator
    math_pattern = r'[\d\+\-\*/\(\)\.\s]+'
    if any(word in msg for word in ['calculate', 'compute', 'what is', "what's", 'solve']):
        matches = re.findall(math_pattern, user_message)
        if matches:
            expression = max(matches, key=len).strip()
            if expression and any(op in expression for op in ['+', '-', '*', '/']):
                return calculator(expression)
    
    # Time/Date
    if any(word in msg for word in ['time', 'date', 'today', 'now', 'hi', 'hello', 'hey']):
        return get_time()
    
    # Joke
    if any(word in msg for word in ['joke', 'funny', 'laugh', 'humor']):
        return get_joke()
    
    # Fact
    if any(word in msg for word in ['fact', 'interesting', 'trivia']):
        return get_random_fact()
    
    # Quote
    if any(word in msg for word in ['quote', 'inspire', 'motivation', 'motivate']):
        return get_quote()
    
    # Dice
    if 'dice' in msg or 'roll' in msg:
        sides = 6
        if '20' in msg:
            sides = 20
        elif '12' in msg:
            sides = 12
        return roll_dice(sides)
    
    # Coin
    if 'coin' in msg or 'flip' in msg or 'heads' in msg or 'tails' in msg:
        return flip_coin()
    
    # Password
    if 'password' in msg:
        numbers = re.findall(r'\d+', user_message)
        length = int(numbers[0]) if numbers else 12
        return generate_password(length)
    
    # Magic 8 Ball
    if '8 ball' in msg or 'magic 8' in msg or '8ball' in msg:
        return magic_8ball()
    
    # Prime
    if 'prime' in msg:
        numbers = re.findall(r'\d+', user_message)
        if numbers:
            return is_prime(int(numbers[0]))
    
    # Factorial
    if 'factorial' in msg:
        numbers = re.findall(r'\d+', user_message)
        if numbers:
            return factorial(int(numbers[0]))
    
    # Fibonacci
    if 'fibonacci' in msg or 'fib' in msg:
        numbers = re.findall(r'\d+', user_message)
        count = int(numbers[0]) if numbers else 10
        return fibonacci(count)
    
    return None

def parse_groq_function_syntax(text):
    """Parse Groq's XML-like function call syntax when it appears as text"""
    # Pattern: <function=tool_name{"param": "value"}</function>
    pattern = r'<function=(\w+)(\{[^}]+\})</function>'
    match = re.search(pattern, text)
    
    if match:
        func_name = match.group(1)
        try:
            func_args = json.loads(match.group(2))
            return func_name, func_args
        except:
            pass
    
    return None, None

# ============================================
# FLASK ROUTES
# ============================================

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    conversation_history = data.get('history', [])
    
    print(f"\n{'='*60}")
    print(f"💬 User: {user_message}")
    print(f"{'='*60}")
    
    messages = [
        {
            "role": "system", 
            "content": """You are a friendly AI assistant with 25+ tools! Be conversational and warm.

Keep responses brief and natural (2-3 sentences max). Use a warm, engaging tone."""
        }
    ]
    
    for msg in conversation_history[-6:]:
        if msg.get('role') in ['user', 'assistant'] and msg.get('content'):
            messages.append({"role": msg['role'], "content": msg['content']})
    
    messages.append({"role": "user", "content": user_message})
    
    tool_calls_info = []
    final_message = ""
    
    # Try Groq function calling first
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=300,
            tools=tools,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        
        if hasattr(response_message, 'tool_calls') and response_message.tool_calls:
            print(f"✅ Groq tool calling succeeded")
            
            messages.append({
                "role": "assistant",
                "content": response_message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                    } for tc in response_message.tool_calls
                ]
            })
            
            for tool_call in response_message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                
                print(f"  → {func_name}: {func_args}")
                
                if func_name in available_functions:
                    result = available_functions[func_name](**func_args)
                    print(f"    ✓ {result['output']}")
                    tool_calls_info.append(result)
                    
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": json.dumps(result)
                    })
            
            final_response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.8,
                max_tokens=300
            )
            
            final_message = final_response.choices[0].message.content
        else:
            final_message = response_message.content or "Hey! How can I help you? 😊"
        
    except Exception as e:
        print(f"⚠️  Groq function calling failed: {str(e)}")
        print(f"🔄 Using smart fallback detection...")
        
        # FALLBACK: Manual detection and execution
        tool_result = detect_and_execute_tool(user_message)
        
        if tool_result:
            print(f"✅ Fallback detected: {tool_result['tool']}")
            print(f"   Output: {tool_result['output']}")
            tool_calls_info.append(tool_result)
            
            # Generate natural response
            try:
                prompt = f"User asked: '{user_message}'\n\nTool: {tool_result['tool']}\nResult: {tool_result['output']}\n\nRespond naturally in 2-3 sentences."
                
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {"role": "system", "content": "You are a friendly AI. Respond naturally based on the tool result."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,
                    max_tokens=200
                )
                final_message = response.choices[0].message.content
            except:
                final_message = f"Here's what I found: {tool_result['output']}"
        else:
            # No tool needed - just chat
            try:
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    temperature=0.8,
                    max_tokens=200
                )
                final_message = response.choices[0].message.content
            except:
                final_message = "I'm here to help! I have 25+ tools including Wikipedia, calculator, weather, and more. What would you like to know? 😊"
    
    print(f"🤖 Assistant: {final_message}\n")
    
    new_history = conversation_history + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": final_message}
    ]
    
    return jsonify({
        "response": final_message,
        "tool_calls": tool_calls_info,
        "history": new_history
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "model": MODEL,
        "total_tools": len(available_functions),
        "tools": list(available_functions.keys())
    })

@app.route('/tools', methods=['GET'])
def list_tools():
    """List all available tools"""
    tool_categories = {
        "Time & Date": ["get_time", "calculate_age", "days_until"],
        "Math": ["calculator", "is_prime", "factorial", "fibonacci"],
        "Information": ["get_weather", "search_wikipedia", "get_random_fact", "get_joke", "get_quote"],
        "Text": ["count_words", "reverse_text", "text_to_uppercase", "text_to_lowercase"],
        "Conversion": ["convert_currency", "convert_temperature", "encode_base64", "decode_base64"],
        "Random/Fun": ["roll_dice", "flip_coin", "generate_password", "random_number", "magic_8ball"]
    }
    return jsonify(tool_categories)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 AI Chatbot with 25+ Tools + Smart Fallback!")
    print("="*60)
    print(f"🤖 Model: {MODEL}")
    print(f"📍 Server: http://localhost:5000")
    print(f"🔧 Total Tools: {len(available_functions)}")
    print("\nTool Categories:")
    print("  • Time & Date (3)")
    print("  • Math (4)")
    print("  • Information (5)")
    print("  • Text (4)")
    print("  • Conversion (4)")
    print("  • Random/Fun (5)")
    print("="*60 + "\n")
    app.run(debug=True, port=5000, host='0.0.0.0')
