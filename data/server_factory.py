from wireguard.linux import Linux
from wireguard.mikrotik import MikroTik


def create_server_instance(class_name, server_data):
    if class_name == "Linux":
        return Linux(**server_data)
    elif class_name == "MikroTik":
        return MikroTik(**server_data)
    else:
        raise ValueError(f"Unknown server class: {class_name}")
