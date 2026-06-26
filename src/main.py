# main.py
import asyncio

import flet as ft
from ui import (
    build_agv_tiles,
    build_title_bar,
    build_management_tabs,
    build_bottom_bar,
)
from api import fetch_agv_list, fetch_task_list, fetch_storage_list

from controllers import (
    on_emergency_stop_click,
    open_task_creation_dialog,
    on_pause_all_click,
)
def main(page: ft.Page):
    page.title = "AGV 调度 Pad"
    page.bgcolor = "#F5F5F5"
    page.padding = 20

    # ---------- 数据 ----------
    # 初始加载数据（可异步）
    agv_data = fetch_agv_list()
    task_data = fetch_task_list()
    storage_data = fetch_storage_list()

    # ---------- 界面构建 ----------
    title_bar = build_title_bar()
    map_area = build_management_tabs(task_data, agv_data, storage_data)

    # 定义底部按钮的事件处理（直接绑定控制器函数）
    # 注意：控制器函数需要 page 参数，可以使用 lambda 传递
    bottom_bar = build_bottom_bar(
        on_stop_click=lambda e: on_emergency_stop_click(e, page),
        on_create_click=lambda e: open_task_creation_dialog(page),
        on_pause_click=lambda e: on_pause_all_click(e, page),
    )

    def refresh_agv_view(e=None):
        latest_agv_data = fetch_agv_list()
        agv_view = getattr(map_area, "agv_view", None)
        list_view = getattr(agv_view, "agv_list_view", None)
        if list_view is not None:
            list_view.controls = build_agv_tiles(latest_agv_data)
            list_view.update()
            if agv_view is not None:
                agv_view.update()
            page.update()

    async def periodic_refresh():
        while True:
            await asyncio.sleep(5)
            refresh_agv_view()

    page.run_task(periodic_refresh)

    # ---------- 组装页面 ----------
    page.add(
        ft.Column(
            [
                title_bar,
                ft.Container(
                    expand=True,
                    content=map_area,
                ),  
                bottom_bar,
            ],
            expand=True,
            spacing=20,
        )
    )

ft.run(main)
