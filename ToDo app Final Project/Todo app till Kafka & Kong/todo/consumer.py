
import asyncio
import json
from aiokafka import AIOKafkaConsumer
from sqlmodel import SQLModel, Session, create_engine
from app import settings
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

connection_string = str(settings.DATABASE_URL)
engine = create_engine(
    connection_string, connect_args={}, pool_recycle=300)

async def consume_messages(topic: str, bootstrap_servers: str):
    # Create a consumer instance
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="my-group",
        auto_offset_reset='earliest')

    # Start the consumer
    await consumer.start()
    try:
        # Continuously listen for messages
        async for message in consumer:
            print(f"Received message: {message.value.decode()} on topic {message.topic}")
            data = json.loads(message.value.decode())
            with Session(engine) as session:
                todo = Todo.from_orm(data)
                session.add(todo)
                session.commit()
                session.refresh(todo)
    finally:
        # Ensure to close the consumer when done
        await consumer.stop()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(consume_messages('todos', 'broker:19092'))
