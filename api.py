from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="nuScenes API")
API_HOST = os.getenv('API_HOST')
API_PORT = int(os.getenv('API_PORT'))

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
def get_db():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        cursor_factory=RealDictCursor
    )
    try:
        yield conn
    finally:
        conn.close()

# Pydantic models for request/response
class Log(BaseModel):
    token: str
    logfile: str
    vehicle: str
    date_captured: str
    location: str

class Sensor(BaseModel):
    token: str
    channel: str
    modality: str

class Category(BaseModel):
    token: str
    name: str
    description: str
    index: Optional[int]

class Instance(BaseModel):
    token: str
    category_token: str
    nbr_annotations: int
    first_annotation_token: str
    last_annotation_token: str

class EgoPose(BaseModel):
    token: str
    translation: dict
    rotation: dict
    timestamp: int

class CalibratedSensor(BaseModel):
    token: str
    sensor_token: str
    translation: dict
    rotation: dict
    camera_intrinsic: Optional[dict]

class SampleAnnotation(BaseModel):
    token: str
    sample_token: str
    instance_token: str
    visibility_token: str
    translation: dict
    size: dict
    rotation: dict
    num_lidar_pts: int
    num_radar_pts: int
    next: Optional[str]
    prev: Optional[str]

class Map(BaseModel):
    token: str
    log_tokens: list
    category: str
    filename: str

class Lidarseg(BaseModel):
    token: str
    filename: str
    sample_data_token: str

class Attribute(BaseModel):
    token: str
    name: str
    description: str

class Visibility(BaseModel):
    token: str
    level: str
    description: str

# API endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to nuScenes API"}

# Log endpoints
@app.get("/logs/", response_model=List[Log])
async def get_logs(skip: int = 0, limit: int = 100, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM log OFFSET %s LIMIT %s", (skip, limit))
    logs = cur.fetchall()
    cur.close()
    return logs

@app.get("/logs/{token}", response_model=Log)
async def get_log(token: str, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM log WHERE token = %s", (token,))
    log = cur.fetchone()
    cur.close()
    if log is None:
        raise HTTPException(status_code=404, detail="Log not found")
    return log

# Sensor endpoints
@app.get("/sensors/", response_model=List[Sensor])
async def get_sensors(skip: int = 0, limit: int = 100, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM sensor OFFSET %s LIMIT %s", (skip, limit))
    sensors = cur.fetchall()
    cur.close()
    return sensors

@app.get("/sensors/{token}", response_model=Sensor)
async def get_sensor(token: str, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM sensor WHERE token = %s", (token,))
    sensor = cur.fetchone()
    cur.close()
    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return sensor

# Sample endpoints
@app.get("/samples/")
async def get_samples(skip: int = 0, limit: int = 100, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM sample OFFSET %s LIMIT %s", (skip, limit))
    samples = cur.fetchall()
    cur.close()
    return samples

@app.get("/samples/{token}")
async def get_sample(token: str, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM sample WHERE token = %s", (token,))
    sample = cur.fetchone()
    cur.close()
    if sample is None:
        raise HTTPException(status_code=404, detail="Sample not found")
    return sample

# Sample data endpoints
@app.get("/sample_data/")
async def get_sample_data(skip: int = 0, limit: int = 100, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM sample_data OFFSET %s LIMIT %s", (skip, limit))
    sample_data = cur.fetchall()
    cur.close()
    return sample_data

@app.get("/sample_data/{token}")
async def get_sample_data_by_token(token: str, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM sample_data WHERE token = %s", (token,))
    data = cur.fetchone()
    cur.close()
    if data is None:
        raise HTTPException(status_code=404, detail="Sample data not found")
    return data

# Scene endpoints
@app.get("/scenes/")
async def get_scenes(skip: int = 0, limit: int = 100, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM scenes OFFSET %s LIMIT %s", (skip, limit))
    scenes = cur.fetchall()
    cur.close()
    return scenes

@app.get("/scenes/{token}")
async def get_scene(token: str, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM scenes WHERE scene_token = %s", (token,))
    scene = cur.fetchone()
    cur.close()
    if scene is None:
        raise HTTPException(status_code=404, detail="Scene not found")
    return scene

# Add more endpoints for other tables...

# Advanced query endpoints
@app.get("/scene_samples/{scene_token}")
async def get_samples_by_scene(scene_token: str, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("""
        SELECT s.* FROM sample s
        WHERE s.scene_token = %s
        ORDER BY s.timestamp
    """, (scene_token,))
    samples = cur.fetchall()
    cur.close()
    return samples

@app.get("/sample_annotations/{sample_token}")
async def get_annotations_by_sample(sample_token: str, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("""
        SELECT sa.*, c.name as category_name 
        FROM sample_annotation sa
        JOIN instance i ON sa.instance_token = i.token
        JOIN category c ON i.category_token = c.token
        WHERE sa.sample_token = %s
    """, (sample_token,))
    annotations = cur.fetchall()
    cur.close()
    return annotations

# Ego Pose endpoints
@app.get("/ego_poses/", response_model=List[EgoPose])
async def get_ego_poses(skip: int = 0, limit: int = 100, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM ego_pose OFFSET %s LIMIT %s", (skip, limit))
    ego_poses = cur.fetchall()
    cur.close()
    return ego_poses

@app.get("/ego_poses/{token}", response_model=EgoPose)
async def get_ego_pose(token: str, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM ego_pose WHERE token = %s", (token,))
    ego_pose = cur.fetchone()
    cur.close()
    if ego_pose is None:
        raise HTTPException(status_code=404, detail="Ego pose not found")
    return ego_pose

# Calibrated Sensor endpoints
@app.get("/calibrated_sensors/", response_model=List[CalibratedSensor])
async def get_calibrated_sensors(skip: int = 0, limit: int = 100, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM calibrated_sensor OFFSET %s LIMIT %s", (skip, limit))
    sensors = cur.fetchall()
    cur.close()
    return sensors

@app.get("/calibrated_sensors/{token}", response_model=CalibratedSensor)
async def get_calibrated_sensor(token: str, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM calibrated_sensor WHERE token = %s", (token,))
    sensor = cur.fetchone()
    cur.close()
    if sensor is None:
        raise HTTPException(status_code=404, detail="Calibrated sensor not found")
    return sensor

# Sample Annotation endpoints
@app.get("/sample_annotations/", response_model=List[SampleAnnotation])
async def get_sample_annotations(skip: int = 0, limit: int = 100, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM sample_annotation OFFSET %s LIMIT %s", (skip, limit))
    annotations = cur.fetchall()
    cur.close()
    return annotations

@app.get("/sample_annotations/{token}", response_model=SampleAnnotation)
async def get_sample_annotation(token: str, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM sample_annotation WHERE token = %s", (token,))
    annotation = cur.fetchone()
    cur.close()
    if annotation is None:
        raise HTTPException(status_code=404, detail="Sample annotation not found")
    return annotation

# Map endpoints
@app.get("/maps/", response_model=List[Map])
async def get_maps(skip: int = 0, limit: int = 100, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM map OFFSET %s LIMIT %s", (skip, limit))
    maps = cur.fetchall()
    cur.close()
    return maps

@app.get("/maps/{token}", response_model=Map)
async def get_map(token: str, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM map WHERE token = %s", (token,))
    map_data = cur.fetchone()
    cur.close()
    if map_data is None:
        raise HTTPException(status_code=404, detail="Map not found")
    return map_data

# Lidarseg endpoints
@app.get("/lidarsegs/", response_model=List[Lidarseg])
async def get_lidarsegs(skip: int = 0, limit: int = 100, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM lidarseg OFFSET %s LIMIT %s", (skip, limit))
    lidarsegs = cur.fetchall()
    cur.close()
    return lidarsegs

@app.get("/lidarsegs/{token}", response_model=Lidarseg)
async def get_lidarseg(token: str, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM lidarseg WHERE token = %s", (token,))
    lidarseg = cur.fetchone()
    cur.close()
    if lidarseg is None:
        raise HTTPException(status_code=404, detail="Lidarseg not found")
    return lidarseg

# Attribute endpoints
@app.get("/attributes/", response_model=List[Attribute])
async def get_attributes(skip: int = 0, limit: int = 100, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM attribute OFFSET %s LIMIT %s", (skip, limit))
    attributes = cur.fetchall()
    cur.close()
    return attributes

@app.get("/attributes/{token}", response_model=Attribute)
async def get_attribute(token: str, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM attribute WHERE token = %s", (token,))
    attribute = cur.fetchone()
    cur.close()
    if attribute is None:
        raise HTTPException(status_code=404, detail="Attribute not found")
    return attribute

# Visibility endpoints
@app.get("/visibilities/", response_model=List[Visibility])
async def get_visibilities(skip: int = 0, limit: int = 100, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM visibility OFFSET %s LIMIT %s", (skip, limit))
    visibilities = cur.fetchall()
    cur.close()
    return visibilities

@app.get("/visibilities/{token}", response_model=Visibility)
async def get_visibility(token: str, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM visibility WHERE token = %s", (token,))
    visibility = cur.fetchone()
    cur.close()
    if visibility is None:
        raise HTTPException(status_code=404, detail="Visibility not found")
    return visibility

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=API_HOST,
        port=API_PORT
    )