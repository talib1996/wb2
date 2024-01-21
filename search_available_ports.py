import serial.tools.list_ports


def find_serial_ports():
    ports = serial.tools.list_ports.comports()
    port_list = [port.device for port in ports]
    return port_list


# Example usage:
serial_ports = find_serial_ports()
print("Available Serial Ports:", serial_ports[0])
