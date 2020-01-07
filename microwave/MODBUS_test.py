from pyModbusTCP.client import ModbusClient
try:
    c = ModbusClient(host="localhost", port=502, auto_open=True, auto_close=True)
except ValueError:
    print("Error with host or port params")


regs_list_1 = c.read_holding_registers(104, 10)
print(regs_list_1)