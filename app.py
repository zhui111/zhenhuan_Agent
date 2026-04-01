import streamlit as st
from openai import OpenAI
import json

# ================= 0. 注入全局 CSS 魔法 (UI 升级核心) =================
# 这里我们用 CSS 渐变色打造“皇家琉璃金”背景，并写了一个叫 float 的悬浮动画
custom_css = """
<style>
    /* 替换整体页面背景色（古风柔和渐变） */
    .stApp {
        background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
        background-color: #f8f1e4;
        background-image: linear-gradient(315deg, #fcf6eb 0%, #e8d09d 100%);
    }
    
    /* 标题样式调整，增加古风威严感 */
    h1 {
        color: #8b0000 !important; 
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }

    /* 动态小人专属动画：呼吸悬浮效果 */
    .avatar-container {
        font-size: 100px;
        text-align: center;
        animation: float 3s ease-in-out infinite;
        text-shadow: 0px 10px 15px rgba(0,0,0,0.2);
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-15px); }
        100% { transform: translateY(0px); }
    }
    
    /* 让边栏半透明，融入背景 */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.4) !important;
        backdrop-filter: blur(10px);
    }
</style>
"""

# ================= 1. 加载我们辛苦洗出来的本地数据库 =================
@st.cache_data
def load_database():
    try:
        with open("huanhuan_db.json", "r", encoding="utf-8") as f:
            db = json.load(f)
            if not db:
                return {"系统提示": ["数据库提取为空，请检查"]}
            return db
    except FileNotFoundError:
        return {"系统提示": ["请先运行 data_clean.py 生成 json 数据库！"]}

db = load_database()

# ---- 人物专属动画头像映射表 ----
# 用极具代表性的 Emoji 作为人物象征，如果没有匹配到就用默认的隐形人
AVATAR_MAP = {
    "皇上": "🫅", "玄凌": "🫅", 
    "皇后": "👑", "朱宜修": "👑",
    "甄嬛": "🪷", "莞嫔": "🪷", "熹贵妃": "🪷",
    "华妃": "🦚", "慕容世兰": "🦚", "年世兰": "🦚",
    "沈眉庄": "🍵", "安陵容": "🐦", 
    "端妃": "🐢", "敬妃": "🧱", "齐妃": "🌸",
    "祺贵人": "🦊", "曹琴默": "🐍", "叶澜依": "🐆",
    "太后": "👵", "苏培盛": "🙇‍♂️", "果郡王": "笛", "温实初": "🌿"
}

# ================= 2. NLP 深度挖掘模块 =================
def analyze_subtext(character, quote, api_key, base_url):
    client = OpenAI(api_key=api_key, base_url=base_url) 
    prompt = f"""
    你现在是一个自然语言处理专家兼《甄嬛传》十级学者。请对下面这段台词进行深度文本挖掘和心理学剖析。
    
    人物：{character}
    台词：{quote}
    
    请输出以下 markdown 格式的数据挖掘报告：
    ### 🎭 表面情绪感知 (Surface Emotion)
    （简述这段话字面上表达了什么样的情绪？比如：愤怒、委屈、大义凛然）
    ### 🗡️ 隐性意图提取 (潜台词 Subtext)
    （用极其直白、甚至带点搞笑的现代话翻译一下，她/他心里真正在盘算什么？想达到什么目的？）
    ### 📊 数据化心理画像
    - **攻击性指数**：(1-10分，并说明理由)
    - **防御性指数**：(1-10分，并说明理由)
    - **心机/谋略指数**：(1-10分，并说明理由)
    ### ♟️ 权力局势分析
    （结合这段话，分析该角色当时在后宫的权力地位、处境以及博弈策略。）
    """
    
    response = client.chat.completions.create(
        model="deepseek-chat", 
        messages=[
            {"role": "system", "content": "你是一个精通清宫职场博弈心理学的 AI 助理，语言风格犀利、幽默且一针见血。"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# ================= 3. 前端展示层 =================
st.set_page_config(page_title="甄嬛传潜台词挖掘机", page_icon="🪷", layout="wide")

# 注入 CSS
st.markdown(custom_css, unsafe_allow_html=True)

st.title("🪷 甄嬛传“潜台词” NLP 挖掘 Agent")
st.markdown("**欢迎小主！** 拨开后宫迷雾，利用大语言模型直击职场话术背后的隐性意图。")

with st.sidebar:
    st.header("🔑 配置大模型")
    api_key = st.text_input("API Key", type="password")
    base_url = st.text_input("Base URL", value="https://api.deepseek.com/v1")
    
    st.markdown("---")
    total_quotes = sum([len(v) for v in db.values()])
    st.success(f"📜 宗人府名册簿：\n\n- 记录在案小主：**{len(db)}** 位\n- 摘录起居注台词：**{total_quotes}** 句")

# ==== 绝杀交互设计：双层级联菜单 + 动态人物区 ====
# 我们把页面分成 3 列，中间放下拉菜单，右边放悬浮动画小人
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
    # 动态获取当前选中人物的专属头像，并挂载 CSS 动画 class
    current_avatar = AVATAR_MAP.get(selected_char, "👤")
    st.markdown(f'<div class="avatar-container">{current_avatar}</div>', unsafe_allow_html=True)

# 提供一个文本框，把选中的台词放进去，允许用户在这个基础上删改
current_quote = st.text_area("✍️ 最终要分析的台词文本（支持手动修改/输入）：", value=final_quote, height=100)

if st.button("🚀 启动潜台词深度挖掘"):
    if not api_key:
        st.warning("⚠️ 请先在左侧输入 API Key！")
    elif not current_quote:
        st.warning("⚠️ 台词不能为空！")
    else:
        with st.spinner(f"🔮 正在请神机妙算的大模型解析【{selected_char}】的心机..."):
            result = analyze_subtext(selected_char, current_quote, api_key, base_url)
            
            # 挖出结果后，撒一波雪花特效（呼应剧中纯元皇后的梅花雪景）
            st.snow() 
            
            st.markdown("---")
            st.success("✅ 军机处密报：挖掘完成！")
            st.markdown(result)
