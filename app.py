import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm  # 引入字体管理器
import os

# 设置网页基本配置
st.set_page_config(page_title="质茶门店利润敏感度测试", layout="wide")

# ★★★ 核心修复：动态加载项目内的中文字体文件，彻底根治云端方块字 ★★★
font_path = "simhei.ttf"
if os.path.exists(font_path):
    # 如果找到了上传的字体文件，优先使用它
    my_font = fm.FontProperties(fname=font_path)
    plt.rcParams['font.sans-serif'] = [my_font.get_name()]
else:
    # 本地兜底配置
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial']
    my_font = fm.FontProperties()

plt.rcParams['axes.unicode_minus'] = False # 正常显示负号

# 最上面的名字
st.title("🧋 质茶门店利润敏感度测试")
st.markdown("---")

# 1. 侧边栏：核心销售输入滑块
st.sidebar.header("🎯 核心业务变量调整")
daily_cups = st.sidebar.slider("日均出杯量 (杯)", 100, 1000, 550, step=10) 
avg_price = st.sidebar.slider("杯均客单价 (元)", 12.0, 25.0, 15.0, step=0.5)
raw_material_rate = st.sidebar.slider("原材料成本率 (%)", 30.0, 45.0, 35.0, step=0.5) / 100

st.sidebar.markdown("---")
st.sidebar.header("🏗️ 初始投资配置")
initial_investment = st.sidebar.number_input("门店营建投资总额 (元)", value=600000, step=50000)

# 2. 财务算法核心逻辑
monthly_revenue = daily_cups * 30 * avg_price 
cost_raw = monthly_revenue * raw_material_rate 

rent = max(46240, monthly_revenue * 0.16)

if monthly_revenue < 150000:
    labor = 25300
elif monthly_revenue < 200000:
    labor = 33740
elif monthly_revenue < 300000:
    labor = 48760
else:
    labor = 52880

depreciation = 25000
other_ops_costs = (
    5576          
    + 6000        
    + 5000        
    + 10000       
    + depreciation 
    + (monthly_revenue * 0.02) 
    + (monthly_revenue * 0.03) 
)

net_profit = monthly_revenue - cost_raw - rent - labor - other_ops_costs
net_margin = (net_profit / monthly_revenue) * 100 if monthly_revenue > 0 else 0

monthly_cash_flow = net_profit + depreciation
payback_period = initial_investment / monthly_cash_flow if monthly_cash_flow > 0 else float('inf')

# 3. 前端数据大屏展示
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📊 模拟月度总收入", f"￥{monthly_revenue:,.0f}")
with col2:
    if net_profit >= 0:
        st.metric("💰 预计月度账面利润 (损益)", f"￥{net_profit:,.0f}", delta=f"{net_margin:.1f}% 利润率")
    else:
        st.metric("💰 预计月度账面利润 (损益)", f"￥{net_profit:,.0f}", delta=f"{net_margin:.1f}% 利润率", delta_color="inverse")
with col3:
    if payback_period != float('inf') and payback_period < 100:
        st.metric("⏳ 预计投资回收期 (现金流口径)", f"{payback_period:.1f} 个月", delta="模型健康" if payback_period <= 12 else "需监控风险", delta_color="normal")
    else:
        st.metric("⏳ 预计投资回收期 (现金流口径)", "无法回本", delta="现金流为负", delta_color="inverse")
with col4:
    rent_status = "触发16%营业额抽成" if (monthly_revenue * 0.16) > 46240 else "触发基础保底房租"
    st.metric("🏪 当前租金计算状态", f"￥{rent:,.0f}", delta=rent_status, delta_color="off")

st.markdown("---")

# 4. 图表区
col_left, col_right = st.columns(2)

# 左下：月度成本利润结构
with col_left:
    st.markdown("### 🍕 月度成本利润结构")
    labels = ['原材料成本', '房租物业', '人力成本', '折旧摊销', '税费及其他杂费', '账面净利润']
    sizes = [cost_raw, rent, labor, depreciation, other_ops_costs - depreciation, max(0, net_profit)]
    
    fig1, ax1 = plt.subplots(figsize=(6, 5))
    colors_list = ['#ffb3b3','#66b3ff','#99ff99','#ffcc99','#c2c2f0','#76d7c4']
    
    # 将传进去的字体应用到饼图的文字标签上
    wedges, texts, autotexts = ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, 
                                       colors=colors_list, wedgeprops=dict(width=0.4, edgecolor='w'))
    
    # 强制让饼图的所有汉字使用上传的字体文件，防止乱码
    for text in texts:
        text.set_fontproperties(my_font)
    for autotext in autotexts:
        autotext.set_fontproperties(my_font)
        
    st.pyplot(fig1)

# 右下：回报周期敏感度测试
with col_right:
    st.markdown("### 📉 回报周期敏感度测试")
    
    cup_tests = range(100, 1010, 10) 
    payback_tests = []
    valid_cups = []
    
    for c in cup_tests:
        rev = c * 30 * avg_price
        r_raw = rev * raw_material_rate
        r_rent = max(46240, rev * 0.16)
        r_labor = 25300 if rev < 150000 else (33740 if rev < 200000 else (48760 if rev < 300000 else 52880))
        r_other = 52576 + (rev * 0.05)
        
        r_profit = rev - r_raw - r_rent - r_labor - r_other
        r_cash_flow = r_profit + depreciation
        
        if r_cash_flow > 0:
            p_period = initial_investment / r_cash_flow
            if p_period <= 48: 
                payback_tests.append(p_period)
                valid_cups.append(c)
        
    fig2, ax2 = plt.subplots(figsize=(6, 5))
    
    if len(payback_tests) > 0:
        ax2.plot(valid_cups, payback_tests, color='crimson', marker='.', linewidth=2)
        
        # 强制给图例和轴标签设置上传的中文字体
        ax2.axhline(12, color='green', linestyle='--', alpha=0.6, label='12个月 (黄金周转线)')
        ax2.axhline(18, color='orange', linestyle='--', alpha=0.6, label='18个月 (风险预警线)')
        
        if payback_period != float('inf') and payback_period <= 48:
            ax2.plot(daily_cups, payback_period, marker='*', color='gold', markersize=15, label='当前滑块所处状态')
            
        ax2.set_xlabel("日均出杯量 (杯)", fontproperties=my_font)
        ax2.set_ylabel("投资回收期 (个月)", fontproperties=my_font)
        
        max_y = max(payback_tests) if len(payback_tests) > 0 else 24
        ax2.set_ylim(0, min(48, max(24, max_y + 4)))
        ax2.set_xlim(100, 1000)
        
        # 图例字体应用
        leg = ax2.legend()
        for text in leg.get_texts():
            text.set_fontproperties(my_font)
            
        ax2.grid(True, linestyle=':', alpha=0.6)
    else:
        ax2.text(0.5, 0.5, "当前价格/成本配置下，全盘现金流为负，无法回本", 
                 ha='center', va='center', fontsize=12, color='gray', fontproperties=my_font)
        ax2.set_xlim(100, 1000)
        ax2.set_ylim(0, 24)
        
    st.pyplot(fig2)