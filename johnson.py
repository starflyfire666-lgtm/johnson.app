import streamlit as st
import plotly.express as px
import pandas as pd

def johnson_scheduling(jobs):
    group_a = []
    group_b = []
    for job in jobs:
        name, t1, t2 = job
        if t1 <= t2:
            group_a.append(job)
        else:
            group_b.append(job)

    group_a.sort(key=lambda x: x[1])
    group_b.sort(key=lambda x: x[2], reverse=True)

    optimal_jobs = group_a + group_b
    optimal_sequence = [job[0] for job in optimal_jobs]

    schedule_details = []
    m1_finish = 0
    m2_finish = 0

    for job in optimal_jobs:
        name, t1, t2 = job
        m1_finish += t1
        m2_start = max(m2_finish, m1_finish)
        m2_finish = m2_start + t2

        schedule_details.append({
            "工件": name,
            "M1加工时间": t1,
            "M2加工时间": t2,
            "M1完工时间": m1_finish,
            "M2开始时间": m2_start,
            "M2完工时间": m2_finish
        })
    makespan = m2_finish
    return optimal_sequence, schedule_details, makespan

# 页面配置
st.set_page_config(page_title="Johnson法则调度工具", layout="wide")
st.title("Johnson法则｜双机流水车间调度小程序")
st.info("适用条件：所有工件工艺路线 M1 → M2，求解最小总完工时间 Makespan")

# 输入区域
job_count = st.number_input("工件数量", min_value=1, value=4, step=1)
jobs = []
st.subheader("请输入各工件加工时间")
for i in range(int(job_count)):
    col1, col2 = st.columns(2)
    with col1:
        t1 = st.number_input(f"工件{i+1} M1加工时间", min_value=0, value=3, key=f"t1_{i}")
    with col2:
        t2 = st.number_input(f"工件{i+1} M2加工时间", min_value=0, value=3, key=f"t2_{i}")
    jobs.append((f"工件{i+1}", t1, t2))

# 计算按钮
if st.button("开始调度计算", type="primary"):
    opt_seq, details, makespan = johnson_scheduling(jobs)
    st.divider()
    st.subheader("📌 计算结果")
    st.write(f"最优加工顺序：{' → '.join(opt_seq)}")
    st.write(f"总完工时间 Makespan = {makespan}")

    st.divider()
    st.subheader("📋 调度明细表")
    st.dataframe(details, use_container_width=True)

    # 绘制甘特图
    gantt_data = []
    for d in details:
        m1_start = d["M1完工时间"] - d["M1加工时间"]
        gantt_data.append({
            "任务": d["工件"],
            "机器": "M1",
            "开始": m1_start,
            "结束": d["M1完工时间"]
        })
        gantt_data.append({
            "任务": d["工件"],
            "机器": "M2",
            "开始": d["M2开始时间"],
            "结束": d["M2完工时间"]
        })
    df_gantt = pd.DataFrame(gantt_data)
    fig = px.timeline(df_gantt, x_start="开始", x_end="结束", y="任务", color="机器", title="调度甘特图")
    fig.update_xaxes(type="linear")
    st.plotly_chart(fig, use_container_width=True)
