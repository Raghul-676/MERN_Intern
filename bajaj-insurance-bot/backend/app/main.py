# # backend/app/main.py
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from app.api import json_gateway, admin_routes, user_routes

# app = FastAPI(
#     title="Bajaj Insurance RAG Backend",
#     description="Enterprise-grade insurance document analysis backend for Bajaj.",
#     version="1.0.0",
# )

# # CORS settings (adjust origins as needed for your frontend URLs)
# origins = [
#     "http://localhost:3000",  # React dev (CRA)
#     "http://localhost:5173",  # React + Vite
#     "http://127.0.0.1:3000",
#     "http://127.0.0.1:5173",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,          # use ["*"] during early dev if needed
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Routers
# # /bajaj-model  -> fixed JSON I/O contract
# # /admin/...    -> admin policy upload & management
# # /user/...     -> user/agent queries on policies
# app.include_router(json_gateway.router)
# app.include_router(admin_routes.router)
# app.include_router(user_routes.router)


# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from app.api import json_gateway, admin_routes, user_routes
# from app.api import auth_routes

# app = FastAPI(
#     title="Bajaj Insurance RAG Backend",
#     description="Enterprise-grade insurance document analysis backend for Bajaj.",
#     version="1.0.0",
# )

# origins = [
#     "http://localhost:5173",
#     "http://127.0.0.1:5173",
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(auth_routes.router)
# app.include_router(json_gateway.router)
# app.include_router(admin_routes.router)
# app.include_router(user_routes.router)


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import json_gateway, admin_routes, user_routes
from app.api import auth_routes

app = FastAPI(
    title="Bajaj Insurance RAG Backend",
    description="Enterprise-grade insurance document analysis backend for Bajaj.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # TEMP: allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(json_gateway.router)
app.include_router(admin_routes.router)
app.include_router(user_routes.router)
