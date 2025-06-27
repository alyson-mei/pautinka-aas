from fastapi import FastAPI, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.staticfiles import StaticFiles

from data.models.image import Image
from data.repository import RepositoryFactory
from data.db_init import init_db
from data.database import get_db

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("root.html", {
        "request": request
    })

@app.get("/pautinka")
async def get_random_image(request: Request, db: AsyncSession = Depends(get_db)):
    repo = RepositoryFactory(db).get_repository(Image)
    image = await repo.get_random()
    if not image:
        raise HTTPException(status_code=404, detail="No images found")
    
    return templates.TemplateResponse("image.html", {
        "request": request,
        "image": image
    })

@app.get("/pautinka/{image_id}")
async def get_image(request: Request, image_id: int, db: AsyncSession = Depends(get_db)):
    repo = RepositoryFactory(db).get_repository(Image)
    image = await repo.get_by_id(image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return templates.TemplateResponse("image.html", {
        "request": request,
        "image": image
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)