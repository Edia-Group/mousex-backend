from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.auth import auth_router
from app.routers.user import users_router
from app.routers.testgroup import testgroup_router 
from app.routers.test import test_router
from app.routers.domande import domande_router

app = FastAPI(
    openapi_tags=[
        {
            "name": "Auth",
            "description": "Endpoints for user authentication and OTP management.",
        },
        {
            "name": "Users",
            "description": "Endpoints for user profile management.",
        },
        {
            "name": "Test",
            "description": "Endpoints for user profile management.",
        },
        {
            "name": "TestsGroup",
            "description": "Endpoints for user profile management.",
        },
                {
            "name": "Domande",
            "description": "Endpoints for user Domande management.",
        },
    ]
)

# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

"""
@app.on_event("startup")
def on_startup():
    create_database()
# TODO : CHANGE WITH ALEMBIC
# """

app.include_router(users_router)
app.include_router(domande_router)
app.include_router(auth_router)
app.include_router(testgroup_router)
app.include_router(test_router)