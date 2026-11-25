#!/usr/bin/env python3
"""โปรแกรมคำนวณภาษีเงินได้บุคคลธรรมดา (ไทย) - อัตราก้าวหน้า"""
import argparse

# (เพดานของขั้น, อัตราภาษี) - ขั้นสุดท้ายไม่มีเพดาน
BRACKETS = [
    (150_000, 0.00),
    (300_000, 0.05),
    (500_000, 0.10),
    (750_000, 0.15),
    (1_000_000, 0.20),
    (2_000_000, 0.25),
    (5_000_000, 0.30),
    (float("inf"), 0.35),
]

EXPENSE_RATE = 0.50          # หักค่าใช้จ่าย 50% (เงินเดือน/ค่าจ้าง ม.40(1))
EXPENSE_CAP = 100_000        # ไม่เกิน 100,000 บาท
PERSONAL_ALLOWANCE = 60_000  # ลดหย่อนส่วนตัว
SPOUSE_ALLOWANCE = 60_000    # คู่สมรสไม่มีรายได้
CHILD_ALLOWANCE = 30_000     # บุตรคนละ
PARENT_ALLOWANCE = 30_000    # บิดา/มารดา คนละ (สูงสุด 4 คน)
SOCIAL_SECURITY_CAP = 9_000  # ประกันสังคม
LIFE_INSURANCE_CAP = 100_000 # เบี้ยประกันชีวิต


def calc_tax(net_income: float) -> float:
    """คำนวณภาษีจากเงินได้สุทธิ แบบอัตราก้าวหน้า"""
    tax, lower = 0.0, 0.0
    for upper, rate in BRACKETS:
        if net_income <= lower:
            break
        tax += (min(net_income, upper) - lower) * rate
        lower = upper
    return round(tax, 2)


def calc_net_income(annual_income, spouse=False, children=0, parents=0,
                    social_security=0, life_insurance=0, other_deductions=0):
    """คืนค่า (เงินได้สุทธิ, ยอดหักค่าใช้จ่าย, ยอดลดหย่อนรวม)"""
    expense = min(annual_income * EXPENSE_RATE, EXPENSE_CAP)
    allowances = (
        PERSONAL_ALLOWANCE
        + (SPOUSE_ALLOWANCE if spouse else 0)
        + children * CHILD_ALLOWANCE
        + min(parents, 4) * PARENT_ALLOWANCE
        + min(social_security, SOCIAL_SECURITY_CAP)
        + min(life_insurance, LIFE_INSURANCE_CAP)
        + other_deductions
    )
    net = max(annual_income - expense - allowances, 0)
    return net, expense, allowances


def main():
    p = argparse.ArgumentParser(description="คำนวณภาษีเงินได้บุคคลธรรมดา (ไทย)")
    p.add_argument("income", type=float, help="เงินได้ทั้งปี (บาท)")
    p.add_argument("--spouse", action="store_true", help="คู่สมรสไม่มีรายได้")
    p.add_argument("--children", type=int, default=0, help="จำนวนบุตร")
    p.add_argument("--parents", type=int, default=0, help="จำนวนบิดา/มารดาที่อุปการะ")
    p.add_argument("--social-security", type=float, default=0, help="ประกันสังคมที่จ่าย")
    p.add_argument("--life-insurance", type=float, default=0, help="เบี้ยประกันชีวิต")
    p.add_argument("--other", type=float, default=0, help="ลดหย่อนอื่นๆ (กองทุน RMF/SSF ฯลฯ)")
    a = p.parse_args()

    net, expense, allowances = calc_net_income(
        a.income, a.spouse, a.children, a.parents,
        a.social_security, a.life_insurance, a.other)
    tax = calc_tax(net)

    print(f"เงินได้ทั้งปี        : {a.income:>14,.2f} บาท")
    print(f"หักค่าใช้จ่าย        : {expense:>14,.2f} บาท")
    print(f"หักค่าลดหย่อนรวม     : {allowances:>14,.2f} บาท")
    print(f"เงินได้สุทธิ         : {net:>14,.2f} บาท")
    print(f"ภาษีที่ต้องจ่าย      : {tax:>14,.2f} บาท")
    if a.income:
        print(f"อัตราภาษีที่แท้จริง  : {tax / a.income * 100:>13.2f} %")


if __name__ == "__main__":
    main()
