import streamlit as st
import requests
import json
from pathlib import Path

# 页面基础配置
st.set_page_config(
    page_title="增强版知识库问答系统",
    layout="wide",  # 使用宽屏模式
)

# 定义API基础URL
API_BASE_URL = "http://localhost:8012/v1"  # 根据实际情况修改

# 侧边栏配置
with st.sidebar:
    st.header("知识库管理")

    # 新增知识库
    with st.expander("新增知识库", expanded=True):
        new_kb_name = st.text_input("知识库名称")
        if st.button("创建知识库"):
            if new_kb_name:
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/init",
                        json={"root": new_kb_name},
                    )
                    if response.status_code == 200:
                        st.success(f"知识库 '{new_kb_name}' 创建成功！")
                    else:
                        st.error("创建失败：" + response.text)
                except Exception as e:
                    st.error(f"创建失败：{str(e)}")

    # 选择知识库
    try:
        kb_list_response = requests.get(f"{API_BASE_URL}/list_knowledge_bases")
        knowledge_bases = kb_list_response.json()
        selected_kb = st.selectbox("选择知识库", knowledge_bases)
    except Exception as e:
        st.error(f"获取知识库列表失败: {str(e)}")
        selected_kb = None


# 主界面 - 文档管理
st.title("增强版知识库问答系统")

# 文档上传部分
with st.expander("文档上传与索引", expanded=True):
    col1, col2 = st.columns(2)

    with col1:
        uploaded_files = st.file_uploader(
            "上传文档", accept_multiple_files=True, type=["txt", "md", "pdf"]
        )

        if uploaded_files and selected_kb:
            if st.button("上传并建立索引"):
                for file in uploaded_files:
                    # 保存文件
                    file_path = Path(f"temp/{file.name}")
                    file_path.parent.mkdir(exist_ok=True)
                    file_path.write_bytes(file.getvalue())

                    # 上传文件
                    try:
                        files = {"file": open(file_path, "rb")}
                        response = requests.post(
                            f"{API_BASE_URL}/upload",
                            files=files,
                            data={"knowledge_base_name": selected_kb},
                        )
                        if response.status_code == 200:
                            st.success(f"文件 {file.name} 上传成功！")
                        else:
                            st.error(f"文件 {file.name} 上传失败：" + response.text)
                    except Exception as e:
                        st.error(f"上传失败：{str(e)}")
                    finally:
                        file_path.unlink()  # 删除临时文件

    with col2:
        # 索引配置
        st.subheader("索引配置")
        chunk_size = st.slider("分块大小", 100, 1000, 500)
        chunk_overlap = st.slider("重叠大小", 0, 100, 50)

        if st.button("执行索引"):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/index",
                    json={
                        "knowledge_base_name": selected_kb,
                        "chunk_size": chunk_size,
                        "chunk_overlap": chunk_overlap,
                    },
                )
                if response.status_code == 200:
                    st.success("索引创建成功！")
                else:
                    st.error("索引创建失败：" + response.text)
            except Exception as e:
                st.error(f"索引创建失败：{str(e)}")


# 问答配置和对话界面
st.divider()

# 问答参数配置
with st.expander("问答配置", expanded=False):
    temperature = st.slider("温度", 0.0, 1.0, 0.7)
    top_k = st.slider("返回结果数量", 1, 10, 3)
    score_threshold = st.slider("相似度阈值", 0.0, 1.0, 0.5)

# 对话界面
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 用户输入
if prompt := st.chat_input("请输入您的问题"):
    if not selected_kb:
        st.error("请先选择知识库！")
    else:
        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 调用查询接口
        try:
            response = requests.post(
                f"{API_BASE_URL}/query",
                json={
                    "knowledge_base_name": selected_kb,
                    "query": prompt,
                    "top_k": top_k,
                    "score_threshold": score_threshold,
                    "temperature": temperature,
                },
            )

            if response.status_code == 200:
                answer = response.json()["answer"]
                # 添加助手回复
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )
                with st.chat_message("assistant"):
                    st.markdown(answer)
            else:
                st.error("查询失败：" + response.text)
        except Exception as e:
            st.error(f"查询失败：{str(e)}")

# 清空对话按钮
if st.button("清空对话"):
    st.session_state.messages = []
    st.rerun()
