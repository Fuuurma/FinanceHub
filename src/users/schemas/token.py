from pydantic import BaseModel


class TokenObtainPairOut(BaseModel):
    refresh: str
    access: str


class TokenRefreshOut(BaseModel):
    access: str
