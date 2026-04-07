from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FinanceAI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from routes.transactions import router as transactions_router
app.include_router(transactions_router)

from routes.investments import router as investments_router
app.include_router(investments_router)

from routes.credit_cards import router as credit_cards_router
app.include_router(credit_cards_router)

from routes.summary import router as summary_router
app.include_router(summary_router)

from routes.alerts import router as alerts_router
app.include_router(alerts_router)

from routes.chat import router as chat_router
app.include_router(chat_router)


@app.get("/")
async def health_check():
    return {"status": "ok", "service": "FinanceAI API"}
