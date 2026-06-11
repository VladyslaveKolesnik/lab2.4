from datetime import datetime
from enum import Enum
import time

#  КЛАС ENUM 
class Room(Enum):
    KITCHEN = "Кухня"
    BEDROOM = "Спальня"
    GARAGE = "Гараж"


#  БАЗОВИЙ КЛАС ПРИСТРОЮ 
class Device:

    def __init__(self, name: str, room: Room, power_consumption: float):
        self.name = name
        self.room = room
        self.power_consumption = (
            power_consumption  # Споживана потужність у Ватах
        )
        self.is_on = False

    def turn_on(self):
        """Поліморфний метод увімкнення."""
        self.is_on = True
        print(f"[{self.name}] увімкнено.")

    def turn_off(self):
        self.is_on = False
        print(f"[{self.name}] вимкнено.")

    def __add__(self, other):
        """Реалізація __add__ для бізнес-логіки: додавання потужностей."""
        if isinstance(other, Device):
            return self.power_consumption + other.power_consumption
        return NotImplemented

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name}, {self.room.value}, {self.power_consumption}W, On={self.is_on})"

#  НАЩАДКИ
class SmartLight(Device):

    def __init__(self, name: str, room: Room, power_consumption: float):
        super().__init__(name, room, power_consumption)
        self.brightness = 100  # Яскравість у %

    def turn_on(self):
        """Перевизначений метод з додатковою логікою."""
        self.is_on = True
        print(
            f"[Розумне світло: {self.name}] увімкнено на {self.brightness}% яскравості."
        )

class SmartThermostat(Device):

    def __init__(self, name: str, room: Room, power_consumption: float):
        super().__init__(name, room, power_consumption)
        self.temperature = 22.0 
         # звичайна температура

    def turn_on(self):
        """Перевизначений метод з додатковою логікою."""
        self.is_on = True
        print(
            f"[Розумний термостат: {self.name}] почав підтримку температури {self.temperature}°C."
        )

# КЛАС-КОНТЕКСТНИЙ МЕНЕДЖЕР (НІЧНИЙ РЕЖИМ)
class NightModeManager:

    def __init__(self, hub, timeout_seconds: float = 2.0):
        self.hub = hub
        self.timeout_seconds = timeout_seconds  # Час "тайм-ауту" для імітації
        self.previous_states = {}  # Збереження попереднього стану пристроїв
        self.start_time = None
        self.status = "Active"

    def __enter__(self):
        print("\n=== [ВХІД] Активація 'Нічного режиму' ===")
        self.start_time = datetime.now()

        # Зберігаємо стан та застосовуємо нічні налаштування
        for device in self.hub.devices:
            self.previous_states[device] = {
                "is_on": device.is_on,
                "brightness": (
                    device.brightness if isinstance(device, SmartLight) else None
                ),
                "temperature": (
                    device.temperature
                    if isinstance(device, SmartThermostat)
                    else None
                ),
            }

            # Логіка нічного режиму: світло вимикаємо, термостат зменшуємо
            if isinstance(device, SmartLight):
                device.turn_off()
            elif isinstance(device, SmartThermostat):
                device.temperature = 18.0
                print(
                    f"[{device.name}] Еко-режим активовано: знижено до 18.0°C."
                )

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("\n=== [ВИХІД] Деактивація 'Нічного режиму' ===")
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        # Сценарій Time-Out
        if duration > self.timeout_seconds:
            self.status = "Expired"
            print(
                f"[УВАГА] Перевищено ліміт часу нічного режиму ({duration:.2f}с > {self.timeout_seconds}с)!"
            )
            print("Статус системи: EXPIRED. Аварійне повернення налаштувань.")
        else:
            print("Нічний режим завершився вчасно.")

        # Повертаємо пристрої до початкового стану
        for device, old_state in self.previous_states.items():
            device.is_on = old_state["is_on"]
            if isinstance(device, SmartLight):
                device.brightness = old_state["brightness"]
            elif isinstance(device, SmartThermostat):
                device.temperature = old_state["temperature"]

        print("Всі пристрої повернуто до початкових налаштувань.")
        return True  # Придушуємо можливі внутрішні помилки

  #КЛАС-МЕНЕДЖЕР 
class HomeHub:

    def __init__(self):
        self.devices = []  # Композиція пристроїв

    def add_device(self, device: Device):
        self.devices.append(device)

    def __iter__(self):
        """Сортована ітерація за назвою кімнати, а потім за потужністю (спадання)."""
        sorted_devices = sorted(
            self.devices, key=lambda d: (d.room.value, -d.power_consumption)
        )
        return iter(sorted_devices)

if __name__ == "__main__":
    # Створення хабу та пристроїв
    hub = HomeHub()

    light_kitchen = SmartLight("Кухонна люстра", Room.KITCHEN, 60.0)
    light_bedroom = SmartLight("Нічник", Room.BEDROOM, 15.0)
    thermostat = SmartThermostat(
        "Головний терморегулятор", Room.BEDROOM, 120.0
    )
    garage_light = SmartLight("Прожектор", Room.GARAGE, 150.0)

    hub.add_device(light_kitchen)
    hub.add_device(light_bedroom)
    hub.add_device(thermostat)
    hub.add_device(garage_light)

    #  Попереднє увімкнення деяких пристроїв
    print("--- Початкове налаштування пристроїв ---")
    light_kitchen.turn_on()
    thermostat.turn_on()

    #  Демонстрація оператора __add__
    print(f"\n--- Перевірка оператора __add__ ---")
    total_power = light_kitchen + thermostat
    print(
        f"Сумарна потужність ({light_kitchen.name} + {thermostat.name}): {total_power} Вт"
    )

    # Демонстрація сортованої ітерації (__iter__)
    print("\n--- Демонстрація сортованої ітерації (за Кімнатою та Потужністю) ---")
    for dev in hub:
        print(f"-> {dev}")

    #  Робота контекстного менеджера зі сценарієм Time-Out
    with NightModeManager(hub, timeout_seconds=1.0) as night:
        print(f"\n[Контекст] Поточний статус менеджера: {night.status}")
        print("[Контекст] Імітуємо тривалу ніч (time.sleep)...")
        time.sleep(1.5)

    # Перевірка, що стан повернувся назад
    print("\n--- Стан пристроїв після виходу з контексту ---")
    print(f"Кухонне світло увімкнене? {light_kitchen.is_on}")
    print(f"Температура термостата повернулась до: {thermostat.temperature}°C")
