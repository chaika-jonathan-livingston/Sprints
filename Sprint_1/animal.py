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
    STANDARD_ERROR = 10

    WALK_MAX_MIN = (2, 3)
    RUN_MAX_MIN = (10, 15)
    AVG_SWEEM_SPEED = 5
    SPRINT_SPEED = 24 / 1000 * 3600

    def __init__(self, name=None, season='summer', temp=AVG_TEMPERATURE, live_in_captivity=False, weight=AVG_WEIGHT, age=AVG_LIVE_LATENCY):
        self.live_in_captivity = live_in_captivity
        self.weight = weight
        self.age = age
        self.name = name
        self.temp = temp
        self.update_state(temp)
        self.after_sprint = False
        self.metabolism_ratio = 1
        self.season = season
        self.bmr = self.BMR()
        pass


    def eat(self, food_type):
        '''Попробовать покормить ехидну.'''
        if food_type in ['ant', 'worm']:
            print('Echidna', self.name, 'has accepted food')
            self.shoot_tongue(random.randint(1, 3))
            return True
        else:
            raise ValueError('Echidna', self.name, 'doesn`t eat this kind of food')
    
    def shoot_tongue(self, minutes=1):
        '''Вычисление количества ударов языком за время еды'''
        # Допустим, что количество ударов языком в минуту имеет нормальное распределение
        tongue_per_min = random.normalvariate(self.TONGUE_PER_MINUTE, self.STANDARD_ERROR)
        print(self.name, '`s tongue has shot ', tongue_per_min * minutes, ' times', sep='')
    
    def BMR(self):
        '''
        Вычисляет количество потраченных ехидной каллорий за день.
        Зависит от веса ехидны и времение года.
        '''
        BMR = 21 * (self.weight) ** 0.75 * self.metabolism_ratio
        self.bmr = BMR if self.season == 'summer' else BMR * 0.4
        return self.bmr

    def update_state(self, new_temp):
        '''Обновляет состояние ехидны в зависимости от изменения температуры.'''
        self.temp = new_temp
        
        if new_temp > 32:
            self.state = 'overheating'
        elif 25 <= new_temp <= 32 and random.random() < 0.5:  # 50% шанс
            self.state = 'fast_sleep'
        elif 5 <= new_temp < 15:
            self.state = 'paralysis'
        elif new_temp < 5:
            self.state = 'critical'
        else: 
            self.state = 'active'
        return self.state
    
    def get_state(self):
        return f'{self.name}: {self.state} (температура {self.temp}°C), {self.weight} кг, {self.age} лет'
    
    def walk(self, time):
        '''Спокойное передвижение 2-3 км/ч'''
        return time * random.randint(self.WALK_MAX_MIN[0], self.WALK_MAX_MIN[1])
    
    def run(self, time):
        '''бег 10-15 км/ч'''
        self.metabolism_ratio = random.uniform(2.0, 2.5)
        return time * random.randint(self.RUN_MAX_MIN[0], self.RUN_MAX_MIN[1])
    
    def swim(self, time):
        return time * self.AVG_SWEEM_SPEED
    
    def sprint(self, time):
        '''Попытка сделать рывок'''
        if time > 30:
            raise ValueError('Рывок не должен превышать 30 сек')
        if self.after_sprint:
            raise ValueError('Второй рывок подряд невозможен. Нужен отдых')
        if self.state != 'active':
            raise ValueError('Ехидна не может сделать рывок в текущем состоянии')
        self.metabolism_ratio = 2.5
        self.bmr = self.BMR()
        self.after_sprint = True
        return time * self.SPRINT_SPEED
    
    def get_rest(self):
        '''Восстановить значения, изменённые после рывка или бега'''
        self.metabolism_ratio = 1
        self.bmr = self.BMR()
        self.after_sprint = False
        pass

