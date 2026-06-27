# ui.py
import flet as ft
from api import fetch_task_list
from models import AGVStatus, Task


def paginate_task_list(task_list: list[Task], page_size: int = 7, page_index: int = 0) -> dict:
    """本地分页辅助函数，保留给测试和兼容逻辑。"""
    total_items = len(task_list)
    total_pages = max(1, (total_items + page_size - 1) // page_size)
    if page_index < 0:
        page_index = 0
    if page_index >= total_pages:
        page_index = total_pages - 1

    start = page_index * page_size
    end = start + page_size
    return {
        "items": task_list[start:end],
        "page_index": page_index,
        "page_size": page_size,
        "total_pages": total_pages,
        "total_items": total_items,
    }


def build_title_bar():
    return ft.Container()


def build_task_view(task_list: list[Task]):
    return ft.Container(
        bgcolor="#FFFFFF",
        border_radius=10,
        expand=True,
        padding=10,
        content=ft.Column(
            [
                build_task_panel(task_list),
            ],
            spacing=12,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        ),
    )


def build_storage_cards(storage_list: list):
    """生成一组库位信息卡片。"""
    cards = []
    for slot in storage_list:
        color = {
            "idle": "#E8F5E9",
            "occupied": "#FFE0B2",
            "reserved": "#E3F2FD",
            "error": "#FFCDD2",
        }.get(slot.status, "#F5F5F5")

        cards.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(f"{slot.id}", weight=ft.FontWeight.BOLD),
                        ft.Text(slot.note or "-", size=12, color="#555"),
                        ft.Text(f"占用: {slot.occupant or '-'}  容量: {slot.capacity}", size=12),
                        ft.Text(f"更新时间: {slot.updated_at}", size=11, color="#777"),
                    ],
                    tight=True,
                    spacing=6,
                ),
                padding=10,
                bgcolor=color,
                border_radius=7,
                width=220,
            )
        )

    # 使用 Row 包裹并允许换行
    return ft.Row(cards, wrap=True, spacing=12)


def build_agv_view(agv_list: list[AGVStatus]):
    agv_list_view = build_agv_list(agv_list)
    container = ft.Container(
        bgcolor="#FFFFFF",
        border_radius=10,
        expand=True,
        padding=10,
        content=ft.Column(
            [
                agv_list_view,
            ],
            spacing=12,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        ),
    )
    container.agv_list_view = agv_list_view
    return container


def build_storage_view(storage_list: list):
    """库位管理页面。"""
    return ft.Container(
        bgcolor="#FFFFFF",
        border_radius=10,
        expand=True,
        padding=10,
        content=ft.Column(
            [
                build_storage_panel(storage_list),
            ],
            spacing=12,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        ),
    )


def build_storage_panel(storage_list: list):
    """库位筛选 + 卡片展示面板。"""
    
    # 筛选控件
    status_dropdown = ft.Dropdown(
        width=150,
        label="库位状态",
        options=[
            ft.dropdown.Option(key="all", text="全部"),
            ft.dropdown.Option(key="idle", text="闲置"),
            ft.dropdown.Option(key="occupied", text="占用"),
            ft.dropdown.Option(key="reserved", text="预留"),
            ft.dropdown.Option(key="error", text="故障"),
        ],
        value="all",
    )

    slot_id_field = ft.TextField(label="库位ID", expand=True)
    occupant_field = ft.TextField(label="占用者", expand=True)

    filter_row = ft.Row(
        [
            status_dropdown,
            slot_id_field,
            occupant_field,
            ft.ElevatedButton("筛选", icon=ft.Icons.SEARCH),
            ft.TextButton("重置"),
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=12,
    )

    # 库位卡片
    cards_view = build_storage_cards(storage_list)

    return ft.Container(
        bgcolor="#FFFFFF",
        border_radius=10,
        expand=True,
        padding=10,
        content=ft.Column(
            [
                filter_row,
                ft.Container(expand=True, content=cards_view),
            ],
            spacing=12,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        ),
    )


def build_management_tabs(task_list: list[Task], agv_list: list[AGVStatus], storage_list: list = None):
    task_view = build_task_view(task_list)
    agv_view = build_agv_view(agv_list)
    storage_view = build_storage_view(storage_list) if storage_list else ft.Container()

    tabs = ft.Tabs(
        length=3,
        expand=True,
        content=ft.Column(
            expand=True,
            spacing=10,
            controls=[
                ft.TabBar(
                    tabs=[
                        ft.Tab(label="任务管理"),
                        ft.Tab(label="AGV 管理"),
                        ft.Tab(label="库位管理"),
                    ],
                    indicator_color="#1976D2",
                    label_color="#1976D2",
                    unselected_label_color="#757575",
                ),
                ft.TabBarView(
                    expand=True,
                    controls=[task_view, agv_view, storage_view],
                ),
            ],
        ),
    )
    tabs.agv_view = agv_view
    return tabs


def build_task_panel(task_list: list[Task]):
    """任务筛选 + 列表面板：支持按服务端分页和筛选加载。"""

    page_size = 5
    current_page = {"index": 0}
    current_filters = {"status": "all", "task_id": "", "agv": "", "path": ""}

    def refresh_table(page_num: int):
        payload = fetch_task_list(
            page=page_num + 1,
            pageSize=page_size,
            filters={
                "status": current_filters["status"],
                "task_id": current_filters["task_id"],
                "agv": current_filters["agv"],
                "path": current_filters["path"],
            },
        )
        current_page["index"] = payload["page"] - 1
        rows = []
        for task in payload["tasks"]:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(task.id)),
                        ft.DataCell(ft.Text(task.priority)),
                        ft.DataCell(ft.Text(task.path)),
                        ft.DataCell(ft.Text(task.assigned_agv)),
                        ft.DataCell(ft.Text(task.state, color=_task_state_color(task.state))),
                        ft.DataCell(ft.Text(task.created_at)),
                        ft.DataCell(ft.Text(task.started_at)),
                        ft.DataCell(ft.Text(task.finished_at)),
                    ]
                )
            )

        table.rows = rows
        page_text.value = f"第 {payload['page']}/{payload['total_pages']} 页  共 {payload['total']} 条"
        prev_btn.disabled = payload["page"] <= 1
        next_btn.disabled = payload["page"] >= payload["total_pages"]

        try:
            table.update()
            page_text.update()
            prev_btn.update()
            next_btn.update()
        except RuntimeError:
            pass

    # 筛选控件
    status_dropdown = ft.Dropdown(
        width=150,
        label="任务状态",
        options=[
            ft.dropdown.Option(key="all", text="全部"),
            ft.dropdown.Option(key="waiting", text="待执行"),
            ft.dropdown.Option(key="execution", text="执行中"),
            ft.dropdown.Option(key="success", text="成功"),
            ft.dropdown.Option(key="fail", text="失败"),
            ft.dropdown.Option(key="cancel", text="取消"),
        ],
        value="all",
    )

    # 后三个筛选框放宽为可扩展，以占用更多可用空间
    task_id_field = ft.TextField(label="任务ID", expand=True)
    agv_field = ft.TextField(label="任务AGV", expand=True)
    path_field = ft.TextField(label="任务路径点", expand=True)

    def apply_filters(e):
        current_filters["status"] = status_dropdown.value or "all"
        current_filters["task_id"] = task_id_field.value or ""
        current_filters["agv"] = agv_field.value or ""
        current_filters["path"] = path_field.value or ""
        refresh_table(0)

    def reset_filters(e):
        status_dropdown.value = "all"
        task_id_field.value = ""
        agv_field.value = ""
        path_field.value = ""
        current_filters.update({"status": "all", "task_id": "", "agv": "", "path": ""})
        refresh_table(0)

    filter_row = ft.Row(
        [
            status_dropdown,
            task_id_field,
            agv_field,
            path_field,
            ft.ElevatedButton("筛选", icon=ft.Icons.SEARCH, on_click=apply_filters),
            ft.TextButton("重置", on_click=reset_filters),
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=12,
    )

    page_text = ft.Text("")
    page_input = ft.TextField(label="跳转到页", width=100,height=30, keyboard_type=ft.KeyboardType.NUMBER)
    prev_btn = ft.IconButton(ft.Icons.CHEVRON_LEFT, on_click=lambda e: refresh_table(max(0, current_page["index"] - 1)))
    next_btn = ft.IconButton(ft.Icons.CHEVRON_RIGHT, on_click=lambda e: refresh_table(current_page["index"] + 1))

    def jump_to_page(e):
        try:
            target_page = int(page_input.value or "0") - 1
        except ValueError:
            target_page = current_page["index"]
        refresh_table(target_page)

    jump_btn = ft.ElevatedButton("跳转", on_click=jump_to_page)

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("任务ID")),
            ft.DataColumn(ft.Text("优先级")),
            ft.DataColumn(ft.Text("路径")),
            ft.DataColumn(ft.Text("分配的AGV")),
            ft.DataColumn(ft.Text("状态")),
            ft.DataColumn(ft.Text("创建时间")),
            ft.DataColumn(ft.Text("开始时间")),
            ft.DataColumn(ft.Text("结束时间")),
        ],
        rows=[],
        heading_row_color=ft.Colors.GREY_200,
        show_checkbox_column=False,
        divider_thickness=1,
        column_spacing=14,
        expand=True,
    )

    pagination_row = ft.Container(
        content=ft.Row(
            [
                prev_btn,
                page_text,
                next_btn,
                page_input,
                jump_btn,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=7,
        ),
        margin=ft.margin.Margin(top=8),
        alignment=ft.Alignment(0, 0),
    )

    refresh_table(0)

    return ft.Container(
        bgcolor="#FFFFFF",
        border_radius=10,
        expand=True,
        padding=10,
        content=ft.Column(
            [
                filter_row,
                ft.Container(expand=True, content=table),
                ft.Container(height=12),
                pagination_row,
            ],
            spacing=1,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        ),
    )

def _status_color(state: str) -> str:
    return {
        "运行中": "#4CAF50",
        "空闲": "#2196F3",
        "故障": "#F44336",
        "充电中": "#FFC107"
    }.get(state, "#757575")

def _task_state_color(state: str) -> str:
    return _status_color(state)

# 兼容旧接口，保持现有调用方式。
def build_map_area(task_list: list[Task], page: ft.Page):
    return build_task_panel(task_list)


def _status_color(state: str) -> str:
    return {
        "运行中": "#4CAF50",
        "空闲": "#2196F3",
        "故障": "#F44336",
        "充电中": "#FFC107"
    }.get(state, "#757575")


def build_agv_tiles(agv_list: list[AGVStatus]):
    return [
        ft.ListTile(
            title=ft.Text(f"{agv.name}  [{agv.id}]", weight=ft.FontWeight.BOLD),
            subtitle=ft.Column(
                [
                    ft.Text(f"IP: {agv.ip}", size=12, color="#555"),
                    ft.Text(f"状态: {agv.state} · 电量: {agv.battery}%", size=12),
                    ft.Text(f"位置/楼层: {agv.location}", size=12, color="#555"),
                ],
                tight=True,
                spacing=4,
            ),
            trailing=ft.Container(
                ft.Text(agv.state, color="#FFFFFF", size=12),
                padding=ft.Padding.symmetric(horizontal=10, vertical=6),
                bgcolor=_status_color(agv.state),
                border_radius=10,
            ),
        )
        for agv in agv_list
    ]


def build_agv_list(agv_list: list[AGVStatus]):
    """根据数据动态生成 ListView，并占满可用垂直空间。"""
    return ft.ListView(build_agv_tiles(agv_list), expand=True, spacing=7)

def build_info_panel(agv_list):
    return ft.Container(
        bgcolor="#FFFFFF",
        border_radius=10,
        expand=1,
        content=ft.Column(
            [
                ft.Text("📋 AGV 列表", size=20, weight=ft.FontWeight.BOLD),
                build_agv_list(agv_list),
            ]
        ),
        padding=10,
    )

def build_bottom_bar(on_stop_click=None, on_create_click=None, on_pause_click=None):
    return ft.Row(
        [
            ft.ElevatedButton("创建任务", icon=ft.Icons.ADD, on_click=on_create_click),
            ft.ElevatedButton("暂停所有", icon=ft.Icons.PAUSE, on_click=on_pause_click),
            ft.ElevatedButton(
                "紧急停止",
                icon=ft.Icons.ERROR,
                color="#FFFFFF",
                bgcolor="#F44336",
                on_click=on_stop_click,   # 事件处理从外部传入
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
    )