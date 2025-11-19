"""
Entreprise Grouping Proxy Routes
Proxy les requêtes de regroupement d'entreprises vers le microservice auth
"""
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
import os

grouping_proxy_router = APIRouter(prefix="/entreprises/grouping", tags=["Entreprise Grouping Proxy"])

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")


@grouping_proxy_router.post("/request")
async def create_grouping_request_proxy(request: Request):
    """Proxy: Create grouping request"""
    body = await request.json()
    token = request.headers.get("authorization", "")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/api/entreprises/grouping/request",
                json=body,
                headers={"authorization": token},
                timeout=30.0
            )
            return JSONResponse(
                status_code=response.status_code,
                content=response.json()
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Auth service unavailable: {str(e)}")


@grouping_proxy_router.get("/my-requests")
async def get_my_grouping_requests_proxy(request: Request, status: str = None):
    """Proxy: Get my grouping requests"""
    token = request.headers.get("authorization", "")
    
    params = {}
    if status:
        params["status_filter"] = status
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/api/entreprises/grouping/my-requests",
                params=params,
                headers={"authorization": token},
                timeout=30.0
            )
            return JSONResponse(
                status_code=response.status_code,
                content=response.json()
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Auth service unavailable: {str(e)}")


@grouping_proxy_router.get("/{request_id}")
async def get_grouping_request_proxy(request_id: str, request: Request):
    """Proxy: Get grouping request details"""
    token = request.headers.get("authorization", "")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/api/entreprises/grouping/{request_id}",
                headers={"authorization": token},
                timeout=30.0
            )
            return JSONResponse(
                status_code=response.status_code,
                content=response.json()
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Auth service unavailable: {str(e)}")


@grouping_proxy_router.post("/{request_id}/approve")
async def approve_grouping_request_proxy(request_id: str, request: Request):
    """Proxy: Approve grouping request"""
    body = await request.json()
    token = request.headers.get("authorization", "")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/api/entreprises/grouping/{request_id}/approve",
                json=body,
                headers={"authorization": token},
                timeout=30.0
            )
            return JSONResponse(
                status_code=response.status_code,
                content=response.json()
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Auth service unavailable: {str(e)}")


@grouping_proxy_router.post("/{request_id}/reject")
async def reject_grouping_request_proxy(request_id: str, request: Request):
    """Proxy: Reject grouping request"""
    body = await request.json()
    token = request.headers.get("authorization", "")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/api/entreprises/grouping/{request_id}/reject",
                json=body,
                headers={"authorization": token},
                timeout=30.0
            )
            return JSONResponse(
                status_code=response.status_code,
                content=response.json()
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Auth service unavailable: {str(e)}")
