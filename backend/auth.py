import os, urllib.parse, httpx
from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
from db import coleccion_usuarios

load_dotenv()
router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
OAUTH_SCOPE = "openid email profile"

TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

@router.get("/auth/sesion")
def obtener_sesion(request: Request):
    correo = request.cookies.get("session_email")
    return {"correo": correo if correo else None}

@router.get("/auth/google/login")
def google_login():
    base = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": OAUTH_SCOPE,
        "access_type": "offline",
        "prompt": "consent"
    }
    url = f"{base}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url)

@router.get("/auth/google/callback")
async def google_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return {"error": "No se recibió el código de Google"}

    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            TOKEN_URL,
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": REDIRECT_URI,
                "grant_type": "authorization_code",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token_data = token_res.json()
        access_token = token_data.get("access_token")

        if not access_token:
            return {"error": "No se pudo obtener el token de acceso"}

        user_res = await client.get(
            USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_data = user_res.json()
        correo = user_data.get("email")

    if not correo:
        return {"error": "No se pudo obtener el correo del usuario"}

    existing = await coleccion_usuarios.find_one({"correo": correo})
    if not existing:
        await coleccion_usuarios.insert_one({
            "correo": correo,
            "marcadores": [],
            "token_oauth": access_token
        })
    else:
        await coleccion_usuarios.update_one(
            {"correo": correo},
            {"$set": {"token_oauth": access_token}}
        )

    response = RedirectResponse(url="/")
    response.set_cookie(
        key="session_email",
        value=correo,
        path="/",
        httponly=False,
        samesite="lax"
    )
    return response


@router.post("/auth/logout")
def cerrar_sesion(response: Response):
    response.delete_cookie("session_email")
    return {"mensaje": "Sesión cerrada"}
