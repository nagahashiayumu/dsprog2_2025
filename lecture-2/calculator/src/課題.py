import flet as ft
import math

# --- 拡張ボタンクラス (以前のコードより流用) ---

class CalcButton(ft.ElevatedButton):
    def __init__(self, text, button_clicked, expand=1, color=ft.Colors.WHITE):
        super().__init__()
        self.text = text
        self.expand = expand
        self.on_click = button_clicked
        self.data = text
        self.color = color


class DigitButton(CalcButton):
    def __init__(self, text, button_clicked, expand=1):
        super().__init__(text, button_clicked, expand, color=ft.Colors.WHITE)
        self.bgcolor = ft.Colors.WHITE24


class ActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        super().__init__(text, button_clicked, color=ft.Colors.WHITE)
        self.bgcolor = ft.Colors.ORANGE


class ExtraActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        super().__init__(text, button_clicked, color=ft.Colors.BLACK)
        self.bgcolor = ft.Colors.BLUE_GREY_100

# 新しい科学計算用ボタンのスタイル
class SciButton(CalcButton):
    def __init__(self, text, button_clicked):
        super().__init__(text, button_clicked, color=ft.Colors.WHITE)
        self.bgcolor = ft.Colors.BLUE_GREY_700
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=5),
            padding=ft.padding.all(10)
        )

# --- メインアプリケーションクラス ---

class ScientificCalculatorApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.reset()
        self.is_sci_mode = False  # 科学計算モードのフラグ

        self.result = ft.Text(value="0", color=ft.Colors.WHITE, size=24)
        self.width = 450  # 科学計算キーのために幅を広げる
        self.bgcolor = ft.Colors.BLACK
        self.border_radius = ft.border_radius.all(20)
        self.padding = 20
        
        # 標準キーパッドのレイアウト
        self.standard_keypad = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ExtraActionButton(text="AC", button_clicked=self.button_clicked),
                        ExtraActionButton(text="+/-", button_clicked=self.button_clicked),
                        ExtraActionButton(text="%", button_clicked=self.button_clicked),
                        ActionButton(text="/", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="7", button_clicked=self.button_clicked),
                        DigitButton(text="8", button_clicked=self.button_clicked),
                        DigitButton(text="9", button_clicked=self.button_clicked),
                        ActionButton(text="*", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="4", button_clicked=self.button_clicked),
                        DigitButton(text="5", button_clicked=self.button_clicked),
                        DigitButton(text="6", button_clicked=self.button_clicked),
                        ActionButton(text="-", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="1", button_clicked=self.button_clicked),
                        DigitButton(text="2", button_clicked=self.button_clicked),
                        DigitButton(text="3", button_clicked=self.button_clicked),
                        ActionButton(text="+", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="0", expand=2, button_clicked=self.button_clicked),
                        DigitButton(text=".", button_clicked=self.button_clicked),
                        ActionButton(text="=", button_clicked=self.button_clicked),
                    ]
                ),
            ],
            spacing=10
        )
        
        # 科学計算キーパッドのレイアウト (最低5つ以上のボタン要件を満たす)
        self.sci_keypad = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        SciButton(text="sin", button_clicked=self.button_clicked),
                        SciButton(text="cos", button_clicked=self.button_clicked),
                        SciButton(text="tan", button_clicked=self.button_clicked),
                        SciButton(text="log", button_clicked=self.button_clicked), # 自然対数 ln
                    ]
                ),
                ft.Row(
                    controls=[
                        SciButton(text="x^y", button_clicked=self.button_clicked), # べき乗
                        SciButton(text="sqrt", button_clicked=self.button_clicked), # 平方根
                        SciButton(text="e", button_clicked=self.button_clicked), # ネイピア数
                        SciButton(text="pi", button_clicked=self.button_clicked), # 円周率
                    ]
                ),
            ],
            spacing=10
        )
        
        # メインコンテンツの定義
        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        # モード切替ボタン
                        ExtraActionButton(text="SCI", button_clicked=self.toggle_sci_mode),
                        self.result
                    ],
                    alignment="spaceBetween" # 結果表示とモード切替を両端に配置
                ),
                ft.Row(
                    controls=[
                        self.standard_keypad
                    ],
                    alignment="center",
                )
            ]
        )
        
        # 初期状態では科学計算キーパッドは表示しない
        self.current_keypad_row = self.content.controls[1].controls
        
    def toggle_sci_mode(self, e):
        """科学計算モードと標準モードを切り替える"""
        self.is_sci_mode = not self.is_sci_mode
        
        if self.is_sci_mode:
            # SCIモードON: 科学計算キーパッドを追加
            self.content.controls.insert(1, self.sci_keypad)
            self.content.controls[0].controls[0].text = "STD" # ボタン名をSTDに変更
        else:
            # SCIモードOFF: 科学計算キーパッドを削除
            if len(self.content.controls) > 2:
                self.content.controls.pop(1)
            self.content.controls[0].controls[0].text = "SCI" # ボタン名をSCIに戻す
            
        self.update()

    def button_clicked(self, e):
        data = e.control.data
        print(f"Button clicked with data = {data}")
        
        # エラーリセットまたはAC
        if self.result.value == "Error" or data == "AC":
            self.result.value = "0"
            self.reset()
        
        # --- 数字/小数点入力 ---
        elif data in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "."):
            if self.result.value == "0" or self.new_operand == True:
                self.result.value = data
                self.new_operand = False
            else:
                # 既に小数点があり、再度入力を防ぐ
                if data == "." and "." in self.result.value:
                    pass
                else:
                    self.result.value += data

        # --- 定数入力 (e, pi) ---
        elif data == "e":
            self.result.value = str(self.format_number(math.e))
            self.new_operand = True
        elif data == "pi":
            self.result.value = str(self.format_number(math.pi))
            self.new_operand = True
            
        # --- 単項演算子 (三角関数, log, sqrt, %, +/-, etc.) ---
        elif data in ("sin", "cos", "tan", "log", "sqrt", "%", "+/-"):
            try:
                num = float(self.result.value)
                
                if data == "sin":
                    # Flet/Pythonのmath関数はラジアンを使用するため、度数法を想定して変換
                    self.result.value = self.format_number(math.sin(math.radians(num)))
                elif data == "cos":
                    self.result.value = self.format_number(math.cos(math.radians(num)))
                elif data == "tan":
                    # 90度や270度付近でのエラーを避けるため
                    if abs(math.cos(math.radians(num))) < 1e-9:
                        self.result.value = "Error"
                    else:
                        self.result.value = self.format_number(math.tan(math.radians(num)))
                elif data == "log":
                    # 自然対数 ln
                    if num <= 0:
                        self.result.value = "Error"
                    else:
                        self.result.value = self.format_number(math.log(num))
                elif data == "sqrt":
                    # 平方根
                    if num < 0:
                        self.result.value = "Error"
                    else:
                        self.result.value = self.format_number(math.sqrt(num))
                elif data == "%":
                    self.result.value = self.format_number(num / 100)
                elif data == "+/-":
                    self.result.value = self.format_number(-num)
                    
                self.new_operand = True
                
            except Exception:
                self.result.value = "Error"

        # --- 四則演算/べき乗 (二項演算子) ---
        elif data in ("+", "-", "*", "/", "x^y"):
            try:
                # 前の計算を実行
                current_value = float(self.result.value)
                self.result.value = self.calculate(self.operand1, current_value, self.operator)
                
                # 次の計算のためにオペレーターとオペランドを更新
                self.operator = data
                if self.result.value == "Error":
                    self.operand1 = 0
                else:
                    self.operand1 = float(self.result.value)
                self.new_operand = True
            except ValueError:
                 self.result.value = "Error"

        # --- 実行 (=) ---
        elif data in ("="):
            try:
                self.result.value = self.calculate(self.operand1, float(self.result.value), self.operator)
                self.reset()
            except ValueError:
                self.result.value = "Error"
                self.reset()


        self.update()

    # --- ヘルパーメソッド ---
    
    def format_number(self, num):
        """結果が整数であれば整数で、そうでなければ小数で返す"""
        if isinstance(num, (int, float)) and num == float('inf'):
             return "Error"
        
        # 10桁以上の大きな数値は指数表記で丸める
        if isinstance(num, float) and (abs(num) >= 1e10 or abs(num) < 1e-6 and abs(num) > 0):
            return f"{num:.6e}"

        if num % 1 == 0:
            return int(num)
        else:
            return num

    def calculate(self, operand1, operand2, operator):
        """二項演算子による計算を実行"""
        try:
            if operator == "+":
                return self.format_number(operand1 + operand2)
            elif operator == "-":
                return self.format_number(operand1 - operand2)
            elif operator == "*":
                return self.format_number(operand1 * operand2)
            elif operator == "/":
                if operand2 == 0:
                    return "Error"
                else:
                    return self.format_number(operand1 / operand2)
            elif operator == "x^y":
                 return self.format_number(math.pow(operand1, operand2))
            
            return self.format_number(operand2) # 演算子がない場合は現在の値を返す
            
        except OverflowError:
            return "Error" # 大きすぎる数のエラー

    def reset(self):
        """計算状態を初期化"""
        self.operator = "+"
        self.operand1 = 0
        self.new_operand = True


def main(page: ft.Page):
    page.title = "Scientific Calculator (Flet)"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.add(ScientificCalculatorApp())


if __name__ == "__main__":
    ft.app(target=main)