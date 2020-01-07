from pyModbusTCP.client import ModbusClient
try:
    c = ModbusClient(host="169.254.101.50", port=502, auto_open=True, auto_close=True)
except ValueError:
    print("Error with host or port params")

for ii in range(0,105):
	regs_list_1 = c.read_holding_registers(ii, 8)
	print(regs_list_1)