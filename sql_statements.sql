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
	read_voltage FLOAT NOT NULL,
	set_voltage FLOAT NOT NULL
	);


# Primary key
ALTER TABLE flow_meter_readout_live
ADD COLUMN id SERIAL PRIMARY KEY;

# Create the table flow_meter_readout_storage
CREATE TABLE flow_meter_readout_storage (
	time TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
	read_voltage FLOAT NOT NULL,
	set_voltage FLOAT NOT NULL
	);

# Primary key
ALTER TABLE flow_meter_readout_storage
ADD COLUMN id SERIAL PRIMARY KEY;




# Reset a table
DELETE FROM flow_meter_readout_live;

# Reset a table
ALTER TABLE flow_meter_readout_live AUTO_INCREMENT = 0 # set to 0 for completely fresh table


# ***************************************************************
# ***************************************************************
# MICROWAVE MOTOR CONTROL
# ***************************************************************
# ***************************************************************



# Create the table microwave_generator_command
CREATE TABLE microwave_motor_command (
	time_created TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
	time_executed TIMESTAMP(6),
	command text NOT NULL,
	executed boolean NOT NULL
	);



# ***************************************************************
# ***************************************************************
# MICROWAVE GENERATOR CONTROL and READOUT
# ***************************************************************
# ***************************************************************



# Create the table microwave_generator_command
CREATE TABLE microwave_generator_command (
	time_created TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
	time_executed TIMESTAMP(6),
	command text NOT NULL,
	executed boolean NOT NULL,
	answer text
	);

# Primary key
ALTER TABLE microwave_generator_command
ADD COLUMN id SERIAL PRIMARY KEY;


# Create the table microwave_generator_power
CREATE TABLE microwave_generator_power (
	time TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
	FP float,
	RP float,
	power_setpoint float
	);

# Primary key
ALTER TABLE microwave_generator_power
ADD COLUMN id SERIAL PRIMARY KEY;





# Create the table microwave_generator_frequency
CREATE TABLE microwave_generator_frequency (
	time TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
	frequency float,
	frequency_setpoint float
	);

# Primary key
ALTER TABLE microwave_generator_frequency
ADD COLUMN id SERIAL PRIMARY KEY;


# Create the table microwave_generator_state
CREATE TABLE microwave_generator_state (
	time TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
	external_safety boolean NOT NULL,
	MW_ready boolean NOT NULL,
	MW_on boolean NOT NULL,
	fault_present boolean NOT NULL
	);

# Primary key
ALTER TABLE microwave_generator_state
ADD COLUMN id SERIAL PRIMARY KEY;


INSERT INTO microwave_generator_control (time_created, command, executed) VALUES ('2019-06-')




CREATE TABLE water_sensor_data (
	time TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
	s1 boolean NOT NULL,
	s2 boolean NOT NULL,
	s3 boolean NOT NULL
	);
# Primary key
ALTER TABLE water_sensor_data
ADD COLUMN id SERIAL PRIMARY KEY;
