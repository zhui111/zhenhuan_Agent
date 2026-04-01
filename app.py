import streamlit as st
from openai import OpenAI
import json
import re

# ================= 0. 注入全局 CSS 魔法 =================
custom_css = """
<style>
    .stApp {
        background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
        background-color: #f8f1e4;
        background-image: linear-gradient(315deg, #fcf6eb 0%, #e8d09d 100%);
    }
    h1 { color: #8b0000 !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }
    .avatar-container {
        font-size: 100px; text-align: center;
        animation: float 3s ease-in-out infinite;
        text-shadow: 0px 10px 15px rgba(0,0,0,0.2);
    }
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-15px); }
        100% { transform: translateY(0px); }
    }
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.4) !important;
        backdrop-filter: blur(10px);
    }
    /* 美化数据卡片的边框 */
    div[data-testid="stMetricValue"] { color: #8b0000; font-weight: bold; }
</style>
"""

# ================= 1. 加载本地数据库 =================
@st.cache_data
def load_database():
    try:
        with open("huanhuan_db.json", "r", encoding="utf-8") as f:
            db = json.load(f)
            return db if db else {"系统提示": ["数据库提取为空，请检查"]}
    except FileNotFoundError:
        return {"系统提示": ["请先运行 data_clean.py 生成 json 数据库！"]}

db = load_database()

AVATAR_MAP = {
    "皇上": "🫅", "玄凌": "🫅", "皇后": "👑", "朱宜修": "👑",
    "甄嬛": "🪷", "莞嫔": "🪷", "熹贵妃": "🪷", "华妃": "🦚", "慕容世兰": "🦚", "年世兰": "🦚",
    "沈眉庄": "🍵", "安陵容": "🐦", "端妃": "🐢", "敬妃": "🧱", "齐妃": "🌸",
    "祺贵人": "🦊", "曹琴默": "🐍", "叶澜依": "🐆", "太后": "👵", "苏培盛": "🙇‍♂️",
    "果郡王": "笛", "温实初": "🌿"
}

# ================= 2. NLP 深度挖掘模块 (强约束 JSON 输出) =================
def analyze_subtext(character, quote, api_key, base_url):
    client = OpenAI(api_key=api_key, base_url=base_url) 
    prompt = f"""
    你现在是一个自然语言处理专家兼《甄嬛传》十级学者。请对下面这段台词进行深度剖析。
    人物：{character}
    台词：{quote}
    
    请严格按照以下 JSON 格式输出你的分析结果，不要输出任何额外的说明文字或 markdown 标记：
    {{
        "emotion": "（简述这段话字面上表达了什么样的情绪）",
        "subtext": "（用极其直白、带点搞笑的现代话翻译，心里真正在盘算什么）",
        "attack": 8, 
        "defense": 3,
        "scheme": 9,
        "radar_desc": "（一句话解释上面三个指数为什么这么打分）",
        "power": "（结合这段话，分析该角色当时在后宫的博弈策略）"
    }}
    注意：attack, defense, scheme 必须是 1-10 之间的纯数字。
    """
    
    response = client.chat.completions.create(
        model="deepseek-chat", 
        messages=[
            {"role": "system", "content": "你是一个精通清宫职场博弈心理学的 AI 助理，必须严格输出 JSON 格式。"},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"} # 强制要求模型输出 JSON
    )
    
    # 获取原始结果并清理可能的 Markdown 代码块标记
    raw_text = response.choices[0].message.content
    cleaned_text = re.sub(r'```json\n|\n```|```', '', raw_text).strip()
    return json.loads(cleaned_text)

# ================= 3. 前端展示层 =================
st.set_page_config(page_title="甄嬛传潜台词挖掘机", page_icon="🪷", layout="wide")
st.markdown(custom_css, unsafe_allow_html=True)
st.title("🪷 甄嬛传“潜台词” NLP 挖掘 Agent")
st.markdown("**欢迎小主！** 拨开后宫迷雾，利用大语言模型直击职场话术背后的隐性意图。")

with st.sidebar:
    st.header("🔑 配置大模型")
    api_key = st.text_input("API Key", type="password")
    base_url = st.text_input("Base URL", value="[https://api.deepseek.com/v1](https://api.deepseek.com/v1)")
    st.markdown("---")
    total_quotes = sum([len(v) for v in db.values()])
    st.success(f"📜 宗人府名册簿：\n\n- 记录在案小主：**{len(db)}** 位\n- 摘录起居注台词：**{total_quotes}** 句")

col1, col2, col3 = st.columns([2, 3, 1])
with col1:
    st.markdown("### 👤 点兵点将")
    character_list = list(db.keys())
    selected_char = st.selectbox("第 1 步：请翻牌子", character_list)
with col2:
    st.markdown("### 💬 经典名言")
    quotes_list = db.get(selected_char, [])
    quote_preview = {f"“{q[:20]}...”" if len(q)>20 else f"“{q}”": q for q in quotes_list} 
    selected_preview = st.selectbox(f"第 2 步：选择【{selected_char}】的台词", list(quote_preview.keys()))
    final_quote = quote_preview.get(selected_preview, "")
with col3:
    current_avatar = AVATAR_MAP.get(selected_char, "👤")
    st.markdown(f'<div class="avatar-container">{current_avatar}</div>', unsafe_allow_html=True)

current_quote = st.text_area("✍️ 最终要分析的台词文本（支持手动修改/输入）：", value=final_quote, height=100)

if st.button("🚀 启动潜台词深度挖掘"):
    if not api_key:
        st.warning("⚠️ 请先在左侧输入 API Key！")
    elif not current_quote:
        st.warning("⚠️ 台词不能为空！")
    else:
        with st.spinner(f"🔮 正在请神机妙算的大模型解析【{selected_char}】的心机..."):
            try:
                # 获取 JSON 字典
                data = analyze_subtext(selected_char, current_quote, api_key, base_url)
                st.snow() 
                st.markdown("---")
                
                # ==== 绝美排版：使用 Streamlit 容器和分栏呈现报告 ====
                st.markdown("## 📜 军机处密报")
                
                # 第一层：情绪与潜台词对比（左右分栏 + 彩色提示框）
                c_emo, c_sub = st.columns(2)
                with c_emo:
                    st.markdown("#### 🎭 表面情绪感知")
                    st.info(data.get("emotion", "分析失败")) # 用蓝色框显示表面情绪
                with c_sub:
                    st.markdown("#### 🗡️ 隐性意图提取 (潜台词)")
                    st.error(data.get("subtext", "分析失败")) # 用红色框显示毒舌潜台词
                
                st.markdown("<br>", unsafe_allow_html=True) # 留点呼吸空间
                
                # 第二层：数据仪表盘展示指数
                st.markdown("#### 📊 数据化心理画像")
                st.markdown("""<div style="background-color:rgba(255,255,255,0.5); padding:20px; border-radius:10px;">""", unsafe_allow_html=True)
                c_atk, c_def, c_sch = st.columns(3)
                c_atk.metric("⚔️ 攻击性指数", f"{data.get('attack', 0)} / 10")
                c_def.metric("🛡️ 防御性指数", f"{data.get('defense', 0)} / 10")
                c_sch.metric("🦊 心机/谋略", f"{data.get('scheme', 0)} / 10")
                st.caption(f"**💡 军机处批注：** {data.get('radar_desc', '')}")
                st.markdown("</div><br>", unsafe_allow_html=True)
                
                # 第三层：大局观分析
                st.markdown("#### ♟️ 权力局势分析")
                st.success(data.get("power", "分析失败")) # 用绿色框展示大局观
                
            except Exception as e:
                st.error(f"⚠️ 解析失败，请重试。大模型返回的格式可能不标准。报错信息：{e}")
