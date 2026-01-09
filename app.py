import streamlit as st
import google.generativeai as genai
import time

# ==========================================
# 1. 頁面配置 (Page Config)
# ==========================================
st.set_page_config(
    page_title="Infographic Wizard - Lite",
    page_icon="🧙‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化 Session State
if "generated_prompts" not in st.session_state:
    st.session_state.generated_prompts = []

# ==========================================
# 2. 資料庫：Lite 專屬設計庫
# ==========================================
STYLES = {
    # --- ✨ Trending / 流行潮玩區 ---
    "S01": {"name": "🧸 盲盒公仔 (Blind Box 3D)", "desc": "C4D 質感、可愛角色、柔和打光", "vibe": "Fun"},
    "S02": {"name": "☁️ 軟萌黏土 (Claymorphism)", "desc": "蓬鬆、像棉花糖般的 UI 介面", "vibe": "Fun"},
    "S03": {"name": "👾 8-Bit 像素 (Retro Pixel)", "desc": "復古電玩風、顆粒感、鮮豔色彩", "vibe": "Fun"},
    "S04": {"name": "💥 美式波普 (Pop Art Comic)", "desc": "漫畫分鏡、對話框、大膽撞色", "vibe": "Fun"},
    "S05": {"name": "💿 全像雷射 (Holographic)", "desc": "Y2K 風格、流體金屬、雷射貼紙質感", "vibe": "Fun"},
    "S06": {"name": "🛹 貼紙塗鴉 (Sticker Bomb)", "desc": "街頭潮流、筆電背蓋貼滿貼紙的混亂美", "vibe": "Fun"},
    "S07": {"name": "✏️ 手繪筆記 (Doodle Notebook)", "desc": "咖啡廳手帳感、親切的手繪草圖", "vibe": "Fun"},
    "S08": {"name": "🌃 霓虹賽博 (Neon Cyber)", "desc": "發光管線、夜店風、暗黑科技感", "vibe": "Fun"},
    "S09": {"name": "✂️ 紙藝立體 (Paper Cutout)", "desc": "層層堆疊的剪紙陰影、童話感", "vibe": "Fun"},
    # --- 💼 Classic / 經典商務區 ---
    "S10": {"name": "🎨 多彩曼非斯 (Colorful Memphis)", "desc": "幾何圖形、活潑但不過度", "vibe": "Biz"},
    "S11": {"name": "🔷 扁平插畫 (Flat Illustration)", "desc": "企業通用、乾淨、好理解", "vibe": "Biz"},
    "S12": {"name": "🏢 商務極簡 (Business Minimal)", "desc": "大量留白、細線條、信任感", "vibe": "Biz"},
    "S13": {"name": "🖍️ 黑板粉筆 (Chalkboard Sketch)", "desc": "教學解說、知識感", "vibe": "Biz"},
}

LAYOUTS = {
    # --- 🎮 Easy / 直觀隱喻區 ---
    "L01": {"name": "💬 手機對話串 (Chat Message)", "desc": "用通訊軟體對話框呈現問答", "cat": "Easy"},
    "L02": {"name": "🍱 便當盒網格 (Bento Grid)", "desc": "Apple 風格、模組化卡片總覽", "cat": "Easy"},
    "L03": {"name": "🏰 遊戲闖關圖 (Game Level Map)", "desc": "起點到終點、關卡式步驟流程", "cat": "Easy"},
    "L04": {"name": "🥊 對戰擂台 (VS Battle Arena)", "desc": "左右 PK、格鬥遊戲血條風格", "cat": "Easy"},
    "L05": {"name": "🧊 冰山全貌 (Iceberg Model)", "desc": "水面下隱藏的真相、迷因梗圖結構", "cat": "Easy"},
    "L06": {"name": "🏙️ 微縮城市 (Isometric City)", "desc": "2.5D 上帝視角、生態系全覽", "cat": "Easy"},
    "L07": {"name": "🪐 行星軌道 (Solar System)", "desc": "核心恆星吸引周圍衛星、動態發散", "cat": "Easy"},
    "L08": {"name": "🚇 地鐵路網 (Subway Map)", "desc": "複雜的決策路徑或專案時程", "cat": "Easy"},
    # --- 📊 Formal / 正式邏輯區 ---
    "L09": {"name": "🃏 卡片輪播 (Card Carousel)", "desc": "IG 多圖連播 (自動生成 3~4 張連貫圖卡)", "cat": "Biz"},
    "L10": {"name": "🔺 層級金字塔 (Pyramid)", "desc": "由下而上的階層架構 (如馬斯洛)", "cat": "Biz"},
    "L11": {"name": "🎯 中心對焦 (Center Focus)", "desc": "傳統核心強調、向外輻射", "cat": "Biz"},
    "L12": {"name": "🐍 蛇形流程 (Serpentine Flow)", "desc": "傳統 S 型時間軸", "cat": "Biz"},
}

FRAMES = {
    "A": {"name": "📱 社群貼文 (1:1 Square)", "prompt": "1:1 square aspect ratio, social media post"},
    "B": {"name": "🤳 手機滿版 (9:16 Vertical)", "prompt": "9:16 vertical aspect ratio, mobile wallpaper style, continuous vertical scrolling composition"},
    "C": {"name": "💻 寬螢幕簡報 (16:9 Wide)", "prompt": "16:9 aspect ratio, presentation slide"},
    "D": {"name": "🎞️ 電影寬幅 (21:9 Cinematic)", "prompt": "21:9 ultrawide aspect ratio, cinematic shot"}
}

# ==========================================
# 3. 側邊欄：動態雷達
# ==========================================
with st.sidebar:
    st.title("⚙️ 設定 (Settings)")
    api_key = st.text_input("Google Gemini API Key", type="password")
    
    selected_model_name = None
    
    if api_key:
        st.divider()
        st.subheader("📡 模型雷達 (Model Radar)")
        try:
            genai.configure(api_key=api_key)
            available_models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
            
            if available_models:
                priority_models = [m for m in available_models if "flash" in m or "exp" in m]
                other_models = [m for m in available_models if m not in priority_models]
                sorted_models = priority_models + other_models

                selected_model_name = st.selectbox(
                    "✅ 偵測到您的可用引擎：",
                    sorted_models,
                    index=0
                )
                st.caption(f"目前引擎：{selected_model_name}")
                
                if "gemini-2.5" in selected_model_name or "exp" in selected_model_name:
                    st.success("🚀 已啟動高速實驗引擎 (High Speed)")
                else:
                    st.info("🐢 已啟動標準穩定引擎 (Standard)")
            else:
                st.error("⚠️ 您的 Key 下沒有找到可用模型。")
        except Exception as e:
            st.error(f"連線失敗: {e}")

    st.divider()
    st.markdown("### 🧙‍♂️ About Wizard - Lite")
    st.caption("Version: v12.3 (Final Wording)")
    st.info("Make Info Fun Again! \n讓資訊變好玩！")

# ==========================================
# 4. 主介面：遊戲化引導
# ==========================================
st.title("🧙‍♂️ Infographic Wizard - Lite")
st.markdown("### 您的 AI 資訊圖表 咒語法師 ✨")

# --- Step 1 ---
st.subheader("Step 1: 選擇冒險模式 (Adventure Mode)")
mode = st.radio(
    "準備好開始了嗎？",
    [
        "Mode 1: 🎲 懶人全自動 (I feel lucky)",
        "Mode 2: 🗺️ 手把手引導 (Interactive Guide) [推薦]",
        "Mode 3: 👻 資訊圖底稿 (Phantom Layout) [無字]"
    ],
    index=1
)

if "Mode 1" in mode:
    st.info("💡 **Wizard Tip:** 沒靈感？交給我！只要給我主題，風格我幫你擲🎲")
elif "Mode 2" in mode:
    st.success("💡 **Wizard Tip:** 這是最棒的選擇！🗺️我問你答，咒語會圖文相符。")
elif "Mode 3" in mode:
    st.warning("💡 **Wizard Tip:** 啟動「幽靈佈局」👻！我只給視覺框架，絕不寫錯字，方便你後製創作。")

# --- Step 2 ---
st.subheader("Step 2: 畫布尺寸 (Canvas)")
frame_code = st.selectbox(
    "要在哪裡發布？",
    options=list(FRAMES.keys()),
    format_func=lambda x: f"{FRAMES[x]['name']}"
)
if frame_code == "B":
    st.toast("🔥 已啟動「長圖模式」，將生成垂直滾動視覺！")

# --- Step 3 & 4 ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Step 3: 視覺風格 (Vibe)")
    style_code = st.selectbox(
        "選擇一種氛圍：",
        options=list(STYLES.keys()),
        format_func=lambda x: f"{STYLES[x]['name']}"
    )
    if STYLES[style_code]['vibe'] == "Fun":
        st.caption(f"🔥 **Hot Tip:** {STYLES[style_code]['desc']} (IG 吸睛度高！)")
    else:
        st.caption(f"💼 **Pro Tip:** {STYLES[style_code]['desc']} (老闆會喜歡的安全牌。)")

with col2:
    st.subheader("Step 4: 結構佈局 (Structure)")
    layout_code = st.selectbox(
        "選擇如何呈現：",
        options=list(LAYOUTS.keys()),
        format_func=lambda x: f"{LAYOUTS[x]['name']}"
    )
    if layout_code == "L09":
        st.info(f"✨ **Wow Feature:** 您選擇了卡片輪播！若是**長文內容**，我將自動拆分為 **3~4 頁** 連貫圖卡 (封面-內容-結尾)，一次搞定！")
    else:
        st.caption(f"📐 **Layout Tip:** {LAYOUTS[layout_code]['desc']}")

# --- Step 5 ---
st.divider()
st.subheader("Step 5: 內容注入 (Content Magic)")

user_topic = ""
user_points = ""
user_conclusion = ""
phantom_count = 0

if "Mode 1" in mode:
    user_topic = st.text_input("🔮 請輸入主題 (Topic)", placeholder="例如：為什麼貓咪喜歡紙箱？")
    
elif "Mode 2" in mode or "Mode 3" in mode:
    col_a, col_b = st.columns([1, 2])
    with col_a:
        user_topic = st.text_input("1. 核心標題 (Title)", placeholder="例如：2026 AI 趨勢")
    with col_b:
        user_conclusion = st.text_input("3. 一句話結論 (Conclusion)", placeholder="例如：人機協作是未來")
    
    user_points = st.text_area(
        "2. 關鍵重點 (Key Points)", 
        placeholder="請按 Enter 換行，一行一個重點。\n(支援長文輸入！若超過 3 行重點，且選擇「卡片輪播」，我會自動幫您拆成多頁顯示喔！)",
        height=250 
    )

    if "Mode 3" in mode and user_points:
        phantom_count = len([line for line in user_points.split('\n') if line.strip()])
        st.toast(f"👻 偵測到 {phantom_count} 個重點，將生成對應的空白容器！")

# ==========================================
# 5. 生成邏輯 (Combo Magic)
# ==========================================
generate_btn = st.button("✨ 施展魔法 (Cast Spell)", type="primary", use_container_width=True)

if generate_btn:
    if not api_key:
        st.error("請先在側邊欄輸入 API Key！")
    elif not selected_model_name:
        st.error("正在連線模型雷達，請稍候...")
    else:
        status = st.status("🧙‍♂️ Wizard 正在施咒...", expanded=True)
        st.session_state.generated_prompts = [] 
        
        try:
            # Phase 1: Config
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(selected_model_name)
            
            # Phase 2: Prompt Construction
            frame_prompt = FRAMES[frame_code]['prompt']
            style_prompt = f"{STYLES[style_code]['name']} style, {STYLES[style_code]['desc']}, vibrant colors, high quality 8k render"
            
            is_carousel = (layout_code == "L09")
            
            tasks = []
            if is_carousel:
                status.write("✨ 啟動「卡片輪播」特效：正在計算分頁...")
                
                # --- Slide 1: 封面 ---
                tasks.append({
                    "name": "Slide 1: 封面 (Cover)",
                    "content": f"Title Slide. Big Typography: '{user_topic}'. Central Hero Image / Key Visual representing the topic. High impact composition."
                })
                
                # --- Slide 2: 內容 (Content Split Logic) ---
                points_list = [p for p in user_points.split('\n') if p.strip()]
                
                if len(points_list) > 3:
                    mid = (len(points_list) + 1) // 2
                    part1 = points_list[:mid]
                    part2 = points_list[mid:]
                    
                    tasks.append({
                        "name": "Slide 2-1: 內容 A (Content Part A)",
                        "content": f"Carousel Slide 2 of 4. Content Part A. Visual list: {part1}. Balanced layout."
                    })
                    tasks.append({
                        "name": "Slide 2-2: 內容 B (Content Part B)",
                        "content": f"Carousel Slide 3 of 4. Content Part B. Visual list: {part2}. Consistent layout with Part A."
                    })
                else:
                    tasks.append({
                        "name": "Slide 2: 內容 (Content)",
                        "content": f"Carousel Slide 2 of 3. Content Slide. Visual list/grid of points: '{user_points}'. Clean layout."
                    })
                
                # --- Slide 3: 結尾 ---
                last_slide_num = "4" if len(points_list) > 3 else "3"
                tasks.append({
                    "name": "Slide 3: 結尾 (Ending)",
                    "content": f"Carousel Slide {last_slide_num} of {last_slide_num}. Conclusion Slide. Impactful Visual Metaphor combined with text: '{user_conclusion}'. Call to Action vibe."
                })
                
            else:
                # 一般單張圖
                status.write("🔍 正在解析結構 (Analyzing Structure)...")
                tasks.append({
                    "name": "Single Image",
                    "content": f"Title: '{user_topic}'. Points: '{user_points}'. Conclusion: '{user_conclusion}'. Central Hero Image integrated with data points."
                })

            # --- 迴圈執行生成 ---
            for i, task in enumerate(tasks):
                status.write(f"🎨 正在繪製：{task['name']}...")
                
                anti_clutter = "Summarize text into visual keywords. Avoid clutter. Ensure text legibility."
                
                if "Mode 3" in mode:
                    content_instruction = f"PHANTOM LAYOUT: Create empty frames for content. NO TEXT. Context: {task['content']}"
                else:
                    content_instruction = f"VISUALIZE: {task['content']}. {anti_clutter}"

                layout_desc = LAYOUTS[layout_code]['desc']
                if is_carousel: 
                    layout_desc = "Unified social media carousel slide design, maintaining visual consistency across slides"

                meta_prompt = f"""
                Act as an expert Prompt Engineer for DALL-E 3 and Gemini.
                Target: Social Media Infographic.
                
                Specs:
                - Frame: {frame_prompt}
                - Style: {style_prompt}
                - Layout: {layout_desc}
                - specific Task: {task['name']}
                
                Content: {content_instruction}
                
                Output ONLY the prompt text inside a code block.
                """
                
                response = model.generate_content(meta_prompt)
                final_prompt = response.text.replace("```text", "").replace("```json", "").replace("```", "").strip()
                st.session_state.generated_prompts.append({"title": task['name'], "prompt": final_prompt})
                time.sleep(1)

            status.update(label="🎉 魔法完成！ (Complete!)", state="complete", expanded=False)
            st.balloons()

        except Exception as e:
            status.update(label="❌ 施法失敗 (Failed)", state="error")
            st.error(f"錯誤訊息: {e}")

# ==========================================
# 6. 結果顯示
# ==========================================
if st.session_state.generated_prompts:
    st.divider()
    st.subheader("🎉 您的專屬咒語 (Your Prompts)")
    st.info("👇 複製下方咒語，貼到 ChatGPT (DALL-E 3) 或 Gemini")

    for item in st.session_state.generated_prompts:
        with st.container(border=True):
            st.markdown(f"**📌 {item['title']}**")
            st.code(item['prompt'], language="text")

    with st.expander("🤔 為什麼不用 Midjourney？"):
        st.markdown("""
        * **ChatGPT / Gemini:** 相對看得懂繁體中文，適合有圖有文的需求。BUT…但是...AI 對繁體中文的辨識不足...仍是硬傷啊~~~😥
        * **Midjourney:** 畫圖超美，但基本上是繁體中文文盲🤣。如果您只想要「純底圖」請選「Mode 3」，還是可以用 Midjourney！
        """)