import streamlit as st
import pandas as pd

st.set_page_config(page_title="数据展示")
st.title("数据表格展示")

# 创建示例数据
data = {
    "姓名": ["张三", "李四", "王五"],
    "年龄": [25, 30, 35],
    "城市": ["北京", "上海", "广州"],
}
df = pd.DataFrame(data)

# 使用 for 循环遍历数据框的每一行
for index, row in df.iterrows():
    # 创建三列布局
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    # 在前三列显示数据
    with col1:
        st.write(row["姓名"])
    with col2:
        st.write(row["年龄"])
    with col3:
        st.write(row["城市"])

    # 在第四列显示按钮
    with col4:
        if st.button("详情", key=f"btn_{index}"):
            st.write(f"你点击了 {row['姓名']} 的详情按钮")

    # 添加分割线
    st.divider()
