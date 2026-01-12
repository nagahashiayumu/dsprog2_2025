import flet as ft
import requests
import sqlite3
from datetime import datetime

# --- データベース管理クラス ---
class WeatherDB:
    def __init__(self, db_name="weather_app.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        """テーブルの作成"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # エリアテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS areas (
                    code TEXT PRIMARY KEY,
                    name TEXT
                )
            """)
            # 予報テーブル (target_date と area_code で一意にする)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS forecasts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    area_code TEXT,
                    target_date TEXT,
                    weather_name TEXT,
                    weather_code TEXT,
                    created_at DATETIME,
                    UNIQUE(area_code, target_date),
                    FOREIGN KEY (area_code) REFERENCES areas (code)
                )
            """)
            conn.commit()

    def save_areas(self, area_dict):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for code, info in area_dict.items():
                cursor.execute("INSERT OR IGNORE INTO areas (code, name) VALUES (?, ?)", (code, info["name"]))
            conn.commit()

    def save_forecast(self, area_code, target_date, weather_name, weather_code):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # UPSERT (既にある日付なら更新、なければ挿入)
            cursor.execute("""
                INSERT INTO forecasts (area_code, target_date, weather_name, weather_code, created_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(area_code, target_date) DO UPDATE SET
                    weather_name=excluded.weather_name,
                    weather_code=excluded.weather_code,
                    created_at=excluded.created_at
            """, (area_code, target_date, weather_name, weather_code, datetime.now()))
            conn.commit()

    def get_areas_from_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT code, name FROM areas")
            return cursor.fetchall()

    def get_forecasts_from_db(self, area_code):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # 過去のデータも含めて日付順に取得
            cursor.execute("""
                SELECT target_date, weather_name, weather_code 
                FROM forecasts WHERE area_code = ? 
                ORDER BY target_date DESC
            """, (area_code,))
            return cursor.fetchall()

# --- メインアプリケーション ---
def main(page: ft.Page):
    page.title = "DB連動型・天気予報アプリ"
    page.bgcolor = "#F5F5F5"
    db = WeatherDB()

    # --- 初期データ投入 (APIからエリア取得) ---
    def load_initial_data():
        try:
            res = requests.get("https://www.jma.go.jp/bosai/common/const/area.json")
            offices = res.json().get("offices", {})
            db.save_areas(offices)
        except:
            print("オフラインモードで起動します")

    load_initial_data()

    # --- UI要素 ---
    weather_list = ft.ListView(expand=True, spacing=10, padding=10)
    
    def update_display(area_code):
        """DBからデータを読み取って表示"""
        weather_list.controls.clear()
        rows = db.get_forecasts_from_db(area_code)
        
        for date, name, code in rows:
            weather_list.controls.append(
                ft.ListTile(
                    leading=ft.Image(src=f"https://www.jma.go.jp/bosai/forecast/img/{code}.png", width=40),
                    title=ft.Text(f"{date} の予報"),
                    subtitle=ft.Text(name),
                    tile_color=ft.Colors.WHITE,
                )
            )
        page.update()

    def on_fetch_click(e):
        """APIから最新情報を取得し、DBに保存してから表示を更新"""
        area_code = region_dropdown.value
        if not area_code: return

        try:
            res = requests.get(f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json")
            data = res.json()
            time_series = data[0]["timeSeries"][0]
            times = time_series["timeDefines"]
            area_data = time_series["areas"][0]

            for i in range(len(times)):
                dt = datetime.fromisoformat(times[i]).strftime("%Y-%m-%d")
                db.save_forecast(area_code, dt, area_data["weathers"][i], area_data["weatherCodes"][i])
            
            update_display(area_code)
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text("データの取得に失敗しました"))
            page.snack_bar.open = True
            page.update()

    # プルダウンの作成
    areas = db.get_areas_from_db()
    region_dropdown = ft.Dropdown(
        label="地域を選択",
        options=[ft.dropdown.Option(code, name) for code, name in areas],
        on_change=lambda _: update_display(region_dropdown.value),
        expand=True
    )

    # レイアウト
    page.add(
        ft.Column([
            ft.Row([
                region_dropdown,
                ft.ElevatedButton("最新情報を取得", on_click=on_fetch_click, icon=ft.Icons.REFRESH)
            ]),
            ft.Text("予報履歴 (DBに保存されたデータ):", weight="bold"),
            weather_list
        ], expand=True)
    )

ft.app(target=main)