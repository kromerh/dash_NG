from pyModbusTCP.client import ModbusClient

# MAC Address of the microwave generator
# MAC Address: 00:80:A3:C2:AB:65 (Lantronix)

# sudo
try:
    # c = ModbusClient(host="169.254.150.42", port=502, auto_open=True, auto_close=True)
    c = ModbusClient(host="169.254.240.201", port=502, auto_open=True, auto_close=True)
    # c = ModbusClient(host="169.254.240.1", port=502, auto_open=True, auto_close=True)
except ValueError:
    print("Error with host or port params")

# for ii in range(0,65535):
# 	returnlist = []
# 	for jj in range(0,2000):
# 		regs_list_1 = c.read_holding_registers(ii, jj)
# 		returnlist.append(regs_list_1)
# 	if not None in returnlist:
# 		print(ii, returnlist)



# for ii in range(100,120):
# 	returnlist = []
# 	for jj in range(0,20):
# 		regs_list_1 = c.read_holding_registers(ii, jj)
# 		returnlist.append(regs_list_1)
# 	print(ii, returnlist)

print('Reading registers')
for ii in range(104,110):
	regs_list_1 = c.read_holding_registers(ii, 1)
	print(ii, regs_list_1)

print('\n Writing coil')
bit_addr = 2
bit_value = 128 # 0 0 0 0 0 0 0 1
wr = c.write_single_register(bit_addr, bit_value)
print(wr)

print('\n Reading registers')
for ii in range(104,110):
	regs_list_1 = c.read_holding_registers(ii, 1)
	print(ii, regs_list_1)

while True:
	rr = c.read_holding_registers(99, 1)
	print(rr)

# addr = 104
# regs_list_1 = c.read_holding_registers(addr, 20)
# print(addr)
# print(regs_list_1)

# addr = 108
# regs_list_1 = c.read_holding_registers(addr, 20)
# print(addr)
# print(regs_list_1)


# addr = 102
# regs_list_1 = c.read_holding_registers(addr, 20)
# print(addr)
# print(regs_list_1)

