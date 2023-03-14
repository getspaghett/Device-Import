import yaml

class DeviceType:
    def __init__(self, manufacturer: str = "TODO", model: str = "TODO", slug: str = "TODO", airflow: str = "front-to-rear", weight: float = 0, weight_unit: str = "kg", u_height: int = 0, subdevice_role: str = "child", device_bays: list = [], interfaces: list = [], inventory_items: list = []):
        self.manufacturer = manufacturer
        self.model = model
        self.slug = slug
        self.airflow = airflow
        self.weight = weight
        self.weight_unit = weight_unit
        self.u_height = u_height
        self.subdevice_role = subdevice_role
        self.device_bays = device_bays
        self.interfaces = interfaces
        self.inventory_items = inventory_items

    def getYAML(self):
        return {
            "manufacturer": self.manufacturer,
            "model": self.model,
            "slug": self.slug,
            "airflow": self.airflow,
            "weight": self.weight,
            "weight_unit": self.weight_unit,
            "u_height": self.u_height,
            "subdevice_role": self.subdevice_role,
            "device_bays": self.device_bays,
            "interfaces": self.interfaces,
            "inventory_items": self.inventory_items
        }