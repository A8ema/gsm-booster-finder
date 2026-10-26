import flet as ft
import asyncio
from datetime import datetime
import platform


class SignalMonitor:
    def __init__(self):
        self.signals = []
        self.max_signal = -200
        self.best_reading = None
    
    def get_mock_signal(self):
        # For development/testing
        import random
        return {
            "rsrp": random.randint(-120, -70),
            "rssi": random.randint(-100, -50),
            "type": random.choice(["4G LTE", "3G", "2G"]),
            "operator": "Test",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
    
    def update(self, data):
        self.signals.append(data)
        if data["rsrp"] > self.max_signal:
            self.max_signal = data["rsrp"]
            self.best_reading = data
        if len(self.signals) > 50:
            self.signals.pop(0)


def main(page: ft.Page):
    page.title = "Поиск направления GSM-усилителя"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 10
    page.scroll = ft.ScrollMode.AUTO
    
    # Android permissions would be needed in real app
    monitor = SignalMonitor()
    
    # UI elements
    signal_rsrp = ft.Text("- --", size=48, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
    signal_rssi = ft.Text("RSSI: --", size=16)
    network_type = ft.Text("Сеть: --", size=16)
    operator = ft.Text("Оператор: --", size=16)
    max_signal_text = ft.Text("Лучший: --", size=20, weight=ft.FontWeight.BOLD)
    best_time = ft.Text("Время: --", size=14)
    status_text = ft.Text("Нажмите 'Старт' для измерения", size=14, color=ft.Colors.GREY_700)
    
    # Signal bars visualization
    bars = []
    for i in range(5):
        bars.append(ft.Container(
            width=30,
            height=20 + i*10,
            bgcolor=ft.Colors.GREY_400,
            border_radius=3
        ))
    
    bars_row = ft.Row(bars, alignment=ft.MainAxisAlignment.CENTER, spacing=5)
    
    measuring = False
    
    def update_bars(rsrp):
        # Convert RSRP to bars (rough approximation)
        if rsrp >= -80:
            count = 5
        elif rsrp >= -90:
            count = 4
        elif rsrp >= -100:
            count = 3
        elif rsrp >= -110:
            count = 2
        elif rsrp >= -120:
            count = 1
        else:
            count = 0
        
        for i, bar in enumerate(bars):
            if i < count:
                if count >= 4:
                    bar.bgcolor = ft.Colors.GREEN
                elif count >= 3:
                    bar.bgcolor = ft.Colors.YELLOW_700
                elif count >= 2:
                    bar.bgcolor = ft.Colors.ORANGE
                else:
                    bar.bgcolor = ft.Colors.RED
            else:
                bar.bgcolor = ft.Colors.GREY_400
        page.update()
    
    async def measure_signals(e):
        nonlocal measuring
        if measuring:
            measuring = False
            start_btn.text = "Старт"
            start_btn.icon = ft.Icons.PLAY_ARROW
            status_text.value = "Измерение остановлено"
            page.update()
            return
        
        measuring = True
        start_btn.text = "Стоп"
        start_btn.icon = ft.Icons.STOP
        status_text.value = "Идёт поиск лучшего направления..."
        page.update()
        
        while measuring:
            data = monitor.get_mock_signal()
            monitor.update(data)
            
            signal_rsrp.value = f"{data['rsrp']} dBm"
            signal_rssi.value = f"RSSI: {data['rssi']} dBm"
            network_type.value = f"Сеть: {data['type']}"
            operator.value = f"Оператор: {data['operator']}"
            
            if monitor.best_reading:
                max_signal_text.value = f"Лучший: {monitor.max_signal} dBm"
                best_time.value = f"Время: {monitor.best_reading['timestamp']}"
            
            update_bars(data['rsrp'])
            page.update()
            await asyncio.sleep(1)
    
    start_btn = ft.ElevatedButton(
        text="Старт",
        icon=ft.Icons.PLAY_ARROW,
        on_click=measure_signals,
        width=200,
        height=50
    )
    
    clear_btn = ft.ElevatedButton(
        text="Сброс",
        icon=ft.Icons.REFRESH,
        on_click=lambda e: reset_data(),
        width=200,
        height=50
    )
    
    def reset_data():
        monitor.signals.clear()
        monitor.max_signal = -200
        monitor.best_reading = None
        max_signal_text.value = "Лучший: --"
        best_time.value = "Время: --"
        status_text.value = "Данные сброшены"
        page.update()
    
    # Instructions
    instructions = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Инструкция:", weight=ft.FontWeight.BOLD, size=16),
                ft.Text("1. Нажмите 'Старт'", size=14),
                ft.Text("2. Медленно поворачивайте телефон/антенну", size=14),
                ft.Text("3. Следите за максимальным значением", size=14),
                ft.Text("4. Остановитесь там, где сигнал максимальный", size=14),
            ]),
            padding=10
        )
    )
    
    page.add(
        ft.Column([
            ft.Text("GSM Booster Finder", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Divider(),
            ft.Container(
                content=ft.Column([
                    signal_rsrp,
                    bars_row,
                    ft.Row([signal_rssi, network_type], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                    operator,
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                bgcolor=ft.Colors.BLUE_50,
                border_radius=10
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("РЕКОРД", size=16, weight=ft.FontWeight.BOLD),
                    max_signal_text,
                    best_time,
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=15,
                bgcolor=ft.Colors.GREEN_50,
                border_radius=10
            ),
            ft.Row([start_btn, clear_btn], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            status_text,
            ft.Divider(),
            instructions
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
    )


ft.app(target=main)
