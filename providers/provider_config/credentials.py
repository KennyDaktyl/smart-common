from pydantic import BaseModel, Field


class UsernamePasswordCredentials(BaseModel):
    username: str = Field(..., description="Login username")
    password: str = Field(..., description="Login password")
