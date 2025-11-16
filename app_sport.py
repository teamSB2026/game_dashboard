import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from streamlit_autorefresh import st_autorefresh
import altair as alt
import streamlit.components.v1 as components

# -----------------------
# 設定（調整ポイント）
# -----------------------
COMPONENT_HEIGHT = 1000
ROW_HEIGHT_PX = 18
FONT_SIZE_PX = 12
CELL_PADDING_V = 4
CELL_PADDING_H = 2
COLUMN_WIDTH_PX = 140
FIRST_COL_WIDTH_PX = 100
# -----------------------

# 🎨 共通 CSS
st.markdown(f"""
<style>
body {{ background: #f0faff; }}
.header-title {{ font-size:36px; font-weight:900; text-align:center; color:#1e88e5; margin:10px 0 4px 0; font-family:"Trebuchet MS",sans-serif; text-shadow:1px 2px #b3e5fc; }}
.sub-text {{ text-align:center; font-size:18px; margin-bottom:12px; color:#555; }}
.drink-card {{ border-radius:12px; background:#ffffffcc; backdrop-filter: blur(6px); padding:12px; margin-top:14px; box-shadow:0 4px 10px rgba(130,200,255,0.25); }}
.compact-table {{
  border-collapse: collapse;
  width:100%;
  table-layout: fixed;
  font-size:{FONT_SIZE_PX}px;
  font-family: "Helvetica Neue", Arial, sans-serif;
  border: 1px solid rgba(0,0,0,0.06);
}}
.compact-table th {{
  position: sticky;
  top:0;
  background: rgba(255,255,255,0.95);
  z-index:2;
  font-weight:700;
  padding:{CELL_PADDING_V}px {CELL_PADDING_H}px;
  white-space: nowrap;
  overflow:hidden;
  text-overflow:ellipsis;
  border-bottom:1px solid rgba(0,0,0,0.06);
}}
.compact-table tr {{ height: {ROW_HEIGHT_PX}px; }}
.compact-table td {{
  padding:{CELL_PADDING_V}px {CELL_PADDING_H}px;
  overflow:hidden;
  text-overflow:ellipsis;
  white-space: nowrap;
  vertical-align:middle;
  border-bottom:1px solid rgba(0,0,0,0.03);
}}
.compact-table tbody tr:hover {{ background: rgba(224,247,250,0.6); }}
</style>
""", unsafe_allow_html=True)

# 🔄 自動リフレッシュ（デモ用）
st_autorefresh(interval=3 * 1000, key="refresh_demo")

# ヘッダー画像（任意）
assets_dir = Path(__file__).resolve().parent / "assets"
header_path = assets_dir / "header.png"
if header_path.exists():
    st.image(str(header_path), width="stretch")

# タイトル
st.markdown("<h1 class='header-title'>🥤 第１問 利きスポドリ 💧</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-text'>💪 さあみんなどれがどれだかわかったかな？ 💪</p>", unsafe_allow_html=True)

# -----------------------
# CSVデータ読み込み
# -----------------------
drink_choices = ['ポカリ', 'アクエリ', 'だから', 'キリンラブスポーツ']
drink_colors = {
    'ポカリ': "#4fa6ff",
    'アクエリ': "#0077cc",
    'だから': "#76c893",
    'キリンラブスポーツ': "#f6d743"
}
bg_map = {"ピンク": "#fc81ac", "ブルー": "#5ddaf0", "グリーン": "#72C045", "レッド": "#d92c06"}

# Google Sheetsから読み込み
# スプレッドシートID: 1OwPUg1eGwF41LlNaZ9RKpnBEL748Ui8vINBCPobzML8
# シートID: 985675602
SHEET_ID = "1OwPUg1eGwF41LlNaZ9RKpnBEL748Ui8vINBCPobzML8"
GID = "985675602"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

try:
    # Google SheetsからCSV形式でデータを読み込み
    df_raw = pd.read_csv(SHEET_URL)
    # CSVの「班」列を「回答者」として使用（「班」を付ける）
    df = pd.DataFrame({
        "回答者": [f"{ban}班" for ban in df_raw['班'].values],
        "ピンク": df_raw['回答 [ピンク]'].values,
        "ブルー": df_raw['回答 [ブルー]'].values,
        "グリーン": df_raw['回答 [グリーン]'].values,
        "レッド": df_raw['回答 [レッド]'].values,
    })
    print(df)
    # 重複した班がある場合は最新の回答を残す
    df = df.drop_duplicates(subset=['回答者'], keep='last').reset_index(drop=True)
    # 班番号でソート（数値順）
    df = df.sort_values('回答者', key=lambda x: x.str.replace('班', '').astype(int)).reset_index(drop=True)
    print(df)
except Exception as e:
    # 読み込みに失敗した場合はダミーデータ
    st.warning(f"Google Sheetsからの読み込みに失敗しました: {e}")
    assignments = [np.random.choice(drink_choices, size=4, replace=False) for _ in range(32)]
    df = pd.DataFrame({
        "回答者": [f'{i}班' for i in range(1, 33)],
        "ピンク": [a[0] for a in assignments],
        "ブルー": [a[1] for a in assignments],
        "グリーン": [a[2] for a in assignments],
        "レッド": [a[3] for a in assignments],
    })

# -----------------------
# Pivotテーブル（ドリンク別・色表示）
# -----------------------
df_pivot = pd.DataFrame({'回答者': df['回答者']})
for drink in drink_choices:
    color_list = []
    for i in range(len(df)):
        matched_colors = []
        for color in ['ピンク', 'ブルー', 'グリーン', 'レッド']:
            if df.loc[i, color] == drink:
                matched_colors.append(color)
        color_list.append('・'.join(matched_colors) if matched_colors else '')
    df_pivot[drink] = color_list

# -----------------------
# HTMLテーブル生成（塗りつぶしセル）
# -----------------------
def df_to_colored_html_with_colgroup(df, first_col_w=FIRST_COL_WIDTH_PX, col_w=COLUMN_WIDTH_PX):
    html = "<table class='compact-table'>"
    html += "<colgroup>"
    html += f"<col style='width:{first_col_w}px' />"
    for _ in range(4):
        html += f"<col style='width:{col_w}px' />"
    html += "</colgroup><thead><tr>"
    for col in df.columns:
        html += f"<th>{col}</th>"
    html += "</tr></thead><tbody>"
    for _, row in df.iterrows():
        html += "<tr>"
        for col in df.columns:
            val = row[col]
            if col == "回答者":
                html += f"<td>{val}</td>"
            else:
                if val == "":
                    html += "<td></td>"
                else:
                    colors = val.split("・")
                    bg_colors = [bg_map[c] for c in colors if c in bg_map]
                    gradient = ", ".join(bg_colors)
                    bg_style = f"background: linear-gradient(90deg, {gradient});"
                    html += f"<td style='{bg_style} height:{ROW_HEIGHT_PX}px;'></td>"
        html += "</tr>"
    html += "</tbody></table>"
    return html

def render_compact_table(df, component_height=COMPONENT_HEIGHT):
    html_table = df_to_colored_html_with_colgroup(df)
    wrapper = f"<div class='compact-wrapper'>{html_table}</div>"
    components.html(wrapper, height=component_height, scrolling=False)

# -----------------------
# 棒グラフ生成関数（ドリンクごとに1つ）
# -----------------------
def make_chart_for_drink(df, drink_name):
    melted = df.melt(id_vars='回答者', value_vars=['ピンク','ブルー','グリーン','レッド'],
                     var_name='色', value_name='ドリンク')
    chart_data = melted[melted['ドリンク'] == drink_name]
    counts = chart_data['色'].value_counts().reset_index()
    counts.columns = ['色', '票数']

    max_votes = counts['票数'].max()

    chart = (
        alt.Chart(counts)
        .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
        .encode(
            x=alt.X('色:N', sort=['ピンク','ブルー','グリーン','レッド'], title=None),
            y=alt.Y('票数:Q', scale=alt.Scale(domain=[0, max_votes * 1.25])),
            color=alt.Color('色:N',
                            scale=alt.Scale(domain=list(bg_map.keys()), range=list(bg_map.values())),
                            legend=None),
            tooltip=['色', '票数']
        )
        .properties(title=drink_name, height=400)
    )
    return chart

# -----------------------
# レイアウト
# -----------------------
col1, col2 = st.columns([1.2, 2.3])

with col1:
    st.markdown("<div class='drink-card'>", unsafe_allow_html=True)
    st.write("🧾 集計結果")
    render_compact_table(df_pivot)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='drink-card'>", unsafe_allow_html=True)
    st.write("🥤 利き集計結果（ドリンクごと）")

    sub1, sub2 = st.columns(2)
    with sub1:
        st.altair_chart(make_chart_for_drink(df, 'ポカリ'), use_container_width=True)
        st.altair_chart(make_chart_for_drink(df, 'だから'), use_container_width=True)
    with sub2:
        st.altair_chart(make_chart_for_drink(df, 'アクエリ'), use_container_width=True)
        st.altair_chart(make_chart_for_drink(df, 'キリンラブスポーツ'), use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------
# フッター
# -----------------------
st.success("🌟 デモのため3秒おきにページを自動更新します 🌟")
st.markdown("<p style='text-align:center;color:#888;font-size:12px;'>© Bridge 2025 利きスポドリゲーム</p>", unsafe_allow_html=True)
