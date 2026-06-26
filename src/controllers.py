# src/controllers.py
import flet as ft
from api import send_stop_command, create_task, pause_all_agvs

# ---------- 通用辅助函数 ----------
def show_snackbar(page: ft.Page, message: str, color: str = None):
    """显示底部提示条"""
    page.snack_bar = ft.SnackBar(
        ft.Text(message),
        bgcolor=color or ft.Colors.GREEN,
    )
    page.snack_bar.open = True
    page.update()


# ---------- 具体事件处理函数 ----------
def on_emergency_stop_click(e, page: ft.Page):
    """紧急停止按钮点击处理"""
    success = send_stop_command("all")
    if success:
        show_snackbar(page, "🛑 已发送紧急停止指令！", color=ft.Colors.RED)
    else:
        show_snackbar(page, "❌ 紧急停止指令发送失败", color=ft.Colors.ORANGE)


def on_pause_all_click(e, page: ft.Page):
    """暂停所有AGV"""
    success = pause_all_agvs()
    if success:
        show_snackbar(page, "⏸️ 已暂停所有AGV")
    else:
        show_snackbar(page, "❌ 暂停指令失败", color=ft.Colors.ORANGE)


# ---------- 弹出任务创建对话框 ----------
def open_task_creation_dialog(page: ft.Page):
    """弹出对话框，让用户输入任务起点和终点"""
    try:
        print("[DEBUG] 开始打开任务创建对话框...")
        
        # 检查对话框是否已打开，防止重复打开
        if hasattr(page, '_dialog_open') and page._dialog_open:
            print("[DEBUG] 对话框已打开，忽略重复点击")
            return
        
        page._dialog_open = True
        
        # 创建文本框：输入任务起点
        start_point_field = ft.TextField(
            label="任务起点", 
            hint_text="例如：A1",
            width=250,
        )
        # 创建文本框：输入任务终点
        end_point_field = ft.TextField(
            label="任务终点", 
            hint_text="例如：B5",
            width=250,
        )

        def on_submit(e):
            print("[DEBUG] 提交任务创建...")
            start_point = start_point_field.value
            end_point = end_point_field.value
            if start_point and end_point:
                path = f"{start_point} -> {end_point}"
                print(f"[DEBUG] 创建任务：{path}")
                success = create_task("auto", path)
                if success:
                    show_snackbar(page, f"✅ 任务已创建：{path}")
                else:
                    show_snackbar(page, "❌ 任务创建失败", color=ft.Colors.ORANGE)
            else:
                show_snackbar(page, "⚠️ 请输入任务起点和终点", color=ft.Colors.ORANGE)
            
            # 关闭对话框
            on_cancel(None)

        def on_cancel(e):
            print("[DEBUG] 取消任务创建")
            # 先尝试关闭通过 page.show_dialog 打开的对话框
            try:
                page.pop_dialog()
            except Exception:
                pass
            # 如果之前存在 overlay 中的模态容器，尝试移除
            try:
                if modal_container in getattr(page, 'overlay', []):
                    page.overlay.remove(modal_container)
            except Exception:
                pass
            page._dialog_open = False
            page.update()

        # 创建对话框内容（卡片式设计），使用醒目配色和边框便于诊断可见性
        # 使用 BorderSide/Border 构造边框（兼容当前 Flet 版本）
        bs = ft.border.BorderSide(width=3, color=ft.Colors.RED)
        dialog_content = ft.Container(
            content=ft.Column(
                [
                    # 标题
                    ft.Row(
                        [
                            ft.Text("创建任务", size=26, weight="bold"),
                            ft.IconButton(
                                ft.Icons.CLOSE,
                                icon_size=28,
                                on_click=on_cancel,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(height=20, color="transparent"),
                    # 输入框
                    start_point_field,
                    end_point_field,
                    ft.Divider(height=20, color="transparent"),
                    # 按钮
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "取消",
                                on_click=on_cancel,
                                width=160,
                                height=48,
                                bgcolor=ft.Colors.GREY_400,
                                color=ft.Colors.BLACK,
                            ),
                            ft.ElevatedButton(
                                "确认",
                                on_click=on_submit,
                                width=160,
                                height=48,
                                bgcolor=ft.Colors.GREEN,
                                color=ft.Colors.WHITE,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=24,
                    ),
                ],
                spacing=24,
                tight=False,
                expand=True,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=28,
            border_radius=16,
            bgcolor=ft.Colors.YELLOW_100,
            border=ft.border.Border(top=bs, right=bs, bottom=bs, left=bs),
            width=900,
            height=600,
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=18,
                offset=ft.Offset(0, 10),
                color=ft.Colors.with_opacity(0.28, ft.Colors.BLACK),
            ),
        )

        # 创建模态背景（半透明黑色覆盖层）
        modal_container = ft.Container(
            left=0,
            top=0,
            right=0,
            bottom=0,
            align=ft.alignment.Alignment.CENTER,
            content=ft.Column(
                [
                    ft.Container(expand=True),
                    ft.Row(
                        [
                            ft.Container(expand=True),
                            dialog_content,
                            ft.Container(expand=True),
                        ],
                        expand=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Container(expand=True),
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.with_opacity(0.85, ft.Colors.BLACK),
            expand=True,
            visible=True,
        )

        # 输出页面尺寸调试信息，检查是否受限
        try:
            print(f"[DEBUG] page.width={page.width}, page.height={page.height}")
        except Exception:
            print("[DEBUG] 无法读取 page.width/page.height")
        print("[DEBUG] 对话框对象已创建，准备显示...")

        # 使用 page.show_dialog 显示，作为更可靠的弹窗方式
        dlg = ft.AlertDialog(
            content=dialog_content,
            modal=True,
        )

        try:
            overlay_len_before = len(getattr(page, 'overlay', []))
        except Exception:
            overlay_len_before = 'n/a'
        print(f"[DEBUG] overlay_len_before={overlay_len_before}")
        print(f"[DEBUG] dlg_repr={repr(dlg)}")

        def _on_cancel_dialog(e=None):
            try:
                page.pop_dialog()
            except Exception:
                pass
            page._dialog_open = False
            page.update()

        # 绑定关闭按钮
        # 这里 dialog_content 内部的关闭回调会调用 on_cancel，确保释放标志
        page.show_dialog(dlg)
        try:
            overlay_len_after = len(getattr(page, 'overlay', []))
        except Exception:
            overlay_len_after = 'n/a'
        print(f"[DEBUG] 对话框已显示 (via page.show_dialog), overlay_len_after={overlay_len_after}")
    except Exception as ex:
        print(f"[ERROR] open_task_creation_dialog: {ex}")
        import traceback
        traceback.print_exc()
        page._dialog_open = False

