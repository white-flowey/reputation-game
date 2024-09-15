import pytest

from simulate.information_theory import Info, Ift


def test_info_arithmetic():
    I1, I2, I3 = Info(7, 6), Info(3, 5), Info(-1, -1)
    assert I1.mu + I2.mu == (I1 + I2).mu and I1.la + I2.la == (I1 + I2).la
    assert I1.mu - I2.mu == (I1 - I2).mu and I1.la - I2.la == (I1 - I2).la
    assert 3 * (I1.mu) == (3 * I1).mu and 3 * (I1.la) == (3 * I1).la
    assert I3.mu > -1 and I3.la > -1


def test_KL():
    assert Ift.KL(Info(2, 3), Info(2, 3)) == 0
    assert round(Ift.KL(Info(3, 5), Info(6, 3)), 2) == 1.38


def test_match():
    Itruth, Ilie, Istart = Info(5, 3), Info(6, 4), Info(3, 3)
    I1 = Ift.match(1, Itruth, Ilie, Istart)
    assert I1.mu == Itruth.mu and I1.la == Itruth.la
    I1 = Ift.match(0, Itruth, Ilie, Istart)
    assert I1.mu == Ilie.mu and I1.la == Ilie.la
    

def test_minimize_KL():
    u, v = 1, 2
    mu, la = Ift.minimize_KL(u, v)
    assert mu + 1 > 0 and la + 1 > 0
    