import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

st.set_page_config(
    page_title="NPL Rate Prediction - Mongolia Banking",
    layout="wide"
)

st.markdown("""
<style>
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
}
.high-risk {
    background-color: #ffebee;
    border-left: 5px solid #f44336;
}
.medium-risk {
    background-color: #fff3e0;
    border-left: 5px solid #ff9800;
}
.low-risk {
    background-color: #e8f5e8;
    border-left: 5px solid #4caf50;
}
.gauge-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 200px;
}
.gauge {
    width: 200px;
    height: 200px;
    border-radius: 50%;
    background: conic-gradient(
        #4caf50 0deg 36deg,
        #ff9800 36deg 90deg,
        #f44336 90deg 360deg
    );
    display: flex;
    justify-content: center;
    align-items: center;
    position: relative;
}
.gauge-inner {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    background: white;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
}
</style>
""", unsafe_allow_html=True)

st.title(" NPL Rate Prediction System")
st.markdown("**Монголын банкны NPL rate (Чанаргүй зээл болох хувь) тооцоолох систем**")

st.sidebar.header("Харилцагчийн мэдээлэл оруулна уу")

loan_amount = st.sidebar.number_input(
    "Зээлийн хэмжээ (төгрөг)", 
    min_value=100000, 
    max_value=10000000000, 
    value=50000000, 
    step=1000000
)

monthly_income = st.sidebar.number_input(
    "Сарын орлого (төгрөг)", 
    min_value=100000, 
    max_value=100000000, 
    value=2000000, 
    step=100000
)

age = st.sidebar.slider("Нас", 18, 80, 35)

employment_years = st.sidebar.slider("Ажлын туршлага (жил)", 0, 40, 5)

employment_type = st.sidebar.selectbox(
    "Ажлын төрөл",
    ["Төрийн албан хаагч", "Хувийн хэвшил", "ИТТ", "Бизнес эрхлэгч", "Гадаадын компани", "Бусад"]
)

education_level = st.sidebar.selectbox(
    "Боловсролын түвшин",
    ["Дээд", "Тусгай дунд", "Бүрэн дунд", "Бүрэн бус дунд"]
)

marital_status = st.sidebar.selectbox(
    "Гэрлэлтийн байдал",
    ["Гэрлэсэн", "Ганц бие", "Салсан", "Бэлэвсэн"]
)

credit_history_months = st.sidebar.slider("Зээлийн түүх (сар)", 0, 120, 24)

previous_defaults = st.sidebar.number_input("Өмнөх зээлийн саатал (удаа)", 0, 10, 0)

collateral_value = st.sidebar.number_input(
    "Барьцааны үнэ (төгрөг)", 
    min_value=0, 
    max_value=50000000000, 
    value=100000000, 
    step=5000000
)

debt_to_income = st.sidebar.slider("Өр/Орлогын харьцаа (%)", 0.0, 100.0, 30.0)

def calculate_npl_rate(loan_amount, monthly_income, age, employment_years, 
                      employment_type, education_level, marital_status,
                      credit_history_months, previous_defaults, collateral_value, debt_to_income):
    
    base_score = 0.05
    
    income_loan_ratio = (monthly_income * 12) / loan_amount
    if income_loan_ratio < 0.3:
        base_score += 0.15
    elif income_loan_ratio < 0.5:
        base_score += 0.10
    elif income_loan_ratio < 0.8:
        base_score += 0.05
    
    if age < 25 or age > 65:
        base_score += 0.08
    elif age < 30 or age > 55:
        base_score += 0.03
    
    if employment_years < 2:
        base_score += 0.12
    elif employment_years < 5:
        base_score += 0.06
    
    employment_risk = {
        "Төрийн албан хаагч": 0.00,
        "Гадаадын компани": 0.02,
        "ИТТ": 0.03,
        "Хувийн хэвшил": 0.05,
        "Бизнес эрхлэгч": 0.08,
        "Бусад": 0.10
    }
    base_score += employment_risk.get(employment_type, 0.05)
    
    education_risk = {
        "Дээд": 0.00,
        "Тусгай дунд": 0.02,
        "Бүрэн дунд": 0.05,
        "Бүрэн бус дунд": 0.08
    }
    base_score += education_risk.get(education_level, 0.03)
    
    marital_risk = {
        "Гэрлэсэн": 0.00,
        "Ганц бие": 0.03,
        "Салсан": 0.08,
        "Бэлэвсэн": 0.05
    }
    base_score += marital_risk.get(marital_status, 0.02)
    
    if credit_history_months == 0:
        base_score += 0.15
    elif credit_history_months < 12:
        base_score += 0.10
    elif credit_history_months < 24:
        base_score += 0.05
    
    base_score += previous_defaults * 0.08
    
    if collateral_value > 0:
        coverage_ratio = collateral_value / loan_amount
        if coverage_ratio >= 1.5:
            base_score -= 0.08
        elif coverage_ratio >= 1.2:
            base_score -= 0.05
        elif coverage_ratio >= 1.0:
            base_score -= 0.03
        elif coverage_ratio >= 0.8:
            base_score += 0.02
        else:
            base_score += 0.05
    else:
        base_score += 0.10
    
    if debt_to_income > 70:
        base_score += 0.15
    elif debt_to_income > 50:
        base_score += 0.10
    elif debt_to_income > 30:
        base_score += 0.05
    
    npl_rate = max(0.01, min(0.95, base_score))
    
    return npl_rate

npl_rate = calculate_npl_rate(
    loan_amount, monthly_income, age, employment_years,
    employment_type, education_level, marital_status,
    credit_history_months, previous_defaults, collateral_value, debt_to_income
)

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.subheader("NPL Rate Prediction")
    
    if npl_rate <= 0.10:
        risk_level = "Бага эрсдэлтэй"
        risk_class = "low-risk"
        risk_color = "#4caf50"
    elif npl_rate <= 0.25:
        risk_level = "Дунд эрсдэлтэй"
        risk_class = "medium-risk"
        risk_color = "#ff9800"
    else:
        risk_level = "Өндөр эрсдэлтэй"
        risk_class = "high-risk"
        risk_color = "#f44336"
    
    st.subheader(f"NPL Rate: {npl_rate:.2%}")
    st.progress(min(npl_rate, 1.0))
    
    st.markdown(f"""
    <div style="background-color: {risk_color}20; border: 2px solid {risk_color}; 
    border-radius: 10px; padding: 20px; text-align: center; margin: 20px 0;">
        <h2 style="color: {risk_color}; margin: 0;">{risk_level}</h2>
        <h1 style="color: {risk_color}; margin: 10px 0;">{npl_rate:.2%}</h1>
    </div>
    """, unsafe_allow_html=True)
    
    if npl_rate <= 0.05:
        st.success(" Маш бага эрсдэл")
    elif npl_rate <= 0.10:
        st.success(" Хүлээн зөвшөөрөх эрсдэл")
    elif npl_rate <= 0.20:
        st.warning(" Анхаарал хандуулах эрсдэл")
    elif npl_rate <= 0.30:
        st.error(" Өндөр эрсдэл")
    else:
        st.error(" Маш өндөр эрсдэл")

with col2:
    st.subheader("Зээлийн мэдээлэл")
    st.metric("Зээлийн хэмжээ", f"{loan_amount:,.0f} ₮")
    st.metric("Сарын орлого", f"{monthly_income:,.0f} ₮")
    st.metric("Орлого/Зээлийн харьцаа", f"{(monthly_income * 12 / loan_amount):.2%}")
    
    st.subheader("Эрсдэлийн оноо")
    base_factors = {
        "Үндсэн оноо": 5.0,
        "Орлогын хүчин зүйл": max(0, min(15, (0.3 - (monthly_income * 12 / loan_amount)) * 50)) if (monthly_income * 12 / loan_amount) < 0.3 else 0,
        "Нас": 8.0 if age < 25 or age > 65 else (3.0 if age < 30 or age > 55 else 0),
        "Ажлын туршлага": 12.0 if employment_years < 2 else (6.0 if employment_years < 5 else 0)
    }
    
    for factor, score in base_factors.items():
        if score > 0:
            st.metric(factor, f"{score:.1f}%")

with col3:
    st.subheader("Барьцааны мэдээлэл")
    if collateral_value > 0:
        st.metric("Барьцааны үнэ", f"{collateral_value:,.0f} ₮")
        st.success(" Барьцаатай зээл")
    else:
        st.metric("Барьцааны үнэ", "Байхгүй")
        st.error(" Барьцаагүй зээл")
    
    st.metric("Өр/Орлогын харьцаа", f"{debt_to_income:.1f}%")

st.subheader("Эрсдэлийн хүчин зүйлсийн дүн шинжилгээ")

col1, col2 = st.columns(2)

with col1:
    risk_factors = []
    
    income_loan_ratio = (monthly_income * 12) / loan_amount
    if income_loan_ratio < 0.3:
        risk_factors.append("Орлогын түвшин хангалтгүй")
    
    if age < 25 or age > 65:
        risk_factors.append("Эрсдэлтэй нас")
    
    if employment_years < 2:
        risk_factors.append("Ажлын туршлага бага")
    
    if employment_type in ["Бизнес эрхлэгч", "Бусад"]:
        risk_factors.append("Тогтворгүй орлого")
    
    if previous_defaults > 0:
        risk_factors.append("Өмнөх зээлийн саатал")
    
    if debt_to_income > 50:
        risk_factors.append("Өндөр өрийн дарамт")
    
    if collateral_value < loan_amount:
        risk_factors.append("Хангалтгүй барьцаа")
    
    st.write("**Эрсдлийг нэмэгдүүлэх хүчин зүйлс:**")
    if risk_factors:
        for factor in risk_factors:
            st.write(f"• {factor}")
    else:
        st.write("• Томоохон эрсдэлийн хүчин зүйл илрээгүй")

with col2:
    positive_factors = []
    
    if income_loan_ratio >= 0.5:
        positive_factors.append("Хангалттай орлогын түвшин")
    
    if 30 <= age <= 55:
        positive_factors.append("Тогтвортой нас")
    
    if employment_years >= 5:
        positive_factors.append("Сайн ажлын туршлага")
    
    if employment_type in ["Төрийн албан хаагч", "Гадаадын компани"]:
        positive_factors.append("Тогтвортой ажлын байр")
    
    if previous_defaults == 0:
        positive_factors.append("Цэвэр зээлийн түүх")
    
    if debt_to_income <= 30:
        positive_factors.append("Бага өрийн дарамт")
    
    st.write("**Эерэг хүчин зүйлс:**")
    if positive_factors:
        for factor in positive_factors:
            st.write(f"• {factor}")
    else:
        st.write("• Тодорхой эерэг хүчин зүйл илрээгүй")

st.subheader("Зөвлөмж")

if npl_rate <= 0.10:
    st.success(" **БАТЛАХЫГ ЗӨВЛӨЖ БАЙНА** - Бага эрсдэлтэй харилцагч")
    st.write("• Стандарт нөхцөлөөр зээл олгож болно")
    st.write("• Жигд хяналт тавих")
elif npl_rate <= 0.25:
    st.warning(" **НЭМЭЛТ НӨХЦӨЛТЭЙ БАТЛАХ** - Дунд эрсдэлтэй харилцагч")
    st.write("• Нэмэлт барьцаа шаардах")
    st.write("• Хүүгийн хувь нэмэх")
    st.write("• Сарын хяналт тавих")
else:
    st.error(" **ТАТГАЛЗАХЫГ ЗӨВЛӨЖ БАЙНА** - Өндөр эрсдэлтэй харилцагч")
    st.write("• Орлогын түвшинг нэмэгдүүлэх")
    st.write("• Барьцааны хэмжээг нэмэх")
    st.write("• Зээлийн хэмжээг багасгах")

st.subheader("NPL Rate-ийн чиг хандлага")

years = ["2020", "2021", "2022", "2023", "2024"]
sample_npl_rates = [6.2, 8.1, 9.5, 7.8, 8.3]  

col1, col2 = st.columns(2)

with col1:
    st.write("**Өнгөрсөн жилүүдийн NPL Rate:**")
    for year, rate in zip(years, sample_npl_rates):
        st.write(f"• {year}: {rate}%")

with col2:
    st.write("**Чиг хандлагын дүн шинжилгээ:**")
    st.write("• 2020-2022: Нэмэгдэх хандлага")
    st.write("• 2023: Буурах хандлага") 
    st.write("• 2024: Тогтвор")
    st.write(f"• Одоогийн таамаглал: **{npl_rate:.2%}**")

st.markdown("---")
st.subheader("Эрсдэлийн харьцуулалт")

risk_levels = {
    "Маш бага эрсдэл (0-5%)": "🟢",
    "Хүлээн зөвшөөрөх эрсдэл (5-10%)": "🟡", 
    "Анхаарал хандуулах эрсдэл (10-20%)": "🟠",
    "Өндөр эрсдэл (20-30%)": "🔴",
    "Маш өндөр эрсдэл (30%+)": "⚫"
}

current_category = ""
if npl_rate <= 0.05:
    current_category = "Маш бага эрсдэл (0-5%)"
elif npl_rate <= 0.10:
    current_category = "Хүлээн зөвшөөрөх эрсдэл (5-10%)"
elif npl_rate <= 0.20:
    current_category = "Анхаарал хандуулах эрсдэл (10-20%)"
elif npl_rate <= 0.30:
    current_category = "Өндөр эрсдэл (20-30%)"
else:
    current_category = "Маш өндөр эрсдэл (30%+)"

for category, emoji in risk_levels.items():
    if category == current_category:
        st.markdown(f"**{emoji} {category} ← ОДООГИЙН ТҮВШИН**")
    else:
        st.write(f"{emoji} {category}")

st.subheader("Хураангуй")

summary_data = {
    "Харилцагчийн мэдээлэл": [
        f"Зээлийн хэмжээ: {loan_amount:,.0f} ₮",
        f"Сарын орлого: {monthly_income:,.0f} ₮", 
        f"Нас: {age} настай",
        f"Ажлын туршлага: {employment_years} жил",
        f"Ажлын төрөл: {employment_type}",
        f"Боловсрол: {education_level}"
    ],
    "Эрсдэлийн үнэлгээ": [
        f"NPL Rate: {npl_rate:.2%}",
        f"Эрсдэлийн түвшин: {risk_level}",
        f"Орлого/Зээлийн харьцаа: {(monthly_income * 12 / loan_amount):.2%}",
        f"Барьцаа: {collateral_value:,.0f} ₮" if collateral_value > 0 else "Барьцаа: Байхгүй",
        f"Өрийн дарамт: {debt_to_income:.1f}%",
        f"Зээлийн түүх: {credit_history_months} сар"
    ]
}

col1, col2 = st.columns(2)
with col1:
    st.write("**Харилцагчийн мэдээлэл:**")
    for info in summary_data["Харилцагчийн мэдээлэл"]:
        st.write(f"• {info}")

with col2:
    st.write("**Эрсдэлийн үнэлгээ:**")
    for assessment in summary_data["Эрсдэлийн үнэлгээ"]:
        st.write(f"• {assessment}")

st.markdown("---")
st.markdown("**Тэмдэглэл:** Энэхүү NPL rate тооцоолол нь хувийн төсөлд хийсэн бөгөөд бодит банкны шийдвэр гаргахад бусад олон хүчин зүйлийг харгалзан үзэх шаардлагатай. " \
"Т.Баярмаа")