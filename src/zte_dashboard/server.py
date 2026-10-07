from fastapi import FastAPI, Response, Request
from routes.api import API
from routes.website import Website
from zte_wrapper.wrapper import ZTEWrapper
import os
import uvicorn
from dotenv import load_dotenv
from utils import OnCooldownException

load_dotenv()

app = FastAPI()
zte_wrapper = ZTEWrapper(os.environ["WEBUI_ADDR"], os.environ["WEBUI_PASSWORD"])

api_router = API(zte_wrapper)
app.include_router(api_router.router)
app.include_router(Website().router)


@app.exception_handler(OnCooldownException)
async def cooldown_handler(request: Request, exc: Exception):
    return Response("On cooldown", 503)


uvicorn.run(app, host=os.environ["HOST"], port=int(os.environ["PORT"]))
