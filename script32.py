import streamlit as st
import base64
from datetime import datetime
from supabase import create_client

st.set_page_config(page_title="أكاديمية كابتن محسن", page_icon="⚽", layout="wide")

# ============================================================
# 🔥 إعدادات Supabase
# ============================================================
SUPABASE_URL = "https://yiassgywpdgdwlcavbch.supabase.co"
SUPABASE_KEY = "sb_publishable_UIGOw-9Q2Qg2S7Yb8MAgNg_VOGdntyl"  # 👈 غير ده
TABLE_NAME = "coach_data"

LOGIN_BG_IMAGE = "https://i.postimg.cc/1XBwfr7M/Screenshot-20261017-210359-Google.jpg"
HOME_BG_IMAGE = "https://i.postimg.cc/1XBwfr7M/Screenshot-20261017-210359-Google.jpg"


@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)


client = init_supabase()


# ============================================================
# دوال قاعدة البيانات
# ============================================================
def load_data():
    try:
        response = client.table(TABLE_NAME).select("*").eq("id", 1).execute()
        if response.data:
            data = response.data[0]["content"]
            if "users" not in data: data["users"] = {}
            return data
        else:
            default_data = {"schedule": [], "users": {}, "last_update_msg": "", "last_update_time": "",
                            "motivation_msg": "مجهود عظيم! 💪"}
            client.table(TABLE_NAME).insert({"id": 1, "content": default_data}).execute()
            return default_data
    except Exception as e:
        st.error(f"مشكلة في الاتصال: {e}")
        return {"schedule": [], "users": {}, "motivation_msg": ""}


def save_data(data):
    try:
        client.table(TABLE_NAME).update({"content": data}).eq("id", 1).execute()
    except Exception as e:
        st.error(f"فشل الحفظ: {e}")


if "data" not in st.session_state:
    st.session_state.data = load_data()

if "user" not in st.session_state:
    if "user" in st.query_params:
        saved_email = st.query_params["user"]
        if saved_email in st.session_state.data["users"]:
            st.session_state.user = {"email": saved_email, **st.session_state.data["users"][saved_email]}
        else:
            st.session_state.user = None
    else:
        st.session_state.user = None


# ============================================================
# التصميم الأساسي
# ============================================================
def set_bg_image(src):
    if not src: return
    st.markdown(f"""
    <style>
    .stApp {{ background-image: url("{src}"); background-size: cover; background-position: center top; direction: rtl; }}
    [data-testid="stAppViewContainer"] {{ background-color: rgba(15, 23, 42, 0.4); }}
    [data-testid="stHeader"] {{ display: none !important; }}
    button[data-baseweb="tab"] p {{ font-size: 1.2rem !important; font-weight: 900 !important; color: white !important; }}
    .big-title {{ font-size: 2.5rem; font-weight: 900; color: #00e5ff; text-align: center; text-shadow: 0px 0px 10px rgba(0, 229, 255, 0.5); }}
    .profile-pic {{ width: 150px; height: 180px; border-radius: 15px; object-fit: cover; border: 4px solid #00e5ff; }}
    .sub {{ color: #ffffff; font-weight: 600; }}
    </style>
    """, unsafe_allow_html=True)


# ============================================================
# صفحة تسجيل الدخول
# ============================================================
def show_auth_screen():
    set_bg_image(LOGIN_BG_IMAGE)

    # تقسيم الشاشة عشان صندوق الدخول يكون في النص
    _, col, _ = st.columns([1, 1.5, 1])

    with col:
        st.markdown("""
        <div style="background: rgba(17, 24, 39, 0.9); padding: 30px; border-radius: 20px; border: 2px solid #00e5ff; box-shadow: 0 0 20px rgba(0, 229, 255, 0.3);">
            <h2 style="text-align:center; color:#00e5ff; margin-top:0;">⚽ كابتن محسن</h2>
            <p style="text-align:center; color:white; margin-bottom: 20px;">انضم لأكبر أكاديمية كرة قدم</p>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["دخول", "حساب جديد"])

        with tab1:
            email = st.text_input("رقم الموبايل أو الإيميل", key="login_email")
            pw = st.text_input("كلمة المرور", type="password", key="login_pw")
            if st.button("دخول", use_container_width=True, type="primary"):
                cred = email.lower()
                if "@" not in cred: cred = f"{cred}@mobile.local"
                u = st.session_state.data["users"].get(cred)
                if u and u["password"] == pw:
                    st.session_state.user = {"email": cred, **u}
                    st.query_params["user"] = cred
                    st.rerun()
                else:
                    st.error("بيانات خطأ")

        with tab2:
            n = st.text_input("الاسم بالكامل", key="up_name")
            e = st.text_input("رقم الموبايل أو الإيميل", key="up_email")
            p = st.text_input("كلمة المرور", type="password", key="up_pw")
            if st.button("إنشاء حساب", use_container_width=True, type="primary"):
                cred = e.lower()
                if "@" not in cred: cred = f"{cred}@mobile.local"
                if cred in st.session_state.data["users"]:
                    st.error("هذه البيانات مسجلة بالفعل!")
                else:
                    st.session_state.data["users"][cred] = {"name": n, "password": p, "info_complete": False,
                                                            "profile_pic": ""}
                    save_data(st.session_state.data)
                    st.session_state.user = {"email": cred, **st.session_state.data["users"][cred]}
                    st.query_params["user"] = cred
                    st.rerun()


# ============================================================
# البيانات الشخصية
# ============================================================
def show_info_screen():
    set_bg_image(LOGIN_BG_IMAGE)
    st.markdown("<div class='big-title'>بياناتك الشخصية</div>", unsafe_allow_html=True)
    phone = st.text_input("الموبايل", key="info_phone")
    age = st.number_input("العمر", 5, 99, 16, key="info_age")
    foot = st.radio("القدم", ["يمين", "شمال"], key="info_foot")
    if st.button("متابعة", key="btn_info"):
        em = st.session_state.user["email"]
        st.session_state.data["users"][em].update(
            {"phone": phone, "age": str(age), "foot": foot, "info_complete": True})
        st.session_state.user = {"email": em, **st.session_state.data["users"][em]}
        save_data(st.session_state.data)
        st.rerun()


# ============================================================
# لوحة تحكم اللاعب
# ============================================================
def show_dashboard():
    set_bg_image(HOME_BG_IMAGE)
    st.markdown("<div class='big-title'>أكاديمية كابتن محسن</div>", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["👤 البروفايل", "📅 احجز", "✈️ تواصل"])

    with t1:
        u = st.session_state.user
        col_pic, col_info = st.columns([1, 2])

        with col_pic:
            if u.get("profile_pic"):
                st.markdown(f'<img src="{u["profile_pic"]}" class="profile-pic">', unsafe_allow_html=True)
            else:
                st.markdown(f'<img src="https://www.w3schools.com/howto/img_avatar.png" class="profile-pic">',
                            unsafe_allow_html=True)

        with col_info:
            st.markdown(f"<h3 style='color: #00e5ff; margin-bottom: 0;'>{u['name']}</h3>", unsafe_allow_html=True)
            st.write(f"📱 الموبايل: {u.get('phone', 'غير مسجل')}")
            st.write(f"🎂 العمر: {u.get('age', 'غير مسجل')} سنة")
            st.write(f"🦶 القدم المسيطرة: {u.get('foot', 'غير مسجل')}")

        st.markdown("---")
        st.subheader("📷 تغيير الصورة الشخصية")
        uploaded_file = st.file_uploader("اختر صورة من جهازك", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            if st.button("حفظ الصورة الجديدة", type="primary"):
                bytes_data = uploaded_file.getvalue()
                base64_str = base64.b64encode(bytes_data).decode()
                new_pic_url = f"data:image/jpeg;base64,{base64_str}"
                em = u["email"]
                st.session_state.data["users"][em]["profile_pic"] = new_pic_url
                st.session_state.user["profile_pic"] = new_pic_url
                save_data(st.session_state.data)
                st.success("تم حفظ صورتك بنجاح! 🎉")
                st.rerun()

    with t2:
        st.write("التدريبات قريباً (Elite & Normal)")

    with t3:
        st.markdown("[تواصل تليجرام](https://t.me/Coashmaher1bot)", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🚪 تسجيل خروج", use_container_width=True, key="btn_logout"):
        st.session_state.user = None
        st.query_params.clear()
        st.rerun()


# ============================================================
# الراوتر
# ============================================================
if st.session_state.user is None:
    show_auth_screen()
elif not st.session_state.user.get("info_complete"):
    show_info_screen()
else:
    show_dashboard()