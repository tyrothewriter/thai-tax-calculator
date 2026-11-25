from couple import Person, compare, separate, full_joint, partial_joint


def test_two_salaries_separate_beats_full_joint():
    a, b = Person(salary=600_000), Person(salary=300_000)
    assert separate(a, b)[1] == 21_500
    assert full_joint(a, b)[1] == 39_500
    assert partial_joint(a, b)[1] == 21_500   # ไม่มีเงินได้อื่นให้รวม
    assert compare(a, b)[0][1] == 21_500


def test_partial_joint_saves_tax():
    # A มีเงินได้อื่น 200,000 รวมเข้าฝ่าย B ที่รายได้น้อย จะประหยัดกว่า
    a = Person(salary=600_000, other_income=200_000)
    b = Person(salary=100_000)
    assert separate(a, b)[1] == 48_500
    assert partial_joint(a, b)[1] == 23_500
    best = compare(a, b)[0]
    assert best[0].startswith("รวมยื่นบางส่วน")
    assert best[1] == 23_500


def test_single_income_gets_spouse_allowance():
    a = Person(salary=600_000)
    # 600,000 - 100,000 - 60,000 - 60,000 = 380,000 -> 7,500 + 8,000
    assert compare(a, Person())[0][1] == 15_500
    assert compare(Person(), a)[0][1] == 15_500   # สลับฝ่ายได้ผลเท่ากัน


def test_no_income():
    assert compare(Person(), Person())[0][1] == 0
