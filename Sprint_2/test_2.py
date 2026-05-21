import pytest
from animal import Echidna

@pytest.fixture
def default_echidna():
    return Echidna(name="Test")

"""Тесты для survive_fire() — адаптация к пожарам"""

def test_survive_fire_sets_burrowing_state(default_echidna):
    default_echidna.survive_fire()
    assert default_echidna.state == "burrowing"

def test_heart_rate_drops_during_burrowing(default_echidna):
    default_echidna.survive_fire()
    assert default_echidna.heart_rate <= 12

def test_metabolism_ratio_drops_during_burrowing(default_echidna):
    default_echidna.survive_fire()
    assert default_echidna.metabolism_ratio == default_echidna.METABOLISM_RATIO_BURROWING

def test_burrowing_continues_for_10_minutes(default_echidna):
    default_echidna.survive_fire(fire_duration_minutes=10, is_real_fire=True)
    for _ in range(9):
        default_echidna.simulate_minute(minutes=1)
        assert default_echidna.burrowing is True
    assert default_echidna.burrowing is True

def test_exits_burrowing_after_10_minutes(default_echidna):
    original_heart_rate = default_echidna.heart_rate
    original_metabolism = default_echidna.metabolism_ratio
    default_echidna.survive_fire()
    default_echidna.simulate_minute(minutes=10)
    assert default_echidna.state != "burrowing"
    assert default_echidna.heart_rate == original_heart_rate
    assert default_echidna.metabolism_ratio == original_metabolism

def test_survive_fire_without_fire_does_nothing(default_echidna):
    original_state = default_echidna.state
    default_echidna.survive_fire(is_real_fire=False)
    assert default_echidna.state == original_state

def test_burrowing_state_at_9_minutes_59_seconds(default_echidna):
    default_echidna.survive_fire(fire_duration_minutes=10, is_real_fire=True)
    default_echidna.simulate_minute(minutes = 59 / 60)
    assert default_echidna.state == "burrowing"

def test_burrowing_exits_exactly_at_10_minutes(default_echidna):
    default_echidna.survive_fire()
    default_echidna.simulate_minute(minutes=10)
    assert default_echidna.state != "burrowing"

def test_burrowing_exits_before_10_minutes_1_second(default_echidna):
    default_echidna.survive_fire(fire_duration_minutes=10, is_real_fire=True)
    default_echidna.simulate_minute(minutes=10)
    default_echidna.simulate_minute(minutes=1 / 60)
    assert default_echidna.state != "burrowing"

"""Тесты для eat() / shoot_tongue() — замедление при переедании"""

def test_slowdown_triggered_at_51g(default_echidna):
    default_echidna.eat(food_type="ant", grams=51)
    assert default_echidna.grinding_time_left > 0

def test_slowdown_triggered_at_200g(default_echidna):
    default_echidna.eat(food_type="ant", grams=200)
    assert default_echidna.grinding_time_left > 0

def test_slowdown_ends_and_returns_to_normal(default_echidna):
    default_echidna.eat(food_type="ant", grams=200)
    assert default_echidna.grinding_time_left > 0
    default_echidna.simulate_minute(minutes=21)
    assert default_echidna.grinding_time_left == 0

def test_no_slowdown_at_0g(default_echidna):
    with pytest.raises(ValueError, match="положительным"):
        default_echidna.eat(food_type="ant", grams=0)

def test_no_slowdown_at_negative_amount(default_echidna):
    with pytest.raises(ValueError, match="положительным"):
        default_echidna.eat(food_type="ant", grams=-10)

def test_no_slowdown_at_exactly_50g(default_echidna):
    default_echidna.eat(food_type="worm", grams=50)
    assert default_echidna.grinding_time_left == 0

def test_no_slowdown_at_49_9g(default_echidna):
    default_echidna.eat(food_type="worm", grams=49.9)
    assert default_echidna.grinding_time_left == 0

def test_no_slowdown_at_50_0g(default_echidna):
    default_echidna.eat(food_type="worm", grams=50.0)
    assert default_echidna.grinding_time_left == 0

def test_slowdown_at_50_1g(default_echidna):
    default_echidna.eat(food_type="worm", grams=50.1)
    assert default_echidna.grinding_time_left > 0