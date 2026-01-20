import os

from openai import OpenAI  # openai==1.52.2
import dotenv

from main import get_db

dotenv.load_dotenv()

client = OpenAI(
    api_key= os.getenv("UPSTAGE_API_KEY"),
    base_url="https://api.upstage.ai/v1"
)

def summary():
   conn = get_db()
   cursor = conn.cursor(dictionary=True, buffered=True)

   cursor.execute("SELECT content, completed FROM todo WHERE DATE(created_at) = CURDATE() ORDER BY id DESC")
   rows = cursor.fetchall() or []

   cursor.close()
   conn.close()

   items = []
   for r in rows:
       if not r:
           continue
       content = r.get("content")
       if not content:
           continue
       completed = bool(r.get("completed"))
       status = "완료" if completed else "미완료"
       items.append({"content": content, "completed": completed, "status": status})

   total = len(items)
   todo_lines = "\n".join([f"- [{it['status']}] {it['content']}" for it in items])

   prompt = f"""
    당신은 유저의 유능한 비서입니다.
    아래는 오늘 생성된 할 일 목록입니다. 총 {total}개입니다.
    할 일 목록: {todo_lines if todo_lines else "- (없음)"}
    
    요구사항:
    - 할 일 목록이 1개 이상이면, 완료/미완료 상태를 반영해서 3~6줄로 요약하세요.
    - 그 다음, 미완료 항목 중 우선순위 TOP 3를 제안하세요. (이유를 간단히)
    - 할 일이 0개면, 현재 상태를 짧게 설명하고 할 일을 1~2개 등록하도록 요청하세요.
    """

   response = client.chat.completions.create(
       model="solar-pro2",
       messages=[{"role": "user", "content": prompt}],
   )

   summary_text = response.choices[0].message.content.strip()

   return {
       "summary": summary_text
   }