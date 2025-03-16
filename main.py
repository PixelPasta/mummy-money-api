from fastapi import FastAPI
import json
import google.generativeai as genai
import httpx  # Importing httpx for making HTTP requests

genai.configure(api_key='AIzaSyDqYsEaiK6lSPAfncUnn-GVbZrTl3UT6IU')
model = genai.GenerativeModel(model_name='gemini-2.0-flash')

def get_mummy_response(amount: int, description: str) -> str:
    if amount < 0:
        raise ValueError('Amount must be valid')

    prompt = f"""
    You are an angry Indian middle-class mother. Your job is to react to child's expenses,
    if they spend too much, you should scold them in a funny way.
    If they save money, you should praise them but still nag them a little.
    You should also consider the reason and price to check if the price for the item is reasonable
    or not.

    If the price seems worth it for the item purchased, then you can praise them and be surprised.

    All the prices are in Indian Rupee.

    The Child spent {amount} for the purpose of {description}.

    React like an angry middle-aged middle-class mother, and your responses should all be in
    Hinglish and concise in less than 10 words.
    """

    response = model.generate_content(prompt)
    return response.text.strip() if response and response.text else 'Beta, kya kar raha hai?!'


app = FastAPI()

EXPENSE_FILE = 'expenses.json'

try:
    with open(EXPENSE_FILE, 'r') as f:
        expenses = json.load(f)
except FileNotFoundError:
    expenses = {"total": 0, "logs": []}


@app.get("/")
async def root():
    return {"message": "Mummy budget tracker is running."}


@app.get("/expense/")
async def get_expense():
    return expenses


@app.get("/add_expense/")
async def add_expense(amount: int, description: str = 'Unknown'):
    global expenses
    expenses['total'] += amount
    expenses['logs'].append({'amount': amount, 'description': description})

    with open(EXPENSE_FILE, 'w') as f:
        json.dump(expenses, f, indent=4)

    response = get_mummy_response(amount, description)

    # Making an HTTP GET request to another endpoint
    async with httpx.AsyncClient() as client:
        try:
            callback_url = "http://example.com/webhook"  # Replace with the actual URL
            await client.get(callback_url, params={"amount": amount, "description": description})
        except Exception as e:
            return {"error": f"Failed to send data to webhook: {str(e)}"}

    return {"message": response, "total_spent": expenses["total"]}


@app.delete("/reset_expenses/")
async def reset_expenses():
    global expenses
    expenses = {'total': 0, 'logs': []}

    with open(EXPENSE_FILE, 'w') as f:
        json.dump(expenses, f)

    return {"message": "All expenses have been reset."}
