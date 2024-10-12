CREATE TABLE log (
    log_token VARCHAR(255) PRIMARY KEY,
    vehicle VARCHAR(255),
    date_captured TIMESTAMP,
    location VARCHAR(255)
);

CREATE TABLE ego_pose (
    ego_pose_token VARCHAR(255) PRIMARY KEY,
    translation VARCHAR(255),
    rotation VARCHAR(255),
    timestamp TIMESTAMP
);

CREATE TABLE calibrated_sensor (
    sensor_token VARCHAR(255) PRIMARY KEY,
    translation VARCHAR(255),
    rotation VARCHAR(255),
    camera_intrinsic TEXT
);

CREATE TABLE sensor (
    sensor_token VARCHAR(255) PRIMARY KEY,
    channel VARCHAR(255),
    modality VARCHAR(255)
);

CREATE TABLE category (
    category_token VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    index INT
);

CREATE TABLE attribute (
    attribute_token VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    description TEXT
);

CREATE TABLE visibility (
    visibility_token VARCHAR(255) PRIMARY KEY,
    level VARCHAR(255),
    description TEXT
);

CREATE TABLE map (
    log_token VARCHAR(255),
    category VARCHAR(255),
    filename VARCHAR(255),
    FOREIGN KEY (log_token) REFERENCES log(log_token)
);

CREATE TABLE scene (
    scene_token VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    log_token VARCHAR(255),
    nbr_samples INT,
    first_sample_token VARCHAR(255),
    last_sample_token VARCHAR(255),
    FOREIGN KEY (log_token) REFERENCES log(log_token)
);

CREATE TABLE sample (
    sample_token VARCHAR(255) PRIMARY KEY,
    timestamp TIMESTAMP,
    scene_token VARCHAR(255),
    next VARCHAR(255),
    prev VARCHAR(255),
    FOREIGN KEY (scene_token) REFERENCES scene(scene_token),
    FOREIGN KEY (next) REFERENCES sample(sample_token),
    FOREIGN KEY (prev) REFERENCES sample(sample_token)
);

CREATE TABLE sample_data (
    sample_data_token VARCHAR(255) PRIMARY KEY,
    sample_token VARCHAR(255),
    ego_pose_token VARCHAR(255),
    calibrated_sensor_token VARCHAR(255),
    filename VARCHAR(255),
    fileformat VARCHAR(50),
    width INT,
    height INT,
    timestamp TIMESTAMP,
    is_key_frame BOOLEAN,
    next VARCHAR(255),
    prev VARCHAR(255),
    FOREIGN KEY (sample_token) REFERENCES sample(sample_token),
    FOREIGN KEY (ego_pose_token) REFERENCES ego_pose(ego_pose_token),
    FOREIGN KEY (calibrated_sensor_token) REFERENCES calibrated_sensor(sensor_token),
    FOREIGN KEY (next) REFERENCES sample_data(sample_data_token),
    FOREIGN KEY (prev) REFERENCES sample_data(sample_data_token)
);

CREATE TABLE instance (
    instance_token VARCHAR(255) PRIMARY KEY,
    category_token VARCHAR(255),
    nbr_annotations INT,
    first_annotation_token VARCHAR(255),
    last_annotation_token VARCHAR(255),
    FOREIGN KEY (category_token) REFERENCES category(category_token)
);

CREATE TABLE sample_annotation (
    sample_annotation_token VARCHAR(255) PRIMARY KEY,
    sample_token VARCHAR(255),
    instance_token VARCHAR(255),
    attribute_tokens TEXT,
    visibility_token VARCHAR(255),
    translation VARCHAR(255),
    size VARCHAR(255),
    rotation VARCHAR(255),
    num_lidar_pts INT,
    num_radar_pts INT,
    next VARCHAR(255),
    prev VARCHAR(255),
    FOREIGN KEY (sample_token) REFERENCES sample(sample_token),
    FOREIGN KEY (instance_token) REFERENCES instance(instance_token),
    FOREIGN KEY (visibility_token) REFERENCES visibility(visibility_token),
    FOREIGN KEY (next) REFERENCES sample_annotation(sample_annotation_token),
    FOREIGN KEY (prev) REFERENCES sample_annotation(sample_annotation_token)
);

CREATE TABLE lidarseg (
    lidarseg_token VARCHAR(255) PRIMARY KEY,
    filename VARCHAR(255),
    sample_data_token VARCHAR(255),
    FOREIGN KEY (sample_data_token) REFERENCES sample_data(sample_data_token)
);
