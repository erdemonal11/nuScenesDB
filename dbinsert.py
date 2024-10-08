import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
database = os.getenv('DB_NAME')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')

engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')

def insert_dataframe_to_db(df, table_name, engine):
    df.to_sql(table_name, con=engine, if_exists='append', index=False)

# Table: log
log_data = pd.DataFrame({
    'log_token': ['log_1', 'log_2'],
    'vehicle': ['car', 'truck'],
    'date_captured': ['2024-01-01', '2024-01-02'],
    'location': ['San Francisco', 'New York']
})

# Table: ego_pose
ego_pose_data = pd.DataFrame({
    'ego_pose_token': ['ego_pose_1', 'ego_pose_2'],
    'translation': ['10,20,30', '40,50,60'],
    'rotation': ['0,0,0,1', '0,0,1,0'],
    'timestamp': ['2024-01-01 00:00:00', '2024-01-02 00:00:00']
})

# Table: calibrated_sensor
calibrated_sensor_data = pd.DataFrame({
    'sensor_token': ['sensor_1', 'sensor_2'],
    'translation': ['10,20,30', '40,50,60'],
    'rotation': ['0,0,0,1', '0,0,1,0'],
    'camera_intrinsic': ['intrinsic_1', 'intrinsic_2']
})

# Table: sensor
sensor_data = pd.DataFrame({
    'sensor_token': ['sensor_1', 'sensor_2'],
    'channel': ['channel_1', 'channel_2'],
    'modality': ['modality_1', 'modality_2']
})

# Table: category
category_data = pd.DataFrame({
    'category_token': ['cat_1', 'cat_2'],
    'name': ['pedestrian', 'vehicle'],
    'description': ['A person', 'A vehicle'],
    'index': [1, 2]
})

# Table: attribute
attribute_data = pd.DataFrame({
    'attribute_token': ['attr_1', 'attr_2'],
    'name': ['speed', 'size'],
    'description': ['Vehicle speed', 'Vehicle size']
})

# Table: visibility
visibility_data = pd.DataFrame({
    'visibility_token': ['vis_1', 'vis_2'],
    'level': ['high', 'low'],
    'description': ['Highly visible', 'Low visibility']
})

# Table: scene
scene_data = pd.DataFrame({
    'scene_token': ['scene_1', 'scene_2'],
    'name': ['scene_1_name', 'scene_2_name'],
    'description': ['First scene', 'Second scene'],
    'log_token': ['log_1', 'log_2'],
    'nbr_samples': [10, 20],
    'first_sample_token': ['sample_1', 'sample_2'],
    'last_sample_token': ['sample_3', 'sample_4']
})

# Table: sample
sample_data = pd.DataFrame({
    'sample_token': ['sample_1', 'sample_2'],
    'timestamp': ['2024-01-01 00:00:00', '2024-01-02 00:00:00'],
    'scene_token': ['scene_1', 'scene_2'],
    'next': ['sample_2', 'sample_3'],
    'prev': [None, 'sample_1']
})

# Table: sample_data
sample_data_data = pd.DataFrame({
    'sample_data_token': ['sd_1', 'sd_2'],
    'sample_token': ['sample_1', 'sample_2'],
    'ego_pose_token': ['ego_pose_1', 'ego_pose_2'],
    'calibrated_sensor_token': ['sensor_1', 'sensor_2'],
    'filename': ['file_1', 'file_2'],
    'fileformat': ['png', 'jpeg'],
    'width': [1920, 1080],
    'height': [1080, 720],
    'timestamp': ['2024-01-01 00:00:00', '2024-01-02 00:00:00'],
    'is_key_frame': [True, False],
    'next': ['sd_2', None],
    'prev': [None, 'sd_1']
})

# Table: instance
instance_data = pd.DataFrame({
    'instance_token': ['inst_1', 'inst_2'],
    'category_token': ['cat_1', 'cat_2'],
    'nbr_annotations': [5, 10],
    'first_annotation_token': ['annot_1', 'annot_2'],
    'last_annotation_token': ['annot_3', 'annot_4']
})

# Table: sample_annotation
sample_annotation_data = pd.DataFrame({
    'sample_annotation_token': ['annot_1', 'annot_2'],
    'sample_token': ['sample_1', 'sample_2'],
    'instance_token': ['inst_1', 'inst_2'],
    'attribute_tokens': ['attr_1', 'attr_2'],
    'visibility_token': ['vis_1', 'vis_2'],
    'translation': ['10,20,30', '40,50,60'],
    'size': ['small', 'large'],
    'rotation': ['0,0,0,1', '0,0,1,0'],
    'num_lidar_pts': [100, 200],
    'num_radar_pts': [50, 100],
    'next': ['annot_2', None],
    'prev': [None, 'annot_1']
})

insert_dataframe_to_db(log_data, 'log', engine)
insert_dataframe_to_db(ego_pose_data, 'ego_pose', engine)
insert_dataframe_to_db(calibrated_sensor_data, 'calibrated_sensor', engine)
insert_dataframe_to_db(sensor_data, 'sensor', engine)
insert_dataframe_to_db(category_data, 'category', engine)
insert_dataframe_to_db(attribute_data, 'attribute', engine)
insert_dataframe_to_db(visibility_data, 'visibility', engine)
insert_dataframe_to_db(scene_data, 'scene', engine)
insert_dataframe_to_db(sample_data, 'sample', engine)
insert_dataframe_to_db(sample_data_data, 'sample_data', engine)
insert_dataframe_to_db(instance_data, 'instance', engine)
insert_dataframe_to_db(sample_annotation_data, 'sample_annotation', engine)

update_sql = text("""
    UPDATE sample
    SET next = 'sample_2'
    WHERE sample_token = 'sample_1'
""")

with engine.connect() as connection:
    connection.execute(update_sql)

engine.dispose()

print("Data inserted and updated successfully!")
