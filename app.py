import streamlit as st
from openai import OpenAI
import json

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
        model="deepseek-chat", # 根据实际使用的模型可修改
        messages=[
            {"role": "system", "content": "你是一个精通清宫职场博弈心理学的 AI 助理，语言风格犀利、幽默且一针见血。"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# ================= 3. 前端展示层 =================
st.set_page_config(page_title="甄嬛传潜台词挖掘机", page_icon="👑", layout="wide")
st.title("👑 甄嬛传“潜台词” NLP 挖掘 Agent")
st.markdown("基于大规模纯文本清洗构建结构化语料库，利用大语言模型剖析后宫职场隐性意图。")

with st.sidebar:
    st.header("🔑 配置大模型")
    api_key = st.text_input("API Key", type="password")
    base_url = st.text_input("Base URL", value="https://api.deepseek.com/v1")
    
    st.markdown("---")
    # 动态统计你刚刚挖出来的总台词数！
    total_quotes = sum([len(v) for v in db.values()])
    st.success(f"📚 当前已挂载结构化角色：**{len(db)}** 位\n\n💬 共计收录精华台词：**{total_quotes}** 句")

# ==== 绝杀交互设计：双层级联菜单 ====
col1, col2 = st.columns([1, 2])

with col1:
    # 第一层：选择提取出的人物名单
    character_list = list(db.keys())
    selected_char = st.selectbox("👤 第 1 步：选择要挖掘的人物", character_list)

with col2:
    # 第二层：根据第一层的人物，动态加载他/她的所有专属台词
    quotes_list = db.get(selected_char, [])
    # 截取台词前20个字作为预览标签，防止下拉菜单太长撑爆屏幕
    quote_preview = {f"“{q[:20]}...”" if len(q)>20 else f"“{q}”": q for q in quotes_list} 
    
    selected_preview = st.selectbox(f"💬 第 2 步：选择【{selected_char}】的经典台词", list(quote_preview.keys()))
    # 拿到完整的真实台词文本
    final_quote = quote_preview.get(selected_preview, "")

# 提供一个文本框，把选中的台词放进去，允许用户在这个基础上删改
current_quote = st.text_area("✍️ 最终要分析的台词文本（支持手动修改/输入）：", value=final_quote, height=100)

if st.button("🚀 启动潜台词深度挖掘"):
    if not api_key:
        st.warning("⚠️ 请先在左侧输入 API Key！")
    elif not current_quote:
        st.warning("⚠️ 台词不能为空！")
    else:
        with st.spinner(f"🧠 正在调用大语言模型解析【{selected_char}】的隐性意图..."):
            result = analyze_subtext(selected_char, current_quote, api_key, base_url)
            st.markdown("---")
            st.success("✅ 挖掘完成！报告如下：")
            st.markdown(result)