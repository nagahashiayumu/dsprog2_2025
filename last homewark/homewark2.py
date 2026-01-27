import flet as ft
import pandas as pd
import requests
import time
import sqlite3

# --- 設定 ---
EXCEL_URL = "https://www.mlit.go.jp/kankocho/content/001750679.xlsx"
DB_NAME = "tourism_analysis.db"

# --- データ取得・保存ロジック (課題 Step2 [cite: 10]) ---
def setup_database():
    """分析用DBの作成 [cite: 33, 41]"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tourism_stats (
            pref_name TEXT PRIMARY KEY,
            jp_users REAL,
            intl_users REAL,
            inbound_ratio REAL
        )
    ''')
    conn.commit()
    conn.close()

def fetch_and_store_data():
    """スクレイピングに相当するデータ取得と保存 [cite: 19, 33, 37]"""
    print("データ取得中...")
    time.sleep(1) # サーバ負荷に配慮 [cite: 37]
    
    excel_file = pd.ExcelFile(EXCEL_URL)
    target_sheet = [s for s in excel_file.sheet_names if '第2表' in s][0]
    df_clean = pd.read_excel(EXCEL_URL, sheet_name=target_sheet, header=9)

    # 必要な列を抽出して掃除
    df = df_clean.iloc[:, [1, 2, 3]].copy()
    df.columns = ['pref', 'jp', 'intl']
    df['jp'] = pd.to_numeric(df['jp'], errors='coerce')
    df['intl'] = pd.to_numeric(df['intl'], errors='coerce')
    df = df.dropna().head(47)

    # 都道府県名の割り当てと比率計算
    prefectures = ["北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県", "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県", "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]
    df['pref'] = prefectures
    df['ratio'] = (df['intl'] / (df['jp'] + df['intl'])) * 100

    conn = sqlite3.connect(DB_NAME)
    # DBに格納 [cite: 33]
    df.to_sql('tourism_stats', conn, if_exists='replace', index=False)
    conn.close()
    return df

# --- UIコンポーネント (可視化 [cite: 39]) ---
class StatCard(ft.Card):
    """分析結果を表示するカード"""
    def __init__(self, pref, jp, ratio):
        super().__init__()
        self.content = ft.Container(
            content=ft.Column([
                ft.Text(pref, size=16, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("日本人宿泊者", size=12, color=ft.Colors.GREY_700),
                ft.Text(f"{int(jp):,}人", size=14, color=ft.Colors.BLUE_700, weight=ft.FontWeight.W_500),
                ft.Text("インバウンド比率", size=12, color=ft.Colors.GREY_700),
                ft.Text(f"{ratio:.1f}%", size=18, color=ft.Colors.RED_600, weight=ft.FontWeight.BOLD),
            ], spacing=5, alignment=ft.MainAxisAlignment.CENTER),
            width=160, height=200, padding=15, bgcolor=ft.Colors.WHITE, border_radius=12
        )

def main(page: ft.Page):
    page.title = "観光統計分析アプリ"
    page.padding = 0
    page.bgcolor = "#B0BEC5" 

    # ヘッダー (すべての ft.Icons を ft.Icons に変更)
    header = ft.Container(
        content=ft.Row([
            ft.Text("観光統計分析 - 宿泊旅行統計調査", color=ft.Colors.WHITE, size=20, weight=ft.FontWeight.BOLD),
            ft.Icon(ft.Icons.ANALYTICS, color=ft.Colors.WHITE) # 修正箇所
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        bgcolor="#311B92", padding=15
    )

    # グリッド
    stat_grid = ft.GridView(expand=True, max_extent=200, child_aspect_ratio=0.8, spacing=15, run_spacing=15)

    def load_display(sort_by='ratio'):
        """入力に応じて出力を動的に変化 """
        stat_grid.controls.clear()
        conn = sqlite3.connect(DB_NAME)
        # 構築したDBに対してクエリを発行して取得 
        query = f"SELECT * FROM tourism_stats ORDER BY {sort_by} DESC"
        df = pd.read_sql(query, conn)
        conn.close()

        for _, row in df.iterrows():
            stat_grid.controls.append(StatCard(row['pref'], row['jp'], row['ratio']))
        page.update()

    # サイドバー
    sidebar = ft.Container(
        width=200, bgcolor="#455A64", padding=20,
        content=ft.Column([
            ft.Text("並び替え", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton("インバウンド比率順", on_click=lambda _: load_display('ratio')),
            ft.ElevatedButton("日本人宿泊客数順", on_click=lambda _: load_display('jp')),
        ], spacing=20)
    )

    # 初期化手続き [cite: 7, 8]
    setup_database()
    fetch_and_store_data()
    
    page.add(
        header,
        ft.Row([sidebar, ft.Container(content=stat_grid, expand=True, padding=20)], expand=True)
    )
    load_display()

if __name__ == "__main__":
    ft.app(target=main)