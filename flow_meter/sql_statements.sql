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




# Reset a table
DELETE FROM flow_meter_readout_live;

# Reset a table
ALTER TABLE flow_meter_readout_live AUTO_INCREMENT = 0 # set to 0 for completely fresh table


# ***************************************************************
# ***************************************************************
# MICROWAVE GENERATOR CONTROL and READOUT
# ***************************************************************
# ***************************************************************

# Create the table microwave_generator_control
CREATE TABLE microwave_generator_control (
	time TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
	DLL_on boolean NOT NULL
	);

# Primary key
ALTER TABLE microwave_generator_control
ADD COLUMN id SERIAL PRIMARY KEY;


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
	power float NOT NULL
	);

# Primary key
ALTER TABLE microwave_generator_power
ADD COLUMN id SERIAL PRIMARY KEY;



# Create the table microwave_generator_reflected_power
CREATE TABLE microwave_generator_reflected_power (
	time TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
	power_out float NOT NULL,
	power_reflected float NOT NULL
	);

# Primary key
ALTER TABLE microwave_generator_reflected_power
ADD COLUMN id SERIAL PRIMARY KEY;




# Create the table microwave_generator_frequency
CREATE TABLE microwave_generator_frequency (
	time TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
	frequency float NOT NULL
	);

# Primary key
ALTER TABLE microwave_generator_frequency
ADD COLUMN id SERIAL PRIMARY KEY;



# Create the table microwave_generator_DLL
CREATE TABLE microwave_generator_DLL (
	time TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
	DLL_frequency float NOT NULL,
	DLL_reflexion float NOT NULL
	);

# Primary key
ALTER TABLE microwave_generator_DLL
ADD COLUMN id SERIAL PRIMARY KEY;



# Create the table microwave_generator_temperature
CREATE TABLE microwave_generator_temperature (
	time TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
	temperature1 float NOT NULL,
	temperature2 float NOT NULL
	);

# Primary key
ALTER TABLE microwave_generator_temperature
ADD COLUMN id SERIAL PRIMARY KEY;



# Create the table microwave_generator_state
CREATE TABLE microwave_generator_state (
	time TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
	relais_5 boolean NOT NULL,
	relais_24 boolean NOT NULL,
	rf_status boolean NOT NULL
	);

# Primary key
ALTER TABLE microwave_generator_state
ADD COLUMN id SERIAL PRIMARY KEY;


INSERT INTO microwave_generator_control (time_created, command, executed) VALUES ('2019-06-')