from fastapi import FastAPI, Response, Request
from routes.api import API
from routes.website import Website
from zte_wrapper.wrapper import ZTEWrapper
import os
import uvicorn
from dotenv import load_dotenv
from utils import OnCooldownException, AuthenticationErrorr
import logging

load_dotenv()


success = True
required_vars = ["HOST", "PORT", "WEBUI_ADDR", "WEBUI_PASSWORD", "PASSWORDS"]
for required_var in required_vars:
    if not os.environ.get(required_var):
        print(f"Please specify {required_var} in your env!")
        success = False

if not success:
    quit(-1)


app = FastAPI()
zte_wrapper = ZTEWrapper(os.environ["WEBUI_ADDR"], os.environ["WEBUI_PASSWORD"])

api_router = API(zte_wrapper)
app.include_router(api_router.router)
app.include_router(Website().router)


@app.exception_handler(OnCooldownException)
async def cooldown_handler(request: Request, exc: Exception):
    return Response("On cooldown", 503, media_type="text/plain")


@app.exception_handler(AuthenticationErrorr)
async def autherror_handler(request: Request, exc: Exception):
    return Response(exc.args[0], 401, media_type="text/plain")


uvicorn.run(app, host=os.environ["HOST"], port=int(os.environ["PORT"]))
