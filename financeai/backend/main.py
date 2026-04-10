import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("financeai")

app = FastAPI(title="FinanceAI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration:.2f}s")
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error on {request.url.path}")
    return JSONResponse(status_code=500, content={"detail": "Erro interno do servidor"})


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

from routes.debts import router as debts_router
app.include_router(debts_router)

from routes.goals import router as goals_router
app.include_router(goals_router)

from routes.recurring import router as recurring_router
app.include_router(recurring_router)

from routes.budgets import router as budgets_router
app.include_router(budgets_router)

from routes.chat import router as chat_router
app.include_router(chat_router)

from routes.plans import router as plans_router
app.include_router(plans_router)


@app.get("/")
async def health_check():
    return {"status": "ok", "service": "FinanceAI API"}
