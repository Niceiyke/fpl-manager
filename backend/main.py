from fastapi import FastAPI,status

app = FastAPI()

@app.get("/health", status_code=status.HTTP_200_OK)
async def read_root():
    return {"message": "Fantasy Premier League API is up and running!"}

@app.get("/api/manager/{manager_id}", status_code=status.HTTP_200_OK)
async def read_team(manager_id: int):
    pass