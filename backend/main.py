from fastapi import FastAPI, HTTPException

# Para poder utilizar campos con fechas
from datetime import date, datetime

# Pydantic es una librería para validar los datos.
# BaseModel sirve para definir clases para crear los modelos
# de datos que se van a usar en la API.
from pydantic import BaseModel

from typing import List

# Motor es una versión asíncrona de PyMongo,
# la biblioteca estándar de Python para trabajar con MongoDB.
import motor.motor_asyncio

# Para aceptar peticiones de diferentes dominios
from fastapi.middleware.cors import CORSMiddleware

# Define el modelo de datos para un usuario utilizando Pydantic.
# Esto ayuda a FastAPI a validar los tipos de datos entrantes.
class User(BaseModel):
    dni: str
    nombre: str
    apellido: str
    telefono: str
    direccion: str
    fecha_nacimiento: date

# Crea la instancia de la aplicación FastAPI.
app = FastAPI()

# Lista de orígenes permitidos
origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Los orígenes que deben ser permitidos, usar ["*"] para permitir todos
    allow_credentials=True,
    allow_methods=["*"],  # Métodos permitidos
    allow_headers=["*"],  # Cabeceras permitidas
)



# Configura el cliente de MongoDB para conectarse a la instancia de MongoDB.
# 'mongodb' es el nombre del servicio definido en docker-compose.yml, y '27017' es el puerto estándar de MongoDB.
# Cadena de conexión a MongoDB con autenticación
MONGODB_URL = "mongodb://admin:123@mongodb:27017/?authSource=admin"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.usersdb

# Endpoint para crear un nuevo usuario.
@app.post("/users/", response_description="Add new user", response_model=User)
async def create_user(user: User):
    user_dict = user.dict()
    user_dict["fecha_nacimiento"] = datetime.combine(user.fecha_nacimiento, datetime.min.time())
    await db["users"].insert_one(user_dict)
    return user

# Endpoint para listar todos los usuarios.
@app.get("/users/", response_description="List all users", response_model=List[User])
async def list_users():
    users = await db["users"].find().to_list(1000)
    return users

# Endpoint para obtener un usuario específico por DNI.
@app.get("/users/{dni}", response_description="Get a single user", response_model=User)
async def find_user(dni: str):
    user = await db["users"].find_one({"dni": dni})
    if user is not None:
        return user
    raise HTTPException(status_code=404, detail=f"User {dni} not found")

# Endpoint para borrar un usuario específico por DNI.
@app.delete("/users/{dni}", response_description="Delete a user", status_code=204)
async def delete_user(dni: str):
    delete_result = await db["users"].delete_one({"dni": dni})

    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"User with DNI {dni} not found")
    
    return {"message": "User deleted successfully"}
