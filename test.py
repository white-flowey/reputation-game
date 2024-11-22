from simulate.information_theory import Ift, Info

trust = 0.08
Itruth = Info(0, 0)
Ilie = Info(0, 1)
Istart = Info(0, 0)

print(str(Ift.match(trust, Itruth, Ilie, Istart).round(2)))