import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Deadline Guardian",
    page_icon="⏳",
    layout="wide"
)

st.markdown("""
<style>
.main {
    background-color: #0e1117;
}
h1, h2, h3 {
    color: #00ffd5;
}
div.stButton > button {
    background-color: #00ffd5;
    color: black;
    font-weight: bold;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)
# ================= DATABASE =================

DB_FILE = "database.json"

def load_database():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_database(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

database = load_database()

# ================= LOGIN =================

st.sidebar.title("🔐 Login")

username = st.sidebar.text_input("Nhập tên của bạn")

if not username:
    st.warning("Vui lòng nhập tên để sử dụng app")
    st.stop()

if username not in database:
    database[username] = {
        "tasks": [],
        "badges": 0
    }
    save_database(database)

user_data = database[username]
tasks = user_data["tasks"]
badges = user_data["badges"]

# ================= TITLE =================

st.title("⏳ Deadline Guardian")
st.subheader("Trợ lý bảo vệ bạn khỏi trễ deadline")

# ================= ADD TASK =================

st.write("## ➕ Thêm bài tập mới")

task_name = st.text_input("Tên bài tập")
deadline = st.date_input("Ngày nộp")

task_type = st.selectbox(
    "Loại bài",
    ["Thuyết trình", "Bài luận", "Ôn thi", "Bài tập ngắn"]
)

if st.button("Tạo kế hoạch bằng AI"):

    today = datetime.today().date()
    days_left = (deadline - today).days

    if days_left <= 0:
        st.error("Deadline không hợp lệ!")
    else:

        if task_type == "Thuyết trình":
            stages = [
                "Lên ý tưởng",
                "Nghiên cứu tài liệu",
                "Làm slide",
                "Chỉnh sửa slide",
                "Luyện tập"
            ]
        elif task_type == "Bài luận":
            stages = [
                "Tìm tài liệu",
                "Lập dàn ý",
                "Viết bản nháp",
                "Chỉnh sửa",
                "Hoàn thiện"
            ]
        elif task_type == "Ôn thi":
            stages = [
                "Ôn lý thuyết",
                "Làm bài tập cơ bản",
                "Làm đề nâng cao",
                "Tổng hợp kiến thức",
                "Ôn lại điểm yếu"
            ]
        else:
            stages = [
                "Hiểu đề",
                "Làm bài",
                "Kiểm tra lại"
            ]

        plan = []
        for i in range(min(days_left, len(stages))):
            work_day = today + timedelta(days=i)
            plan.append({
                "date": str(work_day),
                "task": stages[i],
                "done": False
            })

        new_task = {
            "name": task_name,
            "deadline": str(deadline),
            "type": task_type,
            "days_left": days_left,
            "plan": plan,
            "celebrated": False
        }

        tasks.append(new_task)

        database[username]["tasks"] = tasks
        save_database(database)

        st.success("Đã tạo kế hoạch thành công!")

# ================= DASHBOARD =================

st.divider()
st.header("📊 Dashboard")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🏆 Total Badges", badges)
    # ===== LEVEL SYSTEM =====
if badges >= 10:
    st.markdown("## 👑 Time Lord")
    st.success("Bạn đã hoàn toàn kiểm soát thời gian!")
elif badges >= 5:
    st.markdown("## 🛡 Master Guardian")
    st.info("Bạn đang làm chủ deadline!")
elif badges >= 1:
    st.markdown("## 🥉 Rookie Guardian")
    st.write("Khởi đầu rất tốt!")
else:
    st.write("Chưa có badge nào.")

with col2:
    st.metric("📚 Total Tasks", len(tasks))

with col3:
    urgent_tasks = sum(1 for t in tasks if t["days_left"] <= 2)
    st.metric("🔴 Urgent Tasks", urgent_tasks)


# ================= TASK LIST =================

st.write("## 📚 Danh sách bài tập")

if tasks:

    for index, t in enumerate(tasks):

        with st.container(border=True):

            st.subheader(f"📌 {t['name']}")
            st.caption(f"Loại: {t['type']} | Deadline: {t['deadline']}")

            # ===== COUNTDOWN =====
            try:
                deadline_date = datetime.strptime(t["deadline"], "%Y-%m-%d").date()
                days_remaining = (deadline_date - datetime.today().date()).days

                st.write(f"⏳ Còn {days_remaining} ngày tới deadline")

                if days_remaining <= 2:
                    st.error("🚨 Gấp!")
                elif days_remaining <= 5:
                    st.warning("⚠ Sắp tới hạn")
                else:
                    st.success("✔ Còn thời gian")

            except:
                st.warning("Deadline không hợp lệ")

            # ===== CHECKLIST =====
            completed = 0

            for i, step in enumerate(t["plan"]):

                checkbox = st.checkbox(
                    f"{step['date']} - {step['task']}",
                    value=step.get("done", False),
                    key=f"{index}-{i}"
                )

                if checkbox:
                    tasks[index]["plan"][i]["done"] = True
                    completed += 1
                else:
                    tasks[index]["plan"][i]["done"] = False

            total_steps = len(t["plan"])
            percent = int((completed / total_steps) * 100) if total_steps > 0 else 0

            st.progress(percent)
            st.caption(f"Progress: {percent}%")

            # ===== BADGE =====
            if percent == 100 and not t.get("celebrated", False):
                badges += 1
                tasks[index]["celebrated"] = True
                st.success("🎉 Hoàn thành task!")
                st.balloons()

else:
    st.info("Chưa có task nào.")
# ================= SAVE STATE =================

database[username]["tasks"] = tasks
database[username]["badges"] = badges
save_database(database)

st.divider()
st.caption("Made with ❤️ by Cat Tuong | Streamlit App")











