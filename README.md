# Fast Neutron Generator Monitoring and Control system

## Database information

Runs on twofast-RPi3-0, user pi (with root access), password is the usual.

### How the database was set up

- Name: NG_twofast_DB

- Remote access
  - in `/etc/mysql/mariadb.conf.d` the file `sudo nano 50-server.cnf` contains the bind-address
  - Database is stored under `//fs03/LTH_Neutimag/hkromer/08_Data/mariaDB.mysql/mysql` To see the filesize in MB: `ls -l --block-size=M`

- If you want to make a dump of the database: `mysqldump -u root -p NG_twofast_DB > NAMEOFTHEDUMP.sql`


### What to do when the RaspberryPi running the database was restarted:

- execute `sudo mount -a`
- execute `sudo systemctl start mysql`

### Cleanup of the live database into permanent storage tables
The "live" tables HBox and BBox will "pile up". Hence every night at 3 am the live tables are stored into the store table readings: combineDatabases_V0.py
At 4 am a mysql script will clear all those entries that have NULL everywhere and dose smaller than a threshold (10 µSv/h): cleanup_readings.py

## Start the readout of the Neutron Generator parameters

- Readout of HBox is started via SSH paramiko: H:\hkromer\01_Software\19_Python\DATABASE\Start_HBox_readout.py
- Readout of BBox is started via SSH paramiko: H:\hkromer\01_Software\19_Python\DATABASE\Start_BBox_readout.py
- started by clicking on the shortcut on the control room computer

## Application to display High voltage power supply and neutron dose information

- location: `//fs03/LTH_Neutimag/hkromer/17_github/NG_control_app/`
- code in this repo:  `./NG_control_app/index.py`

## How-to use

- Start python script /NG_control_app/index.py, i.e. on the MPC2278-Computer
- Ensure that the port 5000 is open on that machine, i.e. the MC2278
- Access the readout of the MySQL database in the web browser via: COMPUTERNAME:5000, where COMPUTERNAME is the machine where the script was executed
- Two different layouts:
  - Live: Reads the whole live database and plots high voltage, current, dose and neutron output
  - Historical: Chose a date from which you wish to display the high voltage, current, dose at that particular day. Every morning at 4 AM the live database is backed up into the historical one



# BROOKS Flow Meter

## Pin connection

| Number  | PIN-D cable color  | Description  | Cable color in box | Arduino PIN |
|:-:|:-:|:-:|:-:|:-:|
| 1  | Green | Setpoint common  | Brown | GND |
| 2  | Gray  | Flow Signal 0-5 V  | Green | A0 |
| 5  | Red  | Power Supply +13.5 to +27 VDC  | - | - |
| 8  | Red-Blue  | Setpoint Signal 0 - 5 V  | Yellow | Pin 9 |
| 9  | Black  | Power Supply common | - | - |
| 10  | Brown  | Flow Signal output common  | Brown | GND |
| -  | Aluminum mesh  | Cable shield  | Black | - |

- Check the description of the readout and control structure via flow_meter/2019-06-27.Layout.BROOKSControl and 2019-06-27.Layout.BROOKSReadout


# Microwave Ion Source Control Motor

## Description

- Motor is FITEC FS5106 R, datasheet can be found for example here: https://www.pololu.com/product/3430
- It has three wires, red is 5V, brown is GND, orange is control
- Arduino Uno sketch is found here: dash_NG/microwave_motor/microwave_motor/microwave_motor.ino

## Physical connection

- Use external power supply for the Arduino, or directly power the motor with an external power supply

### Pin connection

| Number  | Cable color  | Description  | Arduino PIN |
|:-:|:-:|:-:|:-:|
| 1  | Brown | Ground  | GND |
| 2  | Red  | 5V power supply  | 5V |
| 3  | Orange  | Control of motor  | 7 |

## Code

### Raspberry Pi3 - twofast-rpi3-5

- Reads the database every 3 seconds
	- Looks up the table microwaveControlMotor, where it reads which command must be executed next, this is only one line, i.e. one command
	- A command can be: move forward (1), move backward (2), start MW (3), stop MW (4)
		- move forward (1): the motor moves a bit clockwise (for 1 second)
		- move backward (2): the motor moves a bit counter clockwise (for 1 second)
		- start MW (3): the motor moves so that the start microwave button is pressed, this takes AMOUNTOFSECONDS
		- stop MW (4): the motor moves so that the stop microwave button is pressed, this takes AMOUNTOFSECONDS
	- Sends the corresponding command to the arduino. It sends via serial connection speed (1 to 92 for forward, 94 to 180 for backward) and the time (which Arduino will put into a delay)
	- After the command was sent, it updates the command in the command table database to have been executed with the correct timestamp

### Arduino - microwave_motor.ino

- reads serial from the RPi3
- receives an integer for the speed and the time for an delay at which to run the motor at at that speed
- otherwise it sends 93 to the motor (stop it)
