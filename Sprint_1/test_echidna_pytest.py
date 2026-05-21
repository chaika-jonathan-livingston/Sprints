# test_echidna_pytest.py
import pytest
from animal import Echidna

# ---------- Фикстуры ----------
@pytest.fixture
def default_echidna():
    return Echidna(name="Test")

# ---------- Позитивные тесты ----------
def test_default_creation():
    e = Echidna()
    assert e.weight == 5.0          # баг: реально 4.75
    assert e.age == 0               # баг: реально 15
    assert e.temp == 28.0

def test_weight_2_0():
    e = Echidna(weight=2.0)
    assert e.weight == 2.0

def test_weight_7_5():
    e = Echidna(weight=7.5)
    assert e.weight == 7.5

def test_normal_temp_active(default_echidna):
    default_echidna.update_state(28)
    assert default_echidna.state == "active"

def test_rem_sleep_at_25(default_echidna):
    default_echidna.update_state(25)
    assert default_echidna.state == "rem_sleep"   # получим fast_sleep

def test_torpor_at_10(default_echidna):
    default_echidna.update_state(10)
    assert default_echidna.state == "torpor"      # получим paralysis

def test_hibernation_at_33(default_echidna):
    default_echidna.update_state(33)
    assert default_echidna.state == "hibernation" # получим overheating

def test_bmr_summer_5kg():
    e = Echidna(weight=5.0, season='summer')
    assert e.BMR() == pytest.approx(21 * 5**0.75, 0.1)

def test_bmr_winter_5kg():
    e = Echidna(weight=5.0, season='winter')
    expected = 21 * 5**0.75 * 0.4
    assert e.BMR() == pytest.approx(expected, 0.1)

def test_walk_1h(default_echidna):
    dist = default_echidna.walk(1)
    assert 2 <= dist <= 3

def test_run_30min(default_echidna):
    dist = default_echidna.run(0.5)
    assert 5 <= dist <= 7.5

def test_sprint_30sec(default_echidna):
    dist = default_echidna.sprint(30/3600)
    assert dist == pytest.approx(0.2, 0.01)   # упадёт из-за SPRINT_SPEED

def test_swim_1h(default_echidna):
    assert default_echidna.swim(1) == 5

def test_tongue_frequency(default_echidna):
    # проверяем, что метод не падает и принимает минуты
    default_echidna.shoot_tongue(1)

def test_tongue_length(default_echidna):
    assert default_echidna.TONGUE_LENGTH == 25

# ---------- Негативные тесты ----------
def test_weight_below_min():
    with pytest.raises(ValueError):
        Echidna(weight=1.9)

def test_weight_above_max():
    with pytest.raises(ValueError):
        Echidna(weight=8.0)

def test_sprint_without_rest(default_echidna):
    default_echidna.sprint(30/3600)
    with pytest.raises(ValueError):
        default_echidna.sprint(30/3600)

def test_sprint_too_long(default_echidna):
    with pytest.raises(ValueError):
        default_echidna.sprint(31/3600)

def test_tongue_no_energy(default_echidna):
    # энергия не реализована, исключения не будет -> тест упадёт
    with pytest.raises(Exception):
        default_echidna.shoot_tongue(1)

def test_temp_below_5(default_echidna):
    default_echidna.update_state(4)
    assert default_echidna.state == "too_cold"

def test_temp_above_35(default_echidna):
    default_echidna.update_state(36)
    assert default_echidna.state == "overheat"

# ---------- Граничные тесты (parametrize) ----------
@pytest.mark.parametrize("weight,should_fail", [
    (2.0, False), (2.001, False), (1.999, True), (7.5, False), (7.501, True)
])
def test_weight_boundaries(weight, should_fail):
    if should_fail:
        with pytest.raises(ValueError):
            Echidna(weight=weight)
    else:
        e = Echidna(weight=weight)
        assert e.weight == weight

@pytest.mark.parametrize("temp,expected_state", [
    (25.0, "rem_sleep"), (25.1, "active"),
    (15.0, "torpor"), (15.1, "active"),
    (5.0, "torpor"), (4.9, "too_cold"),
    (32.0, "active"), (32.1, "hibernation")
])
def test_temperature_boundaries(temp, expected_state):
    e = Echidna()
    e.update_state(temp)
    assert e.state == expected_state

def test_sprint_boundary():
    e = Echidna()
    e.sprint(30/3600)
    with pytest.raises(ValueError):
        e.sprint(30.1/3600)

def test_walk_speed_bounds(default_echidna):
    for _ in range(20):
        dist = default_echidna.walk(1)
        assert 2.0 <= dist <= 3.0

def test_run_speed_bounds(default_echidna):
    for _ in range(20):
        dist = default_echidna.run(1)
        assert 10.0 <= dist <= 15.0

# Дополнительно: проверка после отдыха
def test_rest_after_sprint(default_echidna):
    default_echidna.sprint(30/3600)
    with pytest.raises(ValueError):
        default_echidna.sprint(30/3600)
    default_echidna.get_rest()
    # после отдыха рывок должен быть возможен
    default_echidna.sprint(30/3600)  # не должно быть ошибки