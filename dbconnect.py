import psycopg2
import os
from dotenv import load_dotenv
from nuscenes.nuscenes import NuScenes
import json

load_dotenv()

host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
database = os.getenv('DB_NAME')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')

sql_file_path = os.getenv('SQL_FILE_PATH', '/app/nuScene.sql')

connection = None
cursor = None

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT')
    )

try:
    connection = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )
    cursor = connection.cursor()

    with open(sql_file_path, 'r') as file:
        sql_commands = file.read()
    cursor.execute(sql_commands)
    connection.commit()

    dataroot = os.getenv('NUSCENES_DATAROOT', '/mnt/c/Users/mrifk/Desktop/v1.0-mini')

    # Initialize NuScenes with the correct path
    nusc = NuScenes(version='v1.0-mini', dataroot=dataroot, verbose=True)

    print(f"Number of visibility records: {len(nusc.visibility)}")
    insert_visibility_query = """
    INSERT INTO visibility (token, level, description)
    VALUES (%s, %s, %s)
    """
    for visibility in nusc.visibility:
        cursor.execute(insert_visibility_query, (
            visibility['token'],
            visibility['level'],
            visibility['description']
        ))
    connection.commit()
    print("Visibility records inserted successfully.")

    print(f"Number of log records: {len(nusc.log)}")
    insert_log_query = """
    INSERT INTO log (token, logfile, vehicle, date_captured, location)
    VALUES (%s, %s, %s, %s, %s)
    """
    for log in nusc.log:
        cursor.execute(insert_log_query, (
            log['token'],
            log['logfile'],
            log['vehicle'],
            log['date_captured'],
            log['location']
        ))

    print(f"Number of sensor records: {len(nusc.sensor)}")
    insert_sensor_query = """
    INSERT INTO sensor (token, channel, modality)
    VALUES (%s, %s, %s)
    """
    for sensor in nusc.sensor:
        cursor.execute(insert_sensor_query, (
            sensor['token'],
            sensor['channel'],
            sensor['modality']
        ))

    print(f"Number of category records: {len(nusc.category)}")
    insert_category_query = """
    INSERT INTO category (token, name, description, index)
    VALUES (%s, %s, %s, %s)
    """
    for category in nusc.category:
        cursor.execute(insert_category_query, (
            category['token'],
            category['name'],
            category['description'],
            category.get('index', None)
        ))

    print(f"Number of instance records: {len(nusc.instance)}")
    insert_instance_query = """
    INSERT INTO instance (token, category_token, nbr_annotations, first_annotation_token, last_annotation_token)
    VALUES (%s, %s, %s, %s, %s)
    """
    for instance in nusc.instance:
        cursor.execute(insert_instance_query, (
            instance['token'],
            instance['category_token'],
            instance['nbr_annotations'],
            instance['first_annotation_token'],
            instance['last_annotation_token']
        ))

    print(f"Number of scenes records: {len(nusc.scene)}")
    insert_scene_query = """
    INSERT INTO scenes (scene_token, name, description, log_token, nbr_samples, first_sample_token, last_sample_token)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    for scene in nusc.scene:
        cursor.execute(insert_scene_query, (
            scene['token'],
            scene['name'],
            scene['description'],
            scene['log_token'],
            scene['nbr_samples'],
            scene['first_sample_token'],
            scene['last_sample_token']
        ))

    print(f"Number of sample records: {len(nusc.sample)}")
    insert_sample_query = """
    INSERT INTO sample (token, timestamp, scene_token)
    VALUES (%s, %s, %s)
    """
    for sample in nusc.sample:
        cursor.execute(insert_sample_query, (
            sample['token'],
            sample['timestamp'],
            sample['scene_token']
        ))

    update_sample_query = """
    UPDATE sample
    SET prev = %s, next = %s
    WHERE token = %s
    """
    for sample in nusc.sample:
        cursor.execute(update_sample_query, (
            sample['prev'] if sample['prev'] else None,
            sample['next'] if sample['next'] else None,
            sample['token']
        ))

    print(f"Number of sample_annotation records: {len(nusc.sample_annotation)}")
    insert_sample_annotation_query = """
    INSERT INTO sample_annotation (token, sample_token, instance_token, visibility_token, translation, size, rotation, num_lidar_pts, num_radar_pts)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    for annotation in nusc.sample_annotation:
        cursor.execute(insert_sample_annotation_query, (
            annotation['token'],
            annotation['sample_token'],
            annotation['instance_token'],
            annotation['visibility_token'],
            json.dumps(annotation['translation']),
            json.dumps(annotation['size']),
            json.dumps(annotation['rotation']),
            annotation['num_lidar_pts'],
            annotation['num_radar_pts']
        ))

    update_sample_annotation_query = """
    UPDATE sample_annotation
    SET next = %s, prev = %s
    WHERE token = %s
    """
    for annotation in nusc.sample_annotation:
        cursor.execute(update_sample_annotation_query, (
            annotation['next'] if annotation['next'] else None,
            annotation['prev'] if annotation['prev'] else None,
            annotation['token']
        ))

    print("Inserting sample_annotation records completed.")
    connection.commit()

    print(f"Number of attribute records: {len(nusc.attribute)}")
    insert_attribute_query = """
    INSERT INTO attribute (token, name, description)
    VALUES (%s, %s, %s)
    ON CONFLICT (token) DO NOTHING
    """
    for attribute in nusc.attribute:
        try:
            cursor.execute(insert_attribute_query, (
                attribute['token'],
                attribute['name'],
                attribute['description']
            ))
            print(f"Inserted attribute: {attribute['name']}")
        except Exception as e:
            print(f"Error inserting attribute {attribute['name']}: {e}")
    
    connection.commit()
    print("Attribute records inserted successfully.")

    print(f"Number of ego_pose records: {len(nusc.ego_pose)}")
    insert_ego_pose_query = """
    INSERT INTO ego_pose (token, translation, rotation, timestamp)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (token) DO NOTHING
    """
    for ego_pose in nusc.ego_pose:
        try:
            cursor.execute(insert_ego_pose_query, (
                ego_pose['token'],
                json.dumps(ego_pose['translation']),
                json.dumps(ego_pose['rotation']),
                ego_pose['timestamp']
            ))
            print(f"Inserted ego_pose: {ego_pose['token']}")
        except Exception as e:
            print(f"Error inserting ego_pose {ego_pose['token']}: {e}")
    connection.commit()
    print("Ego pose records inserted successfully.")

    print(f"Number of calibrated_sensor records: {len(nusc.calibrated_sensor)}")
    insert_calibrated_sensor_query = """
    INSERT INTO calibrated_sensor (token, sensor_token, translation, rotation, camera_intrinsic)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (token) DO NOTHING
    """
    for calibrated_sensor in nusc.calibrated_sensor:
        try:
            cursor.execute(insert_calibrated_sensor_query, (
                calibrated_sensor['token'],
                calibrated_sensor['sensor_token'],
                json.dumps(calibrated_sensor['translation']),
                json.dumps(calibrated_sensor['rotation']),
                json.dumps(calibrated_sensor['camera_intrinsic']) if calibrated_sensor['camera_intrinsic'] else None
            ))
            print(f"Inserted calibrated_sensor: {calibrated_sensor['token']}")
        except Exception as e:
            print(f"Error inserting calibrated_sensor {calibrated_sensor['token']}: {e}")
    connection.commit()
    print("Calibrated sensor records inserted successfully.")

    # Disable foreign key constraint temporarily
    cursor.execute("ALTER TABLE sample_data DROP CONSTRAINT IF EXISTS sample_data_next_fkey;")
    connection.commit()

    print(f"Number of sample_data records: {len(nusc.sample_data)}")
    insert_sample_data_query = """
    INSERT INTO sample_data (
        token, sample_token, ego_pose_token, calibrated_sensor_token,
        timestamp, fileformat, is_key_frame, height, width, filename,
        prev, next
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    """
    
    print(f"Number of sample_data records to process: {len(nusc.sample_data)}")
    for sample_data in nusc.sample_data:
        try:
            cursor.execute(insert_sample_data_query, (
                sample_data['token'],
                sample_data['sample_token'],
                sample_data['ego_pose_token'],
                sample_data['calibrated_sensor_token'],
                sample_data['timestamp'],
                sample_data['fileformat'],
                sample_data['is_key_frame'],
                sample_data['height'],
                sample_data['width'], 
                sample_data['filename'],
                sample_data['prev'],
                sample_data['next'] if sample_data['next'] else None
            ))
            connection.commit()
            
        except Exception as e:
            print(f"Error processing {sample_data['token']}: {str(e)}")
            print("Data:", {k: v for k, v in sample_data.items() if k != 'data'})
            connection.rollback()

    # Re-enable foreign key constraint after all inserts
    cursor.execute("""
    ALTER TABLE sample_data 
    ADD CONSTRAINT sample_data_next_fkey 
    FOREIGN KEY (next) 
    REFERENCES sample_data(token)
    DEFERRABLE INITIALLY DEFERRED;
    """)
    connection.commit()

    # Verify the insertions
    cursor.execute("SELECT COUNT(*) FROM sample_data")
    count = cursor.fetchone()[0]
    print(f"Total sample_data records in database: {count}")

    print(f"Number of map records: {len(nusc.map)}")
    insert_map_query = """
    INSERT INTO map (token, log_tokens, category, filename)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (token) DO NOTHING
    """
    for map_data in nusc.map:
        try:
            cursor.execute(insert_map_query, (
                map_data['token'],
                map_data['log_tokens'],
                map_data['category'],
                map_data['filename']
            ))
            print(f"Inserted map: {map_data['token']}")
        except Exception as e:
            print(f"Error inserting map {map_data['token']}: {e}")
    connection.commit()
    print("Map records inserted successfully.")

    if hasattr(nusc, 'lidarseg'):
        print(f"Number of lidarseg records: {len(nusc.lidarseg)}")
        insert_lidarseg_query = """
        INSERT INTO lidarseg (token, filename, sample_data_token)
        VALUES (%s, %s, %s)
        """
        for lidarseg in nusc.lidarseg:
            cursor.execute(insert_lidarseg_query, (
                lidarseg['token'],
                lidarseg['filename'],
                lidarseg['sample_data_token']
            ))
    else:
        print("Lidarseg data not available in this dataset")

except Exception as error:
    print(f"An error occurred: {error}")
    connection.rollback()

finally:
    if cursor is not None:
        cursor.close()
    if connection is not None:
        connection.close()

