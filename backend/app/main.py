from threading import Thread
import time
from fastapi import FastAPI,  Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (get_swagger_ui_html,)
from routes import router
from helpers import Base, engine, rabbitmq, channel

app = FastAPI(title="FastApi",
              version="0.0.1",
              docs_url=None,
              redoc_url=None)


origins = ["*"]
app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"],)


app.include_router(router, prefix='/api')


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
    )

t1 = Thread(target=rabbitmq)


@app.on_event("startup")
def start_task():
    # Base.metadata.create_all(bind=engine)
    t1.start()


@app.on_event("shutdown")
def shutdown_task():
    channel.close()
    t1.do_run = False
