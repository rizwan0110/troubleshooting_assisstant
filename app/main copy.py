import logging
from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import RequestIDMiddleware
from app.api.routes import router

from app.core.exceptions import ValidationException
from app.schemas.responses import ErrorResponse


model = SentenceTransformer("all-MiniLM-L6-v2")




setup_logging()
logger = logging.getLogger(__name__)



app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

app.add_middleware(RequestIDMiddleware)

#app.include_router(router)

@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):

    error_response = ErrorResponse(
        error=exc.message,
        details=exc.details,
        timestamp=datetime.now()
    )

    return JSONResponse(
        status_code=400,
        content=jsonable_encoder(error_response)
        
    )
    
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):

    logger.exception("Unhandled exception occurred")

    error_response = ErrorResponse(
        error="Internal server error",
        details=None,
        timestamp=datetime.now()
    )

    return JSONResponse(
        status_code=500,
        content=jsonable_encoder(error_response)
        
    )
    
    

@app.get("/")
def home():
    return{"Version":settings.VERSION}
@app.get("/health")
def health_check():
    logger.info('Health Check Called')
    return{"Status":"OK"}


