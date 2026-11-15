from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from database.db import get_db, init_db, seed_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # FastAPI's version of Flask's app_context(): make the DB ready before any request.
    init_db()
    seed_db()
    yield


app = FastAPI(title="Spendly", lifespan=lifespan)

# Flask serves /static and finds templates/ on its own; FastAPI needs both set up.
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ------------------------------------------------------------------ #
# Page routes (converted from the Flask app.py)                       #
# Route names = function names, so url_for('landing') etc. still work #
# ------------------------------------------------------------------ #

@app.get("/", response_class=HTMLResponse)
def landing(request: Request):
    return templates.TemplateResponse(request, "landing.html")


@app.get("/register", response_class=HTMLResponse)
def register(request: Request):
    return templates.TemplateResponse(request, "register.html")


@app.get("/login", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse(request, "login.html")


@app.get("/terms", response_class=HTMLResponse)
def terms(request: Request):
    return templates.TemplateResponse(request, "terms.html")


@app.get("/privacy", response_class=HTMLResponse)
def privacy(request: Request):
    return templates.TemplateResponse(request, "privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.get("/logout", response_class=PlainTextResponse)
def logout():
    return "Logout — coming in Step 3"


@app.get("/profile", response_class=PlainTextResponse)
def profile():
    return "Profile page — coming in Step 4"


# Must be declared before /expenses/{expense_id}, or "add" would be read as an id.
@app.get("/expenses/add", response_class=PlainTextResponse)
def add_expense():
    return "Add expense — coming in Step 7"


@app.get("/expenses/{id}/edit", response_class=PlainTextResponse)
def edit_expense(id: int):
    return "Edit expense — coming in Step 8"


@app.get("/expenses/{id}/delete", response_class=PlainTextResponse)
def delete_expense_page(id: int):
    return "Delete expense — coming in Step 9"


# ------------------------------------------------------------------ #
# JSON test API (from the earlier test setup, in-memory only)         #
# ------------------------------------------------------------------ #

class ExpenseIn(BaseModel):
    title: str
    amount: float
    category: str = "general"


class Expense(ExpenseIn):
    id: int


expenses: dict[int, Expense] = {}
next_id = 1


@app.get("/expenses")
def list_expenses() -> list[Expense]:
    return list(expenses.values())


@app.get("/expenses/{expense_id}")
def get_expense(expense_id: int) -> Expense:
    if expense_id not in expenses:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expenses[expense_id]


@app.post("/expenses", status_code=201)
def create_expense(data: ExpenseIn) -> Expense:
    global next_id
    expense = Expense(id=next_id, **data.model_dump())
    expenses[next_id] = expense
    next_id += 1
    return expense


@app.put("/expenses/{expense_id}")
def update_expense(expense_id: int, data: ExpenseIn) -> Expense:
    if expense_id not in expenses:
        raise HTTPException(status_code=404, detail="Expense not found")
    expense = Expense(id=expense_id, **data.model_dump())
    expenses[expense_id] = expense
    return expense


@app.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int):
    if expenses.pop(expense_id, None) is None:
        raise HTTPException(status_code=404, detail="Expense not found")


if __name__ == "__main__":
    # Same as Flask's app.run(debug=True, port=5001)
    import uvicorn
    uvicorn.run("main:app", reload=True, port=5001)
