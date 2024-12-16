from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional, Dict
from pydantic import BaseModel
import os

app = FastAPI(title="nuScenes API")

# Database connection settings
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

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
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor
    )
    try:
        yield conn
    finally:
        conn.close()

# Pydantic models
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

class Visibility(BaseModel):
    token: str
    level: str
    description: str

class Attribute(BaseModel):
    token: str
    name: str
    description: str

class Category(BaseModel):
    token: str
    name: str
    description: str
    index: int

class Instance(BaseModel):
    token: str
    category_token: str
    nbr_annotations: int
    first_annotation_token: str
    last_annotation_token: str

class Scene(BaseModel):
    scene_token: str
    name: str
    description: str
    log_token: str
    nbr_samples: int
    first_sample_token: str
    last_sample_token: str

class Sample(BaseModel):
    token: str
    timestamp: int
    scene_token: str
    next: Optional[str]
    prev: Optional[str]

class EgoPose(BaseModel):
    token: str
    translation: Dict
    rotation: Dict
    timestamp: int

class CalibratedSensor(BaseModel):
    token: str
    sensor_token: str
    translation: Dict
    rotation: Dict
    camera_intrinsic: Optional[Dict]

class SampleData(BaseModel):
    token: str
    sample_token: str
    ego_pose_token: str
    calibrated_sensor_token: str
    timestamp: int
    fileformat: str
    is_key_frame: bool
    height: int
    width: int
    filename: str
    prev: Optional[str]
    next: Optional[str]

class SampleAnnotation(BaseModel):
    token: str
    sample_token: str
    instance_token: str
    visibility_token: str
    translation: Dict
    size: Dict
    rotation: Dict
    num_lidar_pts: int
    num_radar_pts: int
    next: Optional[str]
    prev: Optional[str]

class Lidarseg(BaseModel):
    token: str
    filename: str
    sample_data_token: str

class Map(BaseModel):
    token: str
    log_tokens: List[str]
    category: str
    filename: str

# API Endpoints

@app.get("/")
def read_root():
    return {"message": "Welcome to nuScenes API"}

# Log endpoints
@app.get("/logs", response_model=List[Log])
async def get_logs(db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM log")
    logs = cur.fetchall()
    cur.close()
    return logs

@app.get("/logs/{token}", response_model=Log)
async def get_log(token: str, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM log WHERE token = %s", (token,))
    log = cur.fetchone()
    cur.close()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log

# Sensor endpoints
@app.get("/sensors", response_model=List[Sensor])
async def get_sensors(db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM sensor")
    sensors = cur.fetchall()
    cur.close()
    return sensors

@app.get("/sensors/{token}", response_model=Sensor)
async def get_sensor(token: str, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM sensor WHERE token = %s", (token,))
    sensor = cur.fetchone()
    cur.close()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return sensor

# Visibility endpoints
@app.get("/visibility", response_model=List[Visibility])
async def get_visibility_all(db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM visibility")
    visibility = cur.fetchall()
    cur.close()
    return visibility

@app.get("/visibility/{token}", response_model=Visibility)
async def get_visibility(token: str, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM visibility WHERE token = %s", (token,))
    visibility = cur.fetchone()
    cur.close()
    if not visibility:
        raise HTTPException(status_code=404, detail="Visibility not found")
    return visibility

# Attribute endpoints
@app.get("/attributes", response_model=List[Attribute])
async def get_attributes(db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM attribute")
    attributes = cur.fetchall()
    cur.close()
    return attributes

@app.get("/attributes/{token}", response_model=Attribute)
async def get_attribute(token: str, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM attribute WHERE token = %s", (token,))
    attribute = cur.fetchone()
    cur.close()
    if not attribute:
        raise HTTPException(status_code=404, detail="Attribute not found")
    return attribute

# Category endpoints
@app.get("/categories", response_model=List[Category])
async def get_categories(db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM category")
    categories = cur.fetchall()
    cur.close()
    return categories

@app.get("/categories/{token}", response_model=Category)
async def get_category(token: str, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM category WHERE token = %s", (token,))
    category = cur.fetchone()
    cur.close()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

# Instance endpoints
@app.get("/instances", response_model=List[Instance])
async def get_instances(db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM instance")
    instances = cur.fetchall()
    cur.close()
    return instances

@app.get("/instances/{token}", response_model=Instance)
async def get_instance(token: str, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM instance WHERE token = %s", (token,))
    instance = cur.fetchone()
    cur.close()
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    return instance

# Scene endpoints
@app.get("/scenes", response_model=List[Scene])
async def get_scenes(db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM scenes")
    scenes = cur.fetchall()
    cur.close()
    return scenes

@app.get("/scenes/{token}", response_model=Scene)
async def get_scene(token: str, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM scenes WHERE scene_token = %s", (token,))
    scene = cur.fetchone()
    cur.close()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    return scene

# Sample endpoints
@app.get("/samples", response_model=List[Sample])
async def get_samples(db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM sample")
    samples = cur.fetchall()
    cur.close()
    return samples

@app.get("/samples/{token}", response_model=Sample)
async def get_sample(token: str, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM sample WHERE token = %s", (token,))
    sample = cur.fetchone()
    cur.close()
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    return sample

# EgoPose endpoints
@app.get("/ego_poses", response_model=List[EgoPose])
async def get_ego_poses(db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM ego_pose")
    ego_poses = cur.fetchall()
    cur.close()
    return ego_poses

@app.get("/ego_poses/{token}", response_model=EgoPose)
async def get_ego_pose(token: str, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM ego_pose WHERE token = %s", (token,))
    ego_pose = cur.fetchone()
    cur.close()
    if not ego_pose:
        raise HTTPException(status_code=404, detail="EgoPose not found")
    return ego_pose

# CalibratedSensor endpoints
@app.get("/calibrated_sensors", response_model=List[CalibratedSensor])
async def get_calibrated_sensors(db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM calibrated_sensor")
    sensors = cur.fetchall()
    cur.close()
    return sensors

@app.get("/calibrated_sensors/{token}", response_model=CalibratedSensor)
async def get_calibrated_sensor(token: str, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM calibrated_sensor WHERE token = %s", (token,))
    sensor = cur.fetchone()
    cur.close()
    if not sensor:
        raise HTTPException(status_code=404, detail="CalibratedSensor not found")
    return sensor

# SampleData endpoints
@app.get("/sample_data", response_model=List[SampleData])
async def get_sample_data_all(db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM sample_data")
    data = cur.fetchall()
    cur.close()
    return data

@app.get("/sample_data/{token}", response_model=SampleData)
async def get_sample_data(token: str, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM sample_data WHERE token = %s", (token,))
    data = cur.fetchone()
    cur.close()
    if not data:
        raise HTTPException(status_code=404, detail="SampleData not found")
    return data

# SampleAnnotation endpoints
@app.get("/sample_annotations", response_model=List[SampleAnnotation])
async def get_sample_annotations(db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM sample_annotation")
    annotations = cur.fetchall()
    cur.close()
    return annotations

@app.get("/sample_annotations/{token}", response_model=SampleAnnotation)
async def get_sample_annotation(token: str, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM sample_annotation WHERE token = %s", (token,))
    annotation = cur.fetchone()
    cur.close()
    if not annotation:
        raise HTTPException(status_code=404, detail="SampleAnnotation not found")
    return annotation

# Lidarseg endpoints
@app.get("/lidarsegs", response_model=List[Lidarseg])
async def get_lidarsegs(db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM lidarseg")
    lidarsegs = cur.fetchall()
    cur.close()
    return lidarsegs

@app.get("/lidarsegs/{token}", response_model=Lidarseg)
async def get_lidarseg(token: str, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM lidarseg WHERE token = %s", (token,))
    lidarseg = cur.fetchone()
    cur.close()
    if not lidarseg:
        raise HTTPException(status_code=404, detail="Lidarseg not found")
    return lidarseg

# Map endpoints
@app.get("/maps", response_model=List[Map])
async def get_maps(db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM map")
    maps = cur.fetchall()
    cur.close()
    return maps

@app.get("/maps/{token}", response_model=Map)
async def get_map(token: str, db: psycopg2.extensions.connection = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT * FROM map WHERE token = %s", (token,))
    map_data = cur.fetchone()
    cur.close()
    if not map_data:
        raise HTTPException(status_code=404, detail="Map not found")
    return map_data

# Health check endpoint
@app.get("/health")
def health_check():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)