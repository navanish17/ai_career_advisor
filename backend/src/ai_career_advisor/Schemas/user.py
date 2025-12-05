from pydantic import EmailStr , BaseModel

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponce(BaseModel):
    id: str
    name: str
    email: EmailStr

    class Config:
        from_attributes = True

        