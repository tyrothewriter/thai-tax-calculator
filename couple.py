#!/usr/bin/env python3
"""เปรียบเทียบภาษีสามี-ภริยา: แยกยื่น / รวมยื่นทั้งหมด / รวมยื่นบางส่วน

อ้างอิงแนวทางตามคำชี้แจงกรมสรรพากร เรื่อง การจัดเก็บภาษีเงินได้บุคคลธรรมดา
จากสามีและภริยา (ฉบับที่ 2) ลงวันที่ 14 มกราคม 2556 (ใช้ตั้งแต่ปีภาษี 2555)
"""
import argparse
from dataclasses import dataclass

from tax import (
    calc_tax, EXPENSE_RATE, EXPENSE_CAP, PERSONAL_ALLOWANCE, SPOUSE_ALLOWANCE,
    CHILD_ALLOWANCE, PARENT_ALLOWANCE, SOCIAL_SECURITY_CAP, LIFE_INSURANCE_CAP,
)


@dataclass
class Person:
    salary: float = 0              # เงินเดือน (ม.40(1))
    other_income: float = 0        # เงินได้ ม.40(2)-(8) *หลังหักค่าใช้จ่ายแล้ว*
    children: int = 0
    parents: int = 0               # บิดามารดาของตนเองที่อุปการะ (สูงสุด 2)
    social_security: float = 0
    life_insurance: float = 0
    other_deductions: float = 0    # RMF/SSF/เงินบริจาค/อื่นๆ ที่คิดแล้ว

    @property
    def has_income(self):
        return self.salary > 0 or self.other_income > 0

    @property
    def salary_expense(self):
        return min(self.salary * EXPENSE_RATE, EXPENSE_CAP)

    @property
    def income_after_expense(self):
        return self.salary - self.salary_expense + self.other_income

    def allowances(self, max_parents=2):
        return (
            PERSONAL_ALLOWANCE
            + self.children * CHILD_ALLOWANCE
            + min(self.parents, max_parents) * PARENT_ALLOWANCE
            + min(self.social_security, SOCIAL_SECURITY_CAP)
            + min(self.life_insurance, LIFE_INSURANCE_CAP)
            + self.other_deductions
        )


def _ret(label, net):
    """หนึ่งแบบ ภ.ง.ด.90/91 -> (ชื่อ, เงินได้สุทธิ, ภาษี)"""
    net = max(net, 0)
    return (label, net, calc_tax(net))


def _total(returns):
    return round(sum(r[2] for r in returns), 2)


def single_income(earner, spouse):
    """คู่สมรสไม่มีรายได้: ผู้มีรายได้หักลดหย่อนคู่สมรสได้ (บิดามารดารวมสองฝ่ายสูงสุด 4)"""
    net = earner.income_after_expense - earner.allowances(max_parents=4) - SPOUSE_ALLOWANCE
    r = _ret("ผู้มีรายได้ (หักลดหย่อนคู่สมรส)", net)
    return [("คู่สมรสไม่มีรายได้", _total([r]), [r])]


def separate(a, b):
    ra = _ret("ฝ่าย A", a.income_after_expense - a.allowances())
    rb = _ret("ฝ่าย B", b.income_after_expense - b.allowances())
    return ("แยกยื่น", _total([ra, rb]), [ra, rb])


def full_joint(a, b):
    net = a.income_after_expense + b.income_after_expense - a.allowances() - b.allowances()
    r = _ret("ยื่นรวมในนามคนเดียว", net)
    return ("รวมยื่นทั้งหมด", _total([r]), [r])


def partial_joint(a, b):
    """เงินเดือนแยกยื่น เงินได้ 40(2)-(8) ของฝ่ายหนึ่งไปรวมกับอีกฝ่าย (เลือกฝ่ายที่ประหยัดกว่า)"""
    options = []
    # รวมเข้า A
    ra = _ret("A (รวมเงินได้ ม.40(2)-(8) ของ B)",
              a.income_after_expense + b.other_income - a.allowances())
    rb = _ret("B (เฉพาะเงินเดือน)", b.salary - b.salary_expense - b.allowances())
    options.append(("รวมยื่นบางส่วน (รวมเข้า A)", _total([ra, rb]), [ra, rb]))
    # รวมเข้า B
    ra2 = _ret("A (เฉพาะเงินเดือน)", a.salary - a.salary_expense - a.allowances())
    rb2 = _ret("B (รวมเงินได้ ม.40(2)-(8) ของ A)",
               b.income_after_expense + a.other_income - b.allowances())
    options.append(("รวมยื่นบางส่วน (รวมเข้า B)", _total([ra2, rb2]), [ra2, rb2]))
    return min(options, key=lambda o: o[1])


def compare(a, b):
    """คืนรายการ (ชื่อแบบ, ภาษีรวม, รายละเอียด) เรียงจากถูกไปแพง"""
    if a.has_income and not b.has_income:
        return single_income(a, b)
    if b.has_income and not a.has_income:
        return single_income(b, a)
    if not a.has_income and not b.has_income:
        return [("ไม่มีรายได้", 0.0, [])]
    results = [separate(a, b), full_joint(a, b), partial_joint(a, b)]
    return sorted(results, key=lambda r: r[1])


FIELDS = [
    ("salary", float, "เงินเดือนทั้งปี"),
    ("other-income", float, "เงินได้ ม.40(2)-(8) หลังหักค่าใช้จ่ายแล้ว"),
    ("children", int, "จำนวนบุตรที่ใช้ลดหย่อน"),
    ("parents", int, "จำนวนบิดามารดาของตนที่อุปการะ"),
    ("social-security", float, "ประกันสังคมที่จ่าย"),
    ("life-insurance", float, "เบี้ยประกันชีวิต"),
    ("other-deductions", float, "ลดหย่อนอื่นๆ รวม"),
]


def main():
    p = argparse.ArgumentParser(description="เปรียบเทียบการยื่นภาษีสามี-ภริยา")
    for side in ("a", "b"):
        for name, typ, help_ in FIELDS:
            p.add_argument(f"--{side}-{name}", type=typ, default=0,
                           help=f"[{side.upper()}] {help_}")
    args = vars(p.parse_args())

    def build(side):
        return Person(**{n.replace("-", "_"): t(args[f"{side}_{n.replace('-', '_')}"])
                         for n, t, _ in FIELDS})

    results = compare(build("a"), build("b"))
    for i, (name, total, rets) in enumerate(results):
        mark = "  <-- ประหยัดที่สุด" if i == 0 and len(results) > 1 else ""
        print(f"\n{name}: ภาษีรวม {total:,.2f} บาท{mark}")
        for label, net, tax in rets:
            print(f"   - {label}: เงินได้สุทธิ {net:,.2f} -> ภาษี {tax:,.2f}")
    print("\n*ประมาณการเบื้องต้น ควรตรวจสอบกับกรมสรรพากรก่อนยื่นจริง")


if __name__ == "__main__":
    main()
