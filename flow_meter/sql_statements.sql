# Create the table flow_meter_control
CREATE TABLE flow_meter_control (
	setpoint_voltage FLOAT NOT NULL
	);

# Initialize the setpoint_voltage
INSERT INTO flow_meter_control
VALUES (1.2);

# Primary key
ALTER TABLE flow_meter_control
ADD COLUMN id SERIAL PRIMARY KEY;

# Set the setpoint_voltage
UPDATE flow_meter_control
SET setpoint_voltage = 1
WHERE id = 1;


# Create the table flow_meter_readout_live
CREATE TABLE flow_meter_readout_live (
	time TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
	read_voltage FLOAT NOT NULL
	);


# Primary key
ALTER TABLE flow_meter_readout_live
ADD COLUMN id SERIAL PRIMARY KEY;

# Create the table flow_meter_readout_storage
CREATE TABLE flow_meter_readout_storage (
	time TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
	read_voltage FLOAT NOT NULL
	);

# Primary key
ALTER TABLE flow_meter_readout_storage
ADD COLUMN id SERIAL PRIMARY KEY;