import random

class Echidna:
    """
    Класс Ехидна.
    Спринт 1: базовые атрибуты, еда, БМР, состояния, передвижение (walk, run, swim, sprint).
    Спринт 2: энергия, бурение при пожаре, перетирание пищи, simulate_minute.
    Спринт 3: размножение (беременность, инкубация, рост в сумке, укрытие, кормление).
    """

    # ---------- Константы (общие для всех спринтов) ----------
    MAX_LIVE_LATENCY = 52
    MIN_WEIGHT = 2
    MAX_WEIGHT = 7.5
    AVG_WEIGHT = (MIN_WEIGHT + MAX_WEIGHT) / 2
    AVG_LIVE_LATENCY = 15
    AVG_TEMPERATURE = 28

    TONGUE_LENGTH = 25
    TONGUE_PER_MINUTE = 50
    STANDARD_ERROR = 10

    WALK_MAX_MIN = (2, 3)
    RUN_MAX_MIN = (10, 15)
    AVG_SWEEM_SPEED = 5
    SPRINT_SPEED = 24

    # Константы спринта 2
    FIRE_BURROW_TIME_MAX = 10
    HEART_RATE_NORMAL = 60
    HEART_RATE_BURROWING = 12
    METABOLISM_RATIO_BURROWING = 0.2
    GRINDING_TIME_PER_50G = 5
    MAX_EAT_PER_10MIN = 200
    REF_WEIGHT_FOR_EATING = 3.0

    # Константы спринта 3
    BABY_START_WEIGHT = 0.00045   # кг
    GROWTH_FACTOR = 900

    def __init__(self, name=None, gender=None, season='summer', temp=AVG_TEMPERATURE,
                 live_in_captivity=False, weight=AVG_WEIGHT, age=0):
        """
        Поля спринта 1: weight, age, name, temp, season, metabolism_ratio, bmr, state.
        Поля спринта 2: after_sprint, burrowing, burrow_time_left, grinding_time_left, energy, total_tongue_shots.
        Поля спринта 3: is_pregnant, pregnancy_days, has_egg, egg_incubation_days, baby_in_pouch, pouch_days,
                        baby_in_hiding, days_since_last_feed, independent_age_days, baby_weight.
        """
        # Валидация веса (спринт 1)
        if not (self.MIN_WEIGHT <= weight <= self.MAX_WEIGHT):
            raise ValueError(f"Weight must be between {self.MIN_WEIGHT} and {self.MAX_WEIGHT}")

        # Генерация случайного пола, если не указан (спринт 3)
        if gender is None:
            gender = random.choice(['male', 'female'])
        else:
            gender = gender.lower()
            if gender not in ('male', 'female'):
                raise ValueError("Gender must be 'male' or 'female'")

        # Атрибуты спринта 1
        self.live_in_captivity = live_in_captivity
        self.weight = weight
        self.age = age
        self.name = name if name is not None else f"Echidna_{id(self)}"
        self.gender = gender
        self.temp = temp
        self.after_sprint = False
        self.metabolism_ratio = 1
        self.season = season
        self.state = 'active'

        # Состояние жива/мертва (добавлено в спринте 3)
        self.alive = True

        # Атрибуты спринта 2
        self.heart_rate = self.HEART_RATE_NORMAL
        self.burrowing = False
        self.burrow_time_left = 0
        self.grinding_time_left = 0
        self.energy = 100
        self.total_tongue_shots = 0

        # Атрибуты спринта 3
        self.is_pregnant = False
        self.pregnancy_days = 0
        self.has_egg = False
        self.egg_incubation_days = 0
        self.baby_in_pouch = False
        self.pouch_days = 0
        self.baby_in_hiding = False
        self.days_since_last_feed = 0
        self.independent_age_days = 0
        self.baby_weight = 0.0
        self.PREGNANCY = random.randint(21, 28)
        self.DAYS_IN_POUCH = random.randint(50, 55)

         # Атрибуты спринта 4
        self.electroreceptor_count = 2000
        self.field_strength_mVcm = 1.8

        self.update_state(temp)
        self.bmr = self.BMR()

    # ---------- Методы спринта 1 ----------
    def eat(self, food_type, grams=50):
        if grams <= 0:
            raise ValueError(f'Количество еды должно быть положительным, получено {grams} г')
        if food_type not in ['ant', 'worm']:
            raise ValueError(f'Echidna {self.name} doesn\'t eat this kind of food')
        if self.burrowing:
            raise ValueError(f'Echidna {self.name} is burrowing and cannot eat')
        if self.grinding_time_left > 0:
            raise ValueError(f'Echidna {self.name} is still grinding previous food ({self.grinding_time_left} min left)')

        weight_factor = self.weight / self.REF_WEIGHT_FOR_EATING
        max_grams = self.MAX_EAT_PER_10MIN * weight_factor
        actual_grams = min(grams, max_grams)

        print(f'Echidna {self.name} has accepted {actual_grams}g of {food_type}')

        minutes = actual_grams / 20
        shots = self.shoot_tongue(minutes)
        actual_grams = min(actual_grams, shots * 0.4)

        self.energy = min(100, self.energy + actual_grams / 10)

        if actual_grams > 50:
            grinding_time = (actual_grams / 50) * self.GRINDING_TIME_PER_50G
            self.grinding_time_left = grinding_time
            print(f'Echidna {self.name} needs {grinding_time:.1f} min to grind food')
        else:
            self.grinding_time_left = 0

        self.weight += actual_grams / 1000
        return actual_grams

    def shoot_tongue(self, minutes=1):
        if self.energy <= 0:
            raise ValueError(f'Echidna {self.name} has no energy to shoot tongue')
        shots = int(minutes * self.TONGUE_PER_MINUTE)
        self.total_tongue_shots += shots
        self.energy = max(0, self.energy - shots * 0.1)
        print(f'{self.name}\'s tongue has shot {shots} times')
        return shots

    def BMR(self):
        BMR = 21 * (self.weight) ** 0.75 * self.metabolism_ratio
        if self.season == 'summer':
            self.bmr = BMR
        else:
            self.bmr = BMR * 0.4
        return self.bmr

    def update_state(self, new_temp):
        self.temp = new_temp
        if self.burrowing:
            self.state = 'burrowing'
        elif new_temp > 35:
            self.state = 'overheat'
        elif new_temp > 32:
            self.state = 'hibernation'
        elif new_temp == 25:
            self.state = 'rem_sleep'
        elif 25 < new_temp <= 32:
            self.state = 'active'
        elif 5 <= new_temp < 15:
            self.state = 'torpor'
        elif new_temp < 5:
            self.state = 'too_cold'
        else:
            self.state = 'active'
        return self.state

    def get_state(self):
        if not self.alive:
            return f'{self.name}: мертва'
        status = f'{self.name}: {self.state} (температура {self.temp}°C), {self.weight:.2f} кг, {self.age} лет, энергия {self.energy:.0f}'
        if self.grinding_time_left > 0:
            status += f', перетирает пищу ({self.grinding_time_left:.0f} мин)'
        if self.burrowing:
            status += f', зарылся, сердце {self.heart_rate} уд/мин'
        return status

    def walk(self, time):
        if self.grinding_time_left > 0:
            raise ValueError(f'Echidna {self.name} is grinding food and cannot walk')
        if self.burrowing:
            raise ValueError(f'Echidna {self.name} is burrowing and cannot walk')
        return time * random.randint(self.WALK_MAX_MIN[0], self.WALK_MAX_MIN[1])

    def run(self, time):
        if self.grinding_time_left > 0:
            raise ValueError(f'Echidna {self.name} is grinding food and cannot run')
        if self.burrowing:
            raise ValueError(f'Echidna {self.name} is burrowing and cannot run')
        self.metabolism_ratio = random.uniform(2.0, 2.5)
        return time * random.randint(self.RUN_MAX_MIN[0], self.RUN_MAX_MIN[1])

    def swim(self, time):
        if self.burrowing:
            raise ValueError(f'Echidna {self.name} is burrowing and cannot swim')
        return time * self.AVG_SWEEM_SPEED

    def sprint(self, time):
        if time > 30:
            raise ValueError('Рывок не должен превышать 30 сек')
        if self.after_sprint:
            raise ValueError('Второй рывок подряд невозможен. Нужен отдых')
        if self.state != 'active':
            raise ValueError('Ехидна не может сделать рывок в текущем состоянии')
        if self.grinding_time_left > 0:
            raise ValueError('Ехидна перетирает пищу и не может сделать рывок')
        if self.burrowing:
            raise ValueError('Ехидна зарыта и не может сделать рывок')
        if self.energy < 20:
            raise ValueError('Недостаточно энергии для рывка')

        self.metabolism_ratio = 2.5
        self.bmr = self.BMR()
        self.after_sprint = True
        self.energy -= 20
        distance_km = (time / 3600) * self.SPRINT_SPEED
        return distance_km

    def get_rest(self):
        self.metabolism_ratio = 1
        self.bmr = self.BMR()
        self.after_sprint = False

    # ---------- Методы спринта 2 ----------
    def survive_fire(self, fire_duration_minutes=5, is_real_fire=True):
        if not is_real_fire:
            print(f'Echidna {self.name}: no fire, no burrowing needed')
            return True
        if fire_duration_minutes > self.FIRE_BURROW_TIME_MAX:
            print(f'Echidna {self.name} burned in fire (needed {fire_duration_minutes} min, max {self.FIRE_BURROW_TIME_MAX} min)')
            self.state = 'dead'
            self.alive = False
            return False
        self.burrowing = True
        self.burrow_time_left = fire_duration_minutes
        self.heart_rate = self.HEART_RATE_BURROWING
        self.metabolism_ratio = self.METABOLISM_RATIO_BURROWING
        self.state = 'burrowing'
        self.bmr = self.BMR()
        print(f'Echidna {self.name} burrowed into ground, heart rate {self.heart_rate} bpm')
        return True

    def end_burrowing(self):
        self.burrowing = False
        self.burrow_time_left = 0
        self.heart_rate = self.HEART_RATE_NORMAL
        self.metabolism_ratio = 1
        self.update_state(self.temp)
        self.bmr = self.BMR()
        print(f'Echidna {self.name} came out of burrow, heart rate back to {self.heart_rate} bpm')

    def simulate_minute(self, minutes=1):
        if not self.alive:
            return
        if self.grinding_time_left > 0:
            self.grinding_time_left -= minutes
            if self.grinding_time_left < 0:
                self.grinding_time_left = 0
        if self.burrowing:
            self.burrow_time_left -= minutes
            if self.burrow_time_left <= 0:
                self.end_burrowing()
        if self.after_sprint and minutes >= 5:
            self.get_rest()
        self.energy = min(100, self.energy + minutes * 0.5)

    # ---------- Методы спринта 3 (размножение) ----------
    def start_pregnancy(self):
        """Инициирует беременность (только для самок)."""
        if not self.alive:
            self.is_pregnant = False
            raise ValueError(f"{self.name} мертва и не может забеременеть")
        if self.gender == 'male':
            raise ValueError(f"Самец {self.name} не может забеременеть")
        if self.is_pregnant or self.has_egg or self.baby_in_pouch or self.baby_in_hiding:
            raise ValueError(f"{self.name} уже участвует в размножении")
        self.is_pregnant = True
        self.pregnancy_days = 0
        self.has_egg = False
        self.egg_incubation_days = 0
        self.baby_in_pouch = False
        self.baby_in_hiding = False
        self.baby_weight = 0.0

    def _update_pouch_baby_growth(self):
        """Рост детёныша в сумке (вызывается каждый день)."""
        if not self.baby_in_pouch:
            return
        self.baby_weight = self.BABY_START_WEIGHT * (self.GROWTH_FACTOR ** (self.pouch_days / 60))

    def simulate_day(self):
        """
        Обновляет репродуктивное состояние за один день.
        Возвращает dict с текущим состоянием.
        """
        if not self.alive:
            return self.get_reproduction_status()

        # 1. Беременность -> откладывание яйца
        if self.is_pregnant:
            self.pregnancy_days += 1
            pregnancy_duration = self.PREGNANCY
            if self.pregnancy_days >= pregnancy_duration:
                self.is_pregnant = False
                self.has_egg = True
                self.egg_incubation_days = 0
                self.pregnancy_days = 0

        # 2. Инкубация яйца -> вылупление
        if self.has_egg:
            self.egg_incubation_days += 1
            if self.egg_incubation_days >= 10:
                self.has_egg = False
                self.baby_in_pouch = True
                self.pouch_days = 0
                self.baby_weight = self.BABY_START_WEIGHT

        # 3. Детёныш в сумке
        if self.baby_in_pouch:
            self.pouch_days += 1
            self._update_pouch_baby_growth()
            pouch_stay = self.DAYS_IN_POUCH
            if self.pouch_days >= pouch_stay:
                self.baby_in_pouch = False
                self.baby_in_hiding = True
                self.days_since_last_feed = 0
                self.independent_age_days = 0

        # 4. Детёныш в укрытии
        if self.baby_in_hiding:
            self.days_since_last_feed += 1
            self.independent_age_days += 1
            if self.days_since_last_feed > 15:
                self.baby_in_hiding = False
                self.baby_weight = 0.0
                self.independent_age_days = 0
                print(f"Детёныш {self.name} погиб от голода")
            elif self.days_since_last_feed > 10:
                self.baby_weight *= 0.95
            if self.independent_age_days >= 150:
                self.baby_in_hiding = False
                print(f"Детёныш {self.name} стал самостоятельным")

        return self.get_reproduction_status()

    def mother_feeds(self):
        """Мать кормит детёныша в укрытии."""
        if not self.alive:
            raise ValueError(f"{self.name} мертва и не может кормить")
        if not self.baby_in_hiding:
            raise ValueError(f"У {self.name} нет детёныша в укрытии")
        if self.baby_weight >= 10:
            self.alive = False
            raise ValueError(f"{self.name} не может весить так много, он уже умер")
        self.baby_weight *= 1.2
        self.days_since_last_feed = 0
        print(f"{self.name} покормила детёныша, вес теперь {self.baby_weight*1000:.1f} г")
        return self.baby_weight * 1000

    def get_reproduction_status(self):
        """Возвращает словарь с информацией о размножении."""
        return {
            "is_pregnant": self.is_pregnant,
            "pregnancy_days": self.pregnancy_days,
            "has_egg": self.has_egg,
            "egg_incubation_days": self.egg_incubation_days,
            "baby_in_pouch": self.baby_in_pouch,
            "pouch_days": self.pouch_days,
            "baby_in_hiding": self.baby_in_hiding,
            "days_since_last_feed": self.days_since_last_feed,
            "independent_age_days": self.independent_age_days,
            "baby_weight_kg": self.baby_weight,
            "baby_weight_g": self.baby_weight * 1000,
        }
    
    def detect_prey_by_electric_field(self, depth_cm: float):
        if not self.alive:
            raise ValueError("Ехидна мертва")
        if self.burrowing or self.state in ['torpor', 'hibernation']:
            return {"detected": False, "prey_type": None, "distance_mm": None}
        if depth_cm < 0:
            raise ValueError("Глубина не может быть отрицательной")
        if depth_cm > 15 or self.field_strength_mVcm < 1.8:
            return {"detected": False, "prey_type": None, "distance_mm": None}
        probability = min(1.0, self.electroreceptor_count / 2000)
        if random.random() < probability:
            return {
            "detected": True,
            "prey_type": random.choice(["ants", "termites", "worms"]),
            "distance_mm": depth_cm * 10
            }
        else:
            return {"detected": False, "prey_type": None, "distance_mm": None}
