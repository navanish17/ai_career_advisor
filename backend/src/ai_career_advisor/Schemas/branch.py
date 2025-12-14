from pydantic import BaseModel


class BranchResponse(BaseModel):
    id: int
    name: str
    degree_id: int

    class Config:
        from_attributes = True


class BranchListResponse(BaseModel):
    branches: list[BranchResponse]
