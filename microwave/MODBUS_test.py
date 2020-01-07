from pyModbusTCP.client import ModbusClient
try:
    c = ModbusClient(host="169.254.150.42", port=502, auto_open=True, auto_close=True)
except ValueError:
    print("Error with host or port params")

# for ii in range(0,65535):
# 	returnlist = []
# 	for jj in range(0,2000):
# 		regs_list_1 = c.read_holding_registers(ii, jj)
# 		returnlist.append(regs_list_1)
# 	if not None in returnlist:
# 		print(ii, returnlist)



# for ii in range(104,118):
# 	returnlist = []
# 	for jj in range(0,10):
# 		regs_list_1 = c.read_holding_registers(ii, jj)
# 		returnlist.append(regs_list_1)
# 	print(ii, returnlist)


regs_list_1 = c.read_holding_registers(104, 20)
print(regs_list_1)