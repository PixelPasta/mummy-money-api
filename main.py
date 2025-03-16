from fastapi import FastAPI
import json
import random
import google.generativeai as genai




app = FastAPI()

EXPENSE_FILE = 'expenses.json'

try:
    with open(EXPENSE_FILE, 'r') as f:
        expenses = json.load(f)

except FileNotFoundError:
    expenses = {"total": 0, 'logs': []}

MATA_REACTION = {
    "good": ["Good beta, keep saving!", "Proud of you, but buy some dhaniya too."],
    "warning": ["Hmm… not too much spending, okay?", "Do you think money grows on trees?"],
    "bad": ["AREY! ₹8000 ka pizza? CHAPPAL KHAEGA?", "Should I call your real mom?", "Bas kar beta, bas kar."]
}


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

    if amount < 500:
        response = random.choice(MATA_REACTION["good"])
    elif amount < 5000:
        response = random.choice(MATA_REACTION["warning"])
    else:
        response = random.choice(MATA_REACTION["bad"])

    return {"message": response, "total_spent": expenses["total"]}

@app.delete("/reset_expenses/")
async def reset_expenses():
    global expenses
    expenses = {'total':0, 'logs':[]}

    with open(EXPENSE_FILE, 'w') as f:
        json.dump(expenses,f)

    return {'messages':'All expenses have been reset.'}