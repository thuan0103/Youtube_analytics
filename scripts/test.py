import truststore
truststore.inject_into_ssl()

import os
import ast
import time
import operator
import logging
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

from dotenv import load_dotenv
from ddgs import DDGS
import trafilatura
from trafilatura.settings import use_config

from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool

load_dotenv()

for name in ("trafilatura", "urllib3", "httpx", "httpcore"):
    logging.getLogger(name).setLevel(logging.CRITICAL)

llm = LLM(model="gpt-5-nano", api_key=os.getenv("OPENAI_API_KEY"))

MAX_CHARS_PER_PAGE = 3000
MAX_PAGES = 3
BLOCKED_DOMAINS = {
    "reuters.com", "bloomberg.com", "sciencedirect.com", "investing.com",
    "wsj.com", "ft.com", "linkedin.com", "facebook.com",
}
TF_CONFIG = use_config()
TF_CONFIG.set("DEFAULT", "DOWNLOAD_TIMEOUT", "8")
_search_cache: dict[str, list] = {}


# ======================= TOOLS =======================
def _is_blocked(url: str) -> bool:
    host = urlparse(url).netloc.lower().removeprefix("www.")
    return any(host == d or host.endswith("." + d) for d in BLOCKED_DOMAINS)


def _fetch_one(r: dict) -> dict:
    url = r.get("href", "")
    text = None
    if url and not _is_blocked(url):
        try:
            downloaded = trafilatura.fetch_url(url, config=TF_CONFIG)
            if downloaded:
                text = trafilatura.extract(downloaded, include_comments=False)
        except Exception:
            pass
    text = text or r.get("body", "")
    return {"title": r.get("title"), "url": url, "content": text[:MAX_CHARS_PER_PAGE]}


@tool("search web")
def search_web(request: str) -> list:
    """Tìm kiếm thông tin trên web. Trả về list gồm title, url và nội dung để làm bằng chứng."""
    key = request.strip().lower()
    if key in _search_cache:
        return _search_cache[key]
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(request, max_results=MAX_PAGES * 2))
    except Exception as e:
        return [{"error": f"Không tìm kiếm được: {e}"}]

    results.sort(key=lambda r: _is_blocked(r.get("href", "")))
    results = results[:MAX_PAGES]
    with ThreadPoolExecutor(max_workers=MAX_PAGES) as pool:
        output = list(pool.map(_fetch_one, results))
    _search_cache[key] = output
    return output


_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.USub: operator.neg,
}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("Biểu thức không hợp lệ")


@tool("Calculator")
def calculator(expression: str) -> str:
    """Tính một biểu thức số học, ví dụ '(120+80+45)/3' hoặc '25000/1200*100'. Hỗ trợ + - * / ** %."""
    try:
        return str(_eval(ast.parse(expression, mode="eval").body))
    except Exception as e:
        return f"Lỗi tính toán: {e}"


# ======================= AGENTS =======================
NO_ASK = "Không bao giờ hỏi lại hay xin phép người dùng; tự làm hết sức với thông tin hiện có."

researcher = Agent(
    role="Researcher",
    goal="Thu thập dữ kiện và số liệu cụ thể từ web, kèm URL nguồn",
    backstory=f"Chuyên gia tìm kiếm thông tin, luôn dùng tool 'search web' khi cần bằng chứng. {NO_ASK}",
    tools=[search_web],
    allow_delegation=False,
    max_iter=8,
    llm=llm,
    verbose=True,
)

analyst = Agent(
    role="Data Analyst",
    goal="Tính các chỉ số từ dữ liệu Researcher cung cấp",
    backstory=(
        "Chuyên gia phân tích số liệu cẩn thận. Luôn dùng tool 'Calculator' để tính, không tính nhẩm. "
        f"Không bịa số: thiếu dữ liệu thì ghi N/A. {NO_ASK}"
    ),
    tools=[calculator],
    allow_delegation=False,
    llm=llm,
    verbose=True,
)

writer = Agent(
    role="Writer",
    goal="Viết câu trả lời cuối cùng bằng tiếng Việt cho người dùng",
    backstory=(
        "Biên tập viên nhiều năm kinh nghiệm, viết rõ ràng, có cấu trúc, dẫn nguồn khi có số liệu. "
        f"Trò chuyện xã giao thì ngắn gọn, tự nhiên. {NO_ASK}"
    ),
    allow_delegation=False,
    llm=llm,
    verbose=True,
)


# ======================= TASKS (chạy tuần tự, truyền kết quả qua context) =======================
research_task = Task(
    description=(
        "Yêu cầu của người dùng: {question}\n\n"
        "Nếu yêu cầu là chào hỏi hoặc trò chuyện xã giao, không cần tra cứu: trả lời đúng một dòng "
        "'KHÔNG CẦN TRA CỨU'.\n"
        "Ngược lại, dùng tool 'search web' (tối đa 4 lần, mỗi lần truy vấn khác nhau) để thu thập "
        "dữ kiện và SỐ LIỆU CỤ THỂ (kèm đơn vị, kỳ báo cáo/ngày) phục vụ yêu cầu. "
        "Nguồn nào không có nội dung thì chuyển sang nguồn khác. Không xin phép hay hỏi lại."
    ),
    expected_output=(
        "Danh sách dữ kiện và số liệu cụ thể, mỗi mục kèm URL nguồn; "
        "ghi rõ mục nào không tìm thấy. Hoặc 'KHÔNG CẦN TRA CỨU'."
    ),
    agent=researcher,
)

analysis_task = Task(
    description=(
        "Yêu cầu của người dùng: {question}\n\n"
        "Dựa trên dữ liệu ở bước trước, tính các chỉ số cần thiết cho yêu cầu bằng tool 'Calculator' "
        "(ví dụ tăng trưởng %, biên lợi nhuận, P/E, tổng...). Thiếu dữ liệu thì ghi N/A, không bịa. "
        "Nếu bước trước là 'KHÔNG CẦN TRA CỨU' hoặc không có gì cần tính, trả lời đúng một dòng "
        "'KHÔNG CẦN TÍNH TOÁN'."
    ),
    expected_output="Bảng các chỉ số đã tính kèm công thức và số liệu đầu vào, hoặc 'KHÔNG CẦN TÍNH TOÁN'.",
    agent=analyst,
    context=[research_task],
)

write_task = Task(
    description=(
        "Yêu cầu của người dùng: {question}\n\n"
        "Viết câu trả lời cuối cùng bằng tiếng Việt dựa trên kết quả của các bước trước.\n"
        "- Nếu là chào hỏi/xã giao: đáp ngắn gọn, tự nhiên.\n"
        "- Nếu cần phân tích/báo cáo: viết đầy đủ, có cấu trúc, nêu số liệu và ghi nguồn (URL); "
        "chỗ nào thiếu dữ liệu thì nói rõ.\n"
        "Chỉ xuất nội dung câu trả lời, không mô tả quy trình hay việc các bước trước đã làm."
    ),
    expected_output="Câu trả lời hoàn chỉnh bằng tiếng Việt dành cho người dùng.",
    agent=writer,
    context=[research_task, analysis_task],
)

crew = Crew(
    agents=[researcher, analyst, writer],
    tasks=[research_task, analysis_task, write_task],
    process=Process.sequential,
    verbose=True,
)


# ======================= MAIN =======================
if __name__ == "__main__":
    print("Chat với AI (gõ 'exit' để thoát)\n")
    while True:
        question = input("Bạn: ").strip()
        if not question:
            continue
        if question.lower() in {"exit", "quit", "thoát"}:
            break

        start = time.perf_counter()
        try:
            reply = crew.kickoff(inputs={"question": question}).raw   # raw = kết quả của Writer
        except Exception as e:
            reply = f"Có lỗi xảy ra: {e}"
        elapsed = time.perf_counter() - start

        print(f"\nAI: {reply}")
        print(f"\n[Thời gian phản hồi: {elapsed:.2f}s]\n")