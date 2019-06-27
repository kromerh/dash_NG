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


