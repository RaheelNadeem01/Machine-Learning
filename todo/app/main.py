# main.py
from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
from app import settings
from sqlmodel import Field, Session, SQLModel, create_engine, select, Sequence
from fastapi import FastAPI, Depends,HTTPException,Query
from typing import AsyncGenerator
from typing import Optional, Dict
from typing import Annotated


class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(index=True)


connection_string = str(settings.DATABASE_URL)#.replace("postgresql", "postgresql+psycopg2")


engine = create_engine(
    connection_string, connect_args={}, pool_recycle=300
)




def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)




@asynccontextmanager
async def lifespan(app: FastAPI)-> AsyncGenerator[None, None]:
    print("Creating tables..")
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Todo Application By Raheel Nadeem", 
    version="0.1.0",
    servers=[
        {
            "url": "http://0.0.0.0:8000", # ADD NGROK URL Here Before Creating GPT Action
            "description": "Development Server"
        }
        ])

def get_session():
    with Session(engine) as session:
        yield session




app=FastAPI()
users = [
    {'name': 'raheel', 'password': '123'},
    {'name': 'qasim', 'password': '456'}
]

# Dependency function (updated with security considerations)
async def user_dep(name: str = Query(...), password: str = Query(...)) -> Dict[str, str]:
    # Validate credentials (replace with secure password hashing in a real application)
    for user in users:
        if user['name'] == name and user['password'] == password:  # Correct comparison
            return {"name": name, "valid": "true", "message": f"Hello dear {name}"}
    return {"message": f"Sorry, {name} is not a valid user"}

# Path function (using Depends with user_dep)
@app.get("/user")
async def get_user(user:Annotated[dict,Depends(user_dep)]) -> Dict[str, str]:  # the code will run in such a way that it will find a dependency function 
    return user



# API endpoint to create a new Todo item
@app.post("/todos/", response_model=Todo)
def create_todo(todo: Todo, session: Annotated[Session, Depends(get_session)])->Todo:
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo


# API endpoint to read all Todo items
@app.get("/todos/", response_model=list[Todo])
def read_todos(session: Annotated[Session, Depends(get_session)]):
        todos = session.exec(select(Todo)).all()
        return todos



# API endpoint to read a specific Todo item by ID
@app.get("/todos/{todo_id}", response_model=Todo)
async def read_todo(todo_id: int, session: Session = Depends(get_session)) -> Todo:
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo




# API endpoint to delete a specific Todo item by ID
@app.delete("/todos/{todo_id}", response_model=Todo)
def delete_todo(todo_id: int, session: Annotated[Session, Depends(get_session)]) -> Todo:
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    session.delete(todo)
    session.commit()
    return todo



# API endpoint to delete all completed Todo items
@app.delete("/todos/")
async def delete_completed_todos(session: Session = Depends(get_session)) -> None:
    completed_todos = session.exec(select(Todo).filter_by(done=True)).all()
    for todo in completed_todos:
        session.delete(todo)
    session.commit()




# API endpoint to update a specific Todo item by ID
@app.put("/todos/{todo_id}", response_model=Todo)
async def update_todo(todo_id: int, todo: Todo, session: Session = Depends(get_session)) -> Todo:
    db_todo = session.get(Todo, todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db_todo.content = todo.content
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo