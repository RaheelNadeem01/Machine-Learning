#this is python script for making operating system variables as python variables 

from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()

DATABASE_URL = config("DATABASE_URL", cast=Secret) #making envoirnment variable a runtime python variable

TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast=Secret)

#here cast=secret is used to encrypt the password , if someone tries to hack the python variable
#the password will not show the same 