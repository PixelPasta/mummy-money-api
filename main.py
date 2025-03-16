from fastapi import FastAPI
import json
import google.generativeai as genai


genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name='gemini-2.0-flash')

def get_mummy_response(amount:int, description:str) -> str:
    if amount < 0:
        raise ValueError('Amount must be valid')

    prompt = f"""
    You are an angry indian middle-class mother. Your job is to react to child's expenses,
    if they spend too much, you should scold them and in a funny response.
    if they save money, you should praise them but still nag them a little.
    you should also consider the reason and price before giving you response.

    The Child spent {amount} for the purpose of {description}.

    React like an Angry middle-aged middle-class mother and you responses should all be in
    hinglish and concise in less than 10 words
    """

    response = model.generate_content(prompt)
    return response.text.strip() if response and response.text else 'Beta, kya kar raha hai?!'



app = FastAPI()

EXPENSE_FILE = 'expenses.json'

try:
    with open(EXPENSE_FILE, 'r') as f:
        expenses = json.load(f)

except FileNotFoundError:
    expenses = {"total": 0, 'logs': []}



@app.get("/")
async def root():
    return {'message':'Mummy budget tracker is running.'}

@app.get("/expense/")
async def get_expense():
    return expenses

@app.post("/add_expense/")
async def add_expense(amount:int, description:str='Unknown'):
    
    global expenses
    expenses['total'] += amount
    expenses['logs'].append({'amount':amount, 'description':description})

    with open(EXPENSE_FILE,'w') as f:
        json.dump(expenses,f)


        response = get_mummy_response(amount, description)

    return {"message": response, "total_spent": expenses["total"]}

@app.delete("/reset_expenses/")
async def reset_expenses():
    global expenses
    expenses = {'total':0, 'logs':[]}

    with open(EXPENSE_FILE, 'w') as f:
        json.dump(expenses,f)

    return {'messages':'All expenses have been reset.'}