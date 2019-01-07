# Fast Neutron Generator Monitoring and Control system

## Database information

### What to do when the RaspberryPi running the database was restarted:

- execute `sudo mount -a`
- execute `sudo systemctl start mysql`

## Main Application

/NG_control_app/index.py

## How-to use

- Start python script /NG_control_app/index.py, i.e. on the MPC2278-Computer
- Ensure that the port 5000 is open on that machine, i.e. the MC2278
- Access the readout of the MySQL database in the web browser via: COMPUTERNAME:5000, where COMPUTERNAME is the machine where the script was executed
- Two different layouts:
  - Live: Reads the whole live database and plots high voltage, current, dose and neutron output
  - Historical: Chose a date from which you wish to display the high voltage, current, dose at that particular day. Every morning at 4 AM the live database is backed up into the historical one