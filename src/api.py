# api.py
import datetime
import json
from pathlib import Path
import requests
from models import AGVStatus, Task





_SERVER_BASE_URL = "http://192.168.1.67:52000"


def get_server_base_url() -> str:
    return _SERVER_BASE_URL


def set_server_base_url(url: str) -> str:
    global _SERVER_BASE_URL
    normalized = (url or "").strip().rstrip("/")
    if not normalized:
        normalized = "http://192.168.1.67:52000"
    _SERVER_BASE_URL = normalized
    return _SERVER_BASE_URL


def build_api_url(path: str) -> str:
    normalized_path = path if path.startswith("/") else f"/{path}"
    return f"{get_server_base_url()}{normalized_path}"


def fetch_agv_list() -> list[AGVStatus]:
    
    try:
        resp = requests.get(build_api_url("/api/agv/list"))
        resp.raise_for_status()  # 如果HTTP状态码不是200，抛出异常
        data = resp.json()       # 返回的是一个列表，每个元素是一个AGV信息字典
    except Exception as e:
        print(f"请求AGV列表失败: {e}")
        return []  # 发生错误时返回空列表，或者你可以选择抛出异常

    agv_list = []
    for item in data:
        # 字段映射关系：
        # ID       -> id
        # Name     -> name
        # IP       -> ip
        # State    -> state（直接使用）
        # Battery  -> battery（整数）
        # Floor    + CurrentPoint -> location（组合成“x楼 / 点位xxxx”）
        # taskId   -> task（注意taskId可能是字符串'null'，统一转为空字符串）
        # 其他字段（onLine, enable等）暂不使用，如有需要可扩展AGVStatus类

        location = f"{item.get('Floor', '未知')}L / {item.get('CurrentPoint', 0)}"
        task_id = item.get('taskId', '')
        if task_id == 'null' or task_id is None:
            task_id = ''

        agv = AGVStatus(
            id=item.get('ID', ''),
            ip=item.get('IP', ''),
            name=item.get('Name', ''),
            state=item.get('State', '未知'),
            battery=item.get('Battery', 0),
            location=location,
            task=task_id,
        )
        agv_list.append(agv)

    return agv_list


def fetch_task_list(page: int = 1, pageSize: int = 7, filters: dict | None = None) -> dict:
    """从服务端分页获取任务列表。"""
    url = build_api_url("/api/task/list")
    payload = {
        "page": page,
        "pageSize": pageSize,
        "filters": filters or {},
    }
    headers = {"Content-Type": "application/json"}

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10000)
        resp.raise_for_status()
        result = resp.json()
        print(f"POST请求成功: {result}")
    except Exception as e:
        print(f"POST请求失败: {e}")
        result = {"total": 0, "tasks": []}

    return normalize_task_page_response(result, page=page, pageSize=pageSize)

def normalize_task_page_response(result: dict, page: int = 1, pageSize: int | None = None, page_size: int | None = None) -> dict:
    """把服务端返回的分页任务结果规范化为统一结构。"""
    page_size = page_size if page_size is not None else pageSize
    if page_size is None:
        page_size = 10

    data = result.get("data", result)

    task_json = []
    if isinstance(data, dict):
        task_json = data.get("taskJson", [])
        if not task_json:
            task_json = result.get("tasks", [])
    else:
        task_json = []

    tasks = []
    for value in task_json:
        item = json.loads(value) if isinstance(value, str) else value
        tasks.append(
            Task(
                id=item.get("id", item.get("taskId", "")),
                priority=item.get("priority", 1),
                path=item.get("path", ""),
                assigned_agv=item.get("executingAgvName", item.get("assignedAGV", "")),
                state=item.get("state", 0),
                created_at=item.get("createTime", item.get("createdAt", "")),
                started_at=item.get("startTime", item.get("startedAt", "")),
                finished_at=item.get("endTime", item.get("finishedAt", "")),
            )
        )

    total = 0
    if isinstance(data, dict):
        total = data.get("taskCount", result.get("total", 0))
    else:
        total = result.get("total", 0)
    total_pages = max(1, (total + page_size - 1) // page_size) if page_size else 1

    return {
        "page": page,
        "page_size": page_size,
        "pageSize": page_size,
        "total": total,
        "total_pages": total_pages,
        "tasks": tasks,
    }

def send_stop_command(agv_id: str) -> bool:
    # 调用后端停止接口
    # response = requests.post(f"http://xxx/stop/{agv_id}")
    # return response.status_code == 200
    return True


def load_factory_map() -> dict:
    config_path = Path(__file__).resolve().parent / "工厂.json"
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)

# api.py (补充)

def create_task(agv_id: str, destination: str) -> bool:
    """模拟创建任务"""
    print(f"模拟创建任务: AGV {agv_id} 前往 {destination}")
    return True

def pause_all_agvs() -> bool:
    """模拟暂停所有AGV"""
    print("模拟暂停所有AGV")
    return True


# def fetch_storage_list(filters: dict | None = None, state: int | None = None, name: str = "") -> list:
#     """根据库位筛选条件请求服务端数据，失败时返回本地示例数据。"""
#     from models import StorageSlot

#     filter_map = filters or {}
#     status_value = filter_map.get("status", "") or ""
#     slot_id = filter_map.get("slot_id", "") or filter_map.get("id", "") or ""
#     occupant = filter_map.get("occupant", "") or ""

#     if state is None:
#         state = {
#             "idle": 0,
#             "occupied": 1,
#             "reserved": 2,
#             "error": 3,
#         }.get(status_value, None)

#     payload = {
#         "state": state,
#         "name": name or slot_id or occupant or "",
#         "filters": {
#             "status": status_value,
#             "slot_id": slot_id,
#             "occupant": occupant,
#         },
#     }
#     headers = {"Content-Type": "application/json"}

#     try:
#         resp = requests.post("http://192.168.1.67:52000/api/map/getStoragePoint", json=payload, headers=headers, timeout=10000)
#         resp.raise_for_status()
#         result = resp.json()
#         print(f"POST请求成功: {result}")

#         code =  result.get("code", 404)
#         if code == 0:
#             data = result.get("data", {})

          
#             return 

#     except Exception as e:
#         print(f"POST请求失败: {e}")

#     return [
#         StorageSlot(id="SLOT-001", status="idle", occupant="", updated_at="2026-06-23 08:00", capacity=1, note="A区-01"),
#         StorageSlot(id="SLOT-002", status="occupied", occupant="Pallet-123", updated_at="2026-06-23 09:12", capacity=1, note="A区-02"),
#         StorageSlot(id="SLOT-003", status="reserved", occupant="Order-456", updated_at="2026-06-22 17:50", capacity=2, note="B区-05"),
#         StorageSlot(id="SLOT-004", status="error", occupant="", updated_at="2026-06-20 11:20", capacity=1, note="C区-03"),
#     ]

def fetch_storage_list(filters: dict | None = None, state: int | None = None, name: str = "") -> list:
    """根据库位筛选条件请求服务端数据，失败时返回本地示例数据。"""
    from models import StorageSlot
    # 解析筛选条件（仅用于从 filters 中提取状态，但最终会转换为字符串）
    filter_map = filters or {}
    status_value = filter_map.get("status", "") or ""

    # 如果传入了 state 整数，映射为字符串；否则从 status_value 转换
    state_str = None
    if state is not None:
        # 整数 → 字符串映射（与 C# 端枚举保持一致）
        state_map = {0: "idle", 1: "occupied", 2: "reserved", 3: "error"}
        state_str = state_map.get(state)
    elif status_value:
        state_str = status_value  # 直接使用传入的字符串
    # 否则 state_str 保持 None，服务端不会按状态筛选

    # 构造请求载荷（仅包含 C# 服务端需要的两个字段）
    payload = {}
    if state_str is not None:
        payload["state"] = state_str
    if name:
        payload["name"] = name
    # 如果 name 为空但 slot_id 或 occupant 有值，优先使用它们作为搜索关键词
    elif filter_map.get("slot_id"):
        payload["name"] = filter_map["slot_id"]
    elif filter_map.get("occupant"):
        payload["name"] = filter_map["occupant"]

    headers = {"Content-Type": "application/json"}

    try:
        # 注意：超时时间建议改为 10 秒（而非 10000 秒）
        resp = requests.post(
            build_api_url("/api/map/getStoragePoint"),
            json=payload,
            headers=headers,
            timeout=10
        )
        resp.raise_for_status()
        result = resp.json()
        print(f"POST请求成功: {result}")

        # 检查返回码（C# 返回 200 表示成功）
        code = result.get("code", -1)
        if code == 200:
            data = result.get("data", {})
            storage_list = data.get("StorageStateList", [])
            
            # 将服务端返回的数据转换为 StorageSlot 对象
            return [
                StorageSlot(
                    id=item.get("name", ""),          # 服务端无 id 字段，使用 name 代替
                    status=item.get("state", "idle"), # 状态字符串
                    occupant="",                      # 服务端未返回，留空
                    updated_at=datetime.datetime.now().isoformat(),  # 无时间戳，使用当前时间
                    capacity=1,                       # 默认容量
                    note=item.get("name", ""),        # 备注使用 name
                )
                for item in storage_list
            ]
        else:
            print(f"服务端返回错误码: {code}, 消息: {result.get('message', '')}")

    except requests.exceptions.RequestException as e:
        print(f"POST请求失败: {e}")
    except Exception as e:
        print(f"处理响应时出错: {e}")

    # 请求失败或数据异常时，返回本地示例数据（降级方案）
    return [
        StorageSlot(id="SLOT-001", status="idle", occupant="", updated_at="2026-06-23 08:00", capacity=1, note="A区-01"),
        StorageSlot(id="SLOT-002", status="occupied", occupant="Pallet-123", updated_at="2026-06-23 09:12", capacity=1, note="A区-02"),
        StorageSlot(id="SLOT-003", status="reserved", occupant="Order-456", updated_at="2026-06-22 17:50", capacity=2, note="B区-05"),
        StorageSlot(id="SLOT-004", status="error", occupant="", updated_at="2026-06-20 11:20", capacity=1, note="C区-03"),
    ]