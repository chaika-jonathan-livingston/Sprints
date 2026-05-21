import random

class Echidna:
    MAX_LIVE_LATENCY = 52
    MIN_WEIGHT = 2
    MAX_WEIGHT = 7.5
    AVG_WEIGHT = (MIN_WEIGHT + MAX_WEIGHT) / 2
    AVG_LIVE_LATENCY = 15
    AVG_TEMPERATURE = 28

    TONGUE_LENGTH = 25
    TONGUE_PER_MINUTE = 50
    STANDARD_ERROR = 10  # оставлю для совместимости, но использовать не буду

    WALK_MAX_MIN = (2, 3)
    RUN_MAX_MIN = (10, 15)
    AVG_SWEEM_SPEED = 5
    SPRINT_SPEED = 24  # км/ч (ИСПРАВЛЕН БАГ №5)

    # Константы для спринта 2
    FIRE_BURROW_TIME_MAX = 10
    HEART_RATE_NORMAL = 60
    HEART_RATE_BURROWING = 12
    METABOLISM_RATIO_BURROWING = 0.2
    GRINDING_TIME_PER_50G = 5
    MAX_EAT_PER_10MIN = 200
    REF_WEIGHT_FOR_EATING = 3.0

    def __init__(self, name=None, season='summer', temp=AVG_TEMPERATURE, live_in_captivity=False, weight=AVG_WEIGHT, age=0):  # ИСПРАВЛЕН БАГ №7: age=0
        # ИСПРАВЛЕН БАГ №2: валидация веса
        if not (self.MIN_WEIGHT <= weight <= self.MAX_WEIGHT):
            raise ValueError(f"Weight must be between {self.MIN_WEIGHT} and {self.MAX_WEIGHT}")
        
        self.live_in_captivity = live_in_captivity
        self.weight = weight
        self.age = age
        self.name = name
        self.temp = temp
        self.after_sprint = False
        self.metabolism_ratio = 1
        self.season = season  # ИСПРАВЛЕН БАГ №1: добавлено self.season
        
        # Новые атрибуты спринта 2
        self.state = 'active'
        self.heart_rate = self.HEART_RATE_NORMAL
        self.burrowing = False
        self.burrow_time_left = 0
        self.grinding_time_left = 0
        
        # ИСПРАВЛЕН БАГ №4: добавлена энергия
        self.energy = 100
        
        # Счётчик выстрелов языка
        self.total_tongue_shots = 0
        
        self.update_state(temp)
        self.bmr = self.BMR()
        
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
        
        # ИСПРАВЛЕН БАГ №6: стрельба языка без случайности
        minutes = actual_grams / 20
        shots = self.shoot_tongue(minutes)
        actual_grams = min(actual_grams, shots * 0.4)
        
        # Восстановление энергии (БАГ №4)
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
        '''Вычисление количества ударов языком за время еды'''
        # ИСПРАВЛЕН БАГ №4: проверка энергии
        if self.energy <= 0:
            raise ValueError(f'Echidna {self.name} has no energy to shoot tongue')
        
        # ИСПРАВЛЕН БАГ №6: строго 50 раз в минуту, без случайности
        shots = int(minutes * self.TONGUE_PER_MINUTE)
        self.total_tongue_shots += shots
        
        # Тратим энергию
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
        '''Обновляет состояние ехидны в зависимости от температуры'''
        self.temp = new_temp
        
        # ИСПРАВЛЕН БАГ №3: точные названия состояний, без случайности
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
        '''
        Покормить ехидну.
        :param food_type: 'ant' или 'worm'
        :param grams: количество граммов пищи (должно быть >0)
        :return: количество съеденного (граммов)
        '''
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
        
        # ИСПРАВЛЕН БАГ №5: SPRINT_SPEED теперь 24 км/ч
        distance_km = (time / 3600) * self.SPRINT_SPEED
        return distance_km
    
    def get_rest(self):
        self.metabolism_ratio = 1
        self.bmr = self.BMR()
        self.after_sprint = False
    
    def survive_fire(self, fire_duration_minutes=5, is_real_fire=True):
        '''
        Адаптация к пожарам: ехидна закапывается и впадает в оцепенение
        :param fire_duration_minutes: продолжительность пожара
        :return: выжила ли ехидна
        '''
        if not is_real_fire:
            print(f'Echidna {self.name}: no fire, no burrowing needed')
            return True
        
        if fire_duration_minutes > self.FIRE_BURROW_TIME_MAX:
            print(f'Echidna {self.name} burned in fire (needed {fire_duration_minutes} min, max {self.FIRE_BURROW_TIME_MAX} min)')
            self.state = 'dead'
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
        '''Выход из бурения (после пожара)'''
        self.burrowing = False
        self.burrow_time_left = 0
        self.heart_rate = self.HEART_RATE_NORMAL
        self.metabolism_ratio = 1
        self.update_state(self.temp)
        self.bmr = self.BMR()
        print(f'Echidna {self.name} came out of burrow, heart rate back to {self.heart_rate} bpm')
    
    def simulate_minute(self, minutes=1):
        '''Симуляция времени'''
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
        
        # Восстановление энергии со временем
        self.energy = min(100, self.energy + minutes * 0.5)