import streamlit as st
from datetime import datetime, timedelta
import json
import os

st.set_page_config(
    page_title="Deadline Guardian",
    page_icon="⏳",
    layout="wide"
)

st.title("⏳ Deadline Guardian")
st.subheader("Trợ lý bảo vệ bạn khỏi trễ deadline")

DB_FILE = "tasks.json"

# ===== DATABASE =====
def load_tasks():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)

tasks = load_tasks()
BADGE_FILE = "badges.json"

def load_badges():
    if os.path.exists(BADGE_FILE):
        with open(BADGE_FILE, "r") as f:
            return json.load(f)
    return 0

def save_badges(count):
    with open(BADGE_FILE, "w") as f:
        json.dump(count, f)

badges = load_badges()

# ===== THÊM BÀI TẬP =====
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
                "Luyện tập thuyết trình"
            ]
        elif task_type == "Bài luận":
            stages = [
                "Tìm tài liệu",
                "Lập dàn ý",
                "Viết bản nháp",
                "Chỉnh sửa nội dung",
                "Hoàn thiện & kiểm tra"
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
                "Hiểu yêu cầu đề",
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
            "plan": plan
        }

        tasks.append(new_task)
        save_tasks(tasks)
        st.success("Đã tạo kế hoạch thành công!")

# ===== DASHBOARD =====
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

# Xác định cấp độ
if badges >= 10:
    st.markdown("## 👑 Time Lord")
    st.markdown("Bạn đã hoàn toàn kiểm soát thời gian!")
elif badges >= 5:
    st.markdown("## 🛡 Master Guardian")
    st.markdown("Bạn đang làm chủ deadline!")
elif badges >= 1:
    st.markdown("## 🥉 Rookie Guardian")
    st.markdown("Khởi đầu rất tốt!")
else:
    st.markdown("Chưa có badge nào.")

total_tasks = len(tasks)
urgent_tasks = sum(1 for t in tasks if t["days_left"] <= 2)

st.write(f"📚 Tổng số bài: {total_tasks}")
st.write(f"🔴 Sắp tới hạn (≤2 ngày): {urgent_tasks}")

# ===== HIỂN THỊ BÀI TẬP =====
st.write("## 📚 Danh sách bài tập")

for index, t in enumerate(tasks):

    task_type = t.get("type", "Không xác định")

    with st.container(border=True):
        st.subheader(f"📌 {t['name']}")
        st.caption(f"Loại: {task_type} | Deadline: {t['deadline']}")

        # Mức độ nguy cơ
        if t["days_left"] >= 5:
            st.markdown("🟢 An toàn")
        elif 2 <= t["days_left"] <= 4:
            st.markdown("🟡 Nguy cơ trung bình")
        else:
            st.markdown("🔴 Nguy cơ cao")

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
        progress = completed / total_steps if total_steps > 0 else 0

        percent = int(progress * 100)
        st.progress(percent)
        st.caption(f"Progress: {percent}% completed")

        if percent == 100:
            if not t.get("celebrated", False):
                badges += 1
                save_badges(badges)
                tasks[index]["celebrated"] = True
                save_tasks(tasks)

            st.success("🎉 HOÀN THÀNH! Bạn đã đánh bại deadline!")
            st.balloons()

            if badges >= 10:
                title = "👑 TIME LORD"
            elif badges >= 5:
                title = "🛡 MASTER GUARDIAN"
            else:
                title = "🥉 ROOKIE GUARDIAN"

            st.markdown("## 🏆 BADGE UNLOCKED!")
            st.markdown(f"### {title}")

            st.image(
                "https://media.giphy.com/media/111ebonMs90YLu/giphy.gif",
                caption="Deadline Guardian tự hào về bạn 😎",
            )

        # Nút xoá
        if st.button("🗑 Xoá bài này", key=f"delete-{index}"):
            tasks.pop(index)
            save_tasks(tasks)
            st.rerun()

save_tasks(tasks)

st.divider()
st.caption("Made with ❤️ by Cat Tuong | Streamlit App")
