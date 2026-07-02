import streamlit as st
import pandas as pd

# --- 核心计算逻辑 ---
def get_labor_details(revenue):
    if revenue < 150000: m, d, s, pt = 1, 1, 2, 240
    elif revenue < 200000: m, d, s, pt = 1, 1, 3, 387
    elif revenue < 300000: m, d, s, pt = 1, 2, 5, 413
    else: m, d, s, pt = 1, 2, 5, 569
    manager_salary = 6000 if revenue < 150000 else (7000 if revenue < 260000 else 8000)
    cost = (manager_salary * m) + (5500 * d) + (4500 * s) + (20 * pt)
    total_staff = m + d + s + (pt / 30 / 4)
    return {"cost": cost, "total_staff": round(total_staff, 2)}

def get_detailed_metrics(revenue, gross_margin_rate, rent_mode, fixed_rent, rent_rate):
    gross_margin = revenue * gross_margin_rate
    rent = fixed_rent if rent_mode == "固定值" else max(fixed_rent, revenue * rent_rate)
    tax = revenue * 0.02
    fee = revenue * 0.03
    fixed_others = 46000 
    labor_data = get_labor_details(revenue)
    profit = gross_margin - rent - tax - fee - fixed_others - labor_data["cost"]
    
    daily_cups = (revenue / 30) / 15
    return {
        "营业额": revenue, "毛利": gross_margin, "房租": rent, 
        "营业税(2%)": tax, "手续费(3%)": fee, "固定支出": fixed_others, 
        "人力费用": labor_data["cost"], "净利润": profit,
        "指标_日均杯量": int(daily_cups), "指标_总用工人数": labor_data["total_staff"],
        "指标_日均人效": round((revenue/30)/labor_data["total_staff"], 1),
        "指标_高峰小时出杯": int((daily_cups * 0.70) / 4)
    }

# --- 界面布局 ---
st.set_page_config(page_title="质茶经营分析", layout="wide")
st.title("🍵 质茶生产关键指标分析")

with st.sidebar:
    st.header("⚙️ 参数配置")
    target = st.number_input("目标月利润:", -50000, 100000, 0)
    gross_margin_rate = st.slider("毛利率", 0.50, 0.80, 0.65)
    rent_mode = st.radio("房租模式", ["固定值", "固定与扣点孰高"])
    fixed_rent = st.number_input("房租保底", value=46240)
    rent_rate = st.slider("扣点比例", 0.10, 0.25, 0.16)
    calc_btn = st.button("开始计算", use_container_width=True)

if calc_btn:
    found_res = None
    for r in range(120000, 400000, 1000):
        res = get_detailed_metrics(r, gross_margin_rate, rent_mode, fixed_rent, rent_rate)
        if res["净利润"] >= target:
            found_res = res
            break
            
    if found_res:
        st.info(f"### 🎯 目标达成：需实现月营收 {found_res['营业额']:,.1f} 元")
        
        # 1. 核心五指标
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("净利润", f"{found_res['净利润']:,.1f}")
        c2.metric("日均杯量", f"{found_res['指标_日均杯量']:.1f} 杯")
        c3.metric("总用工人数", f"{found_res['指标_总用工人数']:.1f} 人")
        c4.metric("日均人效", f"{found_res['指标_日均人效']:.1f} 元")
        c5.metric("高峰小时出杯", f"{found_res['指标_高峰小时出杯']:.1f} 杯")
        
        st.write("---")
        st.subheader("📊 详细财务核算明细")
        
        # 2. 表格数据处理：保留一位小数并居中
        rev = found_res["营业额"]
        df_list = []
        for k, v in found_res.items():
            if "指标" not in k:
                df_list.append({
                    "项目": k, 
                    "金额": f"{v:,.1f}", 
                    "占比": f"{(v/rev)*100:.1f}%"
                })
        
        df = pd.DataFrame(df_list)
        # 使用 Styler 实现居中对齐
        styled_df = df.style.set_properties(**{'text-align': 'center'}).hide(axis="index")
        st.table(styled_df)
        
    else:
        st.error("未找到满足目标利润的营收方案。")