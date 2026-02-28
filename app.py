import streamlit as st
from datetime import datetime, timedelta
import json
import os

st.set_page_config(
    page_title="Deadline Guardian",
    page_icon="⏳",
    layout="wide"
)

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

with col2:
    st.metric("📚 Total Tasks", len(tasks))

with col3:
    urgent_tasks = sum(1 for t in tasks if t["days_left"] <= 2)
    st.metric("🔴 Urgent Tasks", urgent_tasks)

# ================= TASK LIST =================

st.write("## 📚 Danh sách bài tập")

for index, t in enumerate(tasks):

    with st.container(border=True):

        st.subheader(f"📌 {t['name']}")
        st.caption(f"Loại: {t['type']} | Deadline: {t['deadline']}")

        completed = 0

        for i, step in enumerate(t["plan"]):
            checkbox = st.checkbox(
                f"{step['date']} - {step['task']}",
                value=step.get("done", False),
                key=f"{username}-{index}-{i}"
            )

            if checkbox:
                tasks[index]["plan"][i]["done"] = True
                completed += 1
            else:
                tasks[index]["plan"][i]["done"] = False

        total_steps = len(t["plan"])
        progress = completed / total_steps if total_steps > 0 else 0
        percent = int(progress * 100)

        st.progress(percent)
        st.caption(f"Progress: {percent}%")

        if percent == 100 and not t["celebrated"]:
            badges += 1
            tasks[index]["celebrated"] = True
            st.balloons()

        if percent == 100:
            st.success("🎉 HOÀN THÀNH!")

        if st.button("🗑 Xoá bài này", key=f"delete-{username}-{index}"):
            tasks.pop(index)
            database[username]["tasks"] = tasks
            database[username]["badges"] = badges
            save_database(database)
            st.rerun()

# ================= SAVE STATE =================

database[username]["tasks"] = tasks
database[username]["badges"] = badges
save_database(database)

st.divider()
st.caption("Made with ❤️ by Cat Tuong | Streamlit App")
