-- First drop dependent tables (in reverse order of dependencies)
DROP TABLE IF EXISTS lidarseg CASCADE;
DROP TABLE IF EXISTS map CASCADE;
DROP TABLE IF EXISTS sample_annotation CASCADE;
DROP TABLE IF EXISTS sample_data CASCADE;
DROP TABLE IF EXISTS calibrated_sensor CASCADE;
DROP TABLE IF EXISTS ego_pose CASCADE;
DROP TABLE IF EXISTS sample CASCADE;
DROP TABLE IF EXISTS scenes CASCADE;
DROP TABLE IF EXISTS instance CASCADE;

-- Then drop independent tables
DROP TABLE IF EXISTS category CASCADE;
DROP TABLE IF EXISTS attribute CASCADE;
DROP TABLE IF EXISTS visibility CASCADE;
DROP TABLE IF EXISTS sensor CASCADE;
DROP TABLE IF EXISTS log CASCADE;

-- Independent tables
CREATE TABLE log (
    token VARCHAR(255) PRIMARY KEY,
    logfile VARCHAR(255),
    vehicle VARCHAR(255),
    date_captured DATE,
    location VARCHAR(255)
);

CREATE TABLE sensor (
    token VARCHAR(255) PRIMARY KEY,
    channel VARCHAR(255),
    modality VARCHAR(50)
);

CREATE TABLE visibility (
    token VARCHAR(255) PRIMARY KEY,
    level VARCHAR(50),
    description TEXT
);

CREATE TABLE attribute (
    token VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    description TEXT
);

CREATE TABLE category (
    token VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    index INT
);

-- Dependent tables
CREATE TABLE instance (
    token VARCHAR(255) PRIMARY KEY,
    category_token VARCHAR(255),
    nbr_annotations INT,
    first_annotation_token VARCHAR(255),
    last_annotation_token VARCHAR(255),
    FOREIGN KEY (category_token) REFERENCES category(token)
);

CREATE TABLE scenes (
    scene_token VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    log_token VARCHAR(255),
    nbr_samples INT,
    first_sample_token VARCHAR(255),
    last_sample_token VARCHAR(255),
    FOREIGN KEY (log_token) REFERENCES log(token)
);

CREATE TABLE sample (
    token VARCHAR(255) PRIMARY KEY,
    timestamp BIGINT,
    scene_token VARCHAR(255),
    next VARCHAR(255),
    prev VARCHAR(255),
    FOREIGN KEY (scene_token) REFERENCES scenes(scene_token),
    FOREIGN KEY (next) REFERENCES sample(token),
    FOREIGN KEY (prev) REFERENCES sample(token)
);


CREATE TABLE ego_pose (
    token VARCHAR(255) PRIMARY KEY,
    translation JSONB,
    rotation JSONB,
    timestamp BIGINT
);

CREATE TABLE calibrated_sensor (
    token VARCHAR(255) PRIMARY KEY,
    sensor_token VARCHAR(255),
    translation JSONB,
    rotation JSONB,
    camera_intrinsic JSONB,
    FOREIGN KEY (sensor_token) REFERENCES sensor(token)
);

CREATE TABLE sample_data (
    token VARCHAR(255) PRIMARY KEY,
    sample_token VARCHAR(255),
    ego_pose_token VARCHAR(255),
    calibrated_sensor_token VARCHAR(255),
    filename VARCHAR(255),
    fileformat VARCHAR(50),
    width INT,
    height INT,
    timestamp BIGINT,
    is_key_frame BOOLEAN,
    next VARCHAR(255),
    prev VARCHAR(255),
    FOREIGN KEY (sample_token) REFERENCES sample(token),
    FOREIGN KEY (ego_pose_token) REFERENCES ego_pose(token),
    FOREIGN KEY (calibrated_sensor_token) REFERENCES calibrated_sensor(token),
    FOREIGN KEY (next) REFERENCES sample_data(token),
    FOREIGN KEY (prev) REFERENCES sample_data(token)
);

CREATE TABLE sample_annotation (
    token VARCHAR(255) PRIMARY KEY,
    sample_token VARCHAR(255),
    instance_token VARCHAR(255),
    visibility_token VARCHAR(255),
    translation JSONB,
    size JSONB,
    rotation JSONB,
    num_lidar_pts INT,
    num_radar_pts INT,
    next VARCHAR(255),
    prev VARCHAR(255),
    FOREIGN KEY (sample_token) REFERENCES sample(token),
    FOREIGN KEY (instance_token) REFERENCES instance(token),
    FOREIGN KEY (visibility_token) REFERENCES visibility(token),
    FOREIGN KEY (next) REFERENCES sample_annotation(token),
    FOREIGN KEY (prev) REFERENCES sample_annotation(token)
);

CREATE TABLE lidarseg (
    token VARCHAR(255) PRIMARY KEY,
    filename VARCHAR(255),
    sample_data_token VARCHAR(255),
    FOREIGN KEY (sample_data_token) REFERENCES sample_data(token)
);

CREATE TABLE map (
    token VARCHAR(255) PRIMARY KEY,
    log_tokens TEXT[],
    category VARCHAR(255),
    filename VARCHAR(255)
);

