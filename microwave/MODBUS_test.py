from pyModbusTCP.client import ModbusClient
try:
    c = ModbusClient(host="localhost", port=502, auto_open=True, auto_close=True)
except ValueError:
    print("Error with host or port params")

for ii in range(104,118):
	returnlist = []
	for jj in range(1,126):
		regs_list_1 = c.read_holding_registers(ii, jj)
		returnlist.append(regs_list_1)
	print(ii, returnlist)