import flet as ft
import requests
from datetime import datetime

class WeatherApp:
    def __init__(self):
        self.api_base = "https://www.jma.go.jp/bosai/forecast/data/forecast"
        self.area_url = "https://www.jma.go.jp/bosai/common/const/area.json"
        self.icon_base = "https://www.jma.go.jp/bosai/forecast/img"

    def get_offices(self):
        """府県単位のリストを取得（class10sより選択しやすいため）"""
        res = requests.get(self.area_url)
        return res.json().get("offices", {})

    def get_weather(self, code):
        """詳細な予報データを取得"""
        res = requests.get(f"{self.api_base}/{code}.json")
        return res.json()

def main(page: ft.Page):
    page.title = "Modern Weather App"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.bgcolor = "#F0F2F5"
    
    app_logic = WeatherApp()

    # --- UI Elements ---
    title_text = ft.Text("天気予報", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
    
    # 天気カードを並べるコンテナ
    weather_grid = ft.Row(wrap=True, spacing=20, alignment=ft.MainAxisAlignment.START)
    
    loading_indicator = ft.ProgressBar(visible=False, color=ft.Colors.BLUE_700)

    def on_region_changed(e):
        """地域変更時の処理"""
        loading_indicator.visible = True
        weather_grid.controls.clear()
        page.update()

        try:
            area_code = e.control.value
            data = app_logic.get_weather(area_code)
            
            # データの解析 (最初のエリアの予報を抽出)
            time_series = data[0]["timeSeries"][0]
            times = time_series["timeDefines"]
            area_data = time_series["areas"][0]
            
            weathers = area_data["weathers"]
            codes = area_data["weatherCodes"]

            for i in range(len(weathers)):
                # 日付のパース
                dt = datetime.fromisoformat(times[i])
                date_str = dt.strftime("%m/%d(%a)")
                
                # カードの作成
                weather_grid.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(date_str, weight=ft.FontWeight.W_500),
                                    ft.Image(
                                        src=f"{app_logic.icon_base}/{codes[i]}.png",
                                        width=50, height=50,
                                    ),
                                    ft.Text(
                                        weathers[i], 
                                        size=12, 
                                        text_align=ft.TextAlign.CENTER,
                                        max_lines=2,
                                        overflow=ft.TextOverflow.ELLIPSIS
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=10,
                            ),
                            padding=15,
                            width=140,
                        ),
                        elevation=2,
                    )
                )
        except Exception as ex:
            print(f"Error: {ex}")
            weather_grid.controls.append(ft.Text("データの取得に失敗しました。"))
        
        loading_indicator.visible = False
        page.update()

    # ドロップダウンの設定
    offices = app_logic.get_offices()
    region_dropdown = ft.Dropdown(
        label="都道府県を選択",
        options=[ft.dropdown.Option(k, v["name"]) for k, v in offices.items()],
        on_change=on_region_changed,
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        width=300,
    )

    # --- Layout ---
    page.add(
        ft.Column(
            [
                ft.Row([ft.Icon(ft.Icons.WB_SUNNY, color="orange"), title_text]),
                ft.Divider(height=10, color="transparent"),
                region_dropdown,
                loading_indicator,
                ft.Divider(height=20),
                weather_grid
            ],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
        )
    )

if __name__ == "__main__":
    ft.app(target=main)