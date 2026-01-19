from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel


class APIResponse(BaseModel):
    msg: str
    data: Any | None = None


app = FastAPI()


@app.get("/", response_model=APIResponse)
def root() -> APIResponse:
    return APIResponse(msg="Hello World")
