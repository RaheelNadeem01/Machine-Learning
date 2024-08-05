# main.py
from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
from app import settings
from sqlmodel import Field, Session, SQLModel, create_engine, select, Sequence
from fastapi import FastAPI, Depends,HTTPException,Query
from typing import AsyncGenerator
from typing import Optional, Dict
from typing import Annotated
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
import json
from pydantic import BaseModel
from sqlalchemy.orm import Session





class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(index=True)



connection_string = str(settings.DATABASE_URL)#.replace("postgresql", "postgresql+psycopg2") #postgress ka container up kr k us me database save krwaya ha , data hamare server se store hoga jo container chal rha ha


engine = create_engine(
    connection_string, connect_args={}, pool_recycle=300
)


def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)


async def consume_messages(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="my-group",
        auto_offset_reset='earliest'
    )

    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            print(f"Received message: {message.value.decode()} on topic {message.topic}")
            # Here you can add code to process each message.
            # Example: parse the message, store it in a database, etc.
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()




@asynccontextmanager
async def lifespan(app: FastAPI)-> AsyncGenerator[None, None]:
    print("Creating tables..")
    # loop.run_until_complete(consume_messages('todos', 'broker:19092'))
    task = asyncio.create_task(consume_messages('todos', 'broker:19092'))
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
    {'name': 'nadeem', 'password': '456'}
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



# Kafka Producer as a dependency
async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()

@app.post("/todos/", response_model=Todo)
async def create_todo(todo: Todo, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)])->Todo:
        todo_dict = {field: getattr(todo, field) for field in todo.dict()}
        todo_json = json.dumps(todo_dict).encode("utf-8")
        print("todoJSON:", todo_json)
        # Produce message
        await producer.send_and_wait("todos", todo_json)
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo

@app.delete("/todos/{todo_id}", response_model=Todo)
async def delete_todo(
    todo_id: int,
    session: Annotated[Session, Depends(get_session)],
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]) -> Todo:
    # Fetch the Todo item to delete
    todo = session.query(Todo).get(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # Convert Todo item to JSON for Kafka message
    todo_dict = {field: getattr(todo, field) for field in todo.dict()}
    todo_json = json.dumps(todo_dict).encode("utf-8")
    print("todoDeleteJSON:", todo_json)
    
    # Produce delete message
    await producer.send_and_wait("todos", todo_json)
    
    # Delete the Todo item from the database
    session.delete(todo)
    session.commit()
    
    return todo


#@app.get("/todos/", response_model=list[Todo])
#def read_todos(session: Annotated[Session, Depends(get_session)]):
        #todos = session.exec(select(Todo)).all()
        #return todos


@app.get("/todos/", response_model=list[Todo])
async def read_todos(session: Annotated[Session, Depends(get_session)]) -> list[Todo]:
    todos = session.query(Todo).all()
    return todos



@app.get("/todos/{todo_id}", response_model=Todo)
async def read_todo(
    todo_id: int,
    session: Annotated[Session, Depends(get_session)]) -> Todo:
    todo = session.query(Todo).get(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo