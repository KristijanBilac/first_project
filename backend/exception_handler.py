from fastapi import Request
from starlette.responses import JSONResponse
from dto_model import ErrorResponse, CustomException


async def exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            status_code=exc.status_code,
            detail=exc.detail,
        ).model_dump()
    )
