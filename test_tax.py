from tax import calc_tax, calc_net_income


def test_exempt():
    assert calc_tax(150_000) == 0


def test_second_bracket():
    assert calc_tax(300_000) == 7_500


def test_mid_bracket():
    assert calc_tax(600_000) == 7_500 + 20_000 + 15_000


def test_top_brackets():
    assert calc_tax(5_000_000) == 1_265_000
    assert calc_tax(6_000_000) == 1_265_000 + 350_000


def test_zero_and_negative():
    assert calc_tax(0) == 0
    assert calc_tax(-100) == 0


def test_expense_cap():
    _, expense, _ = calc_net_income(1_000_000)
    assert expense == 100_000


def test_salary_600k():
    net, _, _ = calc_net_income(600_000)
    assert net == 440_000
    assert calc_tax(net) == 7_500 + 14_000
