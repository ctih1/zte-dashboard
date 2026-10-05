from fastapi import FastAPI
from routes.api import API
from routes.website import Website
from zte_wrapper.wrapper import ZTEWrapper
import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
zte_wrapper = ZTEWrapper(os.environ["WEBUI_ADDR"], os.environ["WEBUI_PASSWORD"])

api_router = API(zte_wrapper)
app.include_router(api_router.router)
app.include_router(Website().router)

uvicorn.run(app, host="0.0.0.0")
