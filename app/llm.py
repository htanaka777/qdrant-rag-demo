from openai import OpenAI

from app.config import get_settings


SYSTEM_PROMPT = """あなたは社内ITヘルプデスクのアシスタントです。
必ず提供された「参考情報」だけを根拠に回答してください。
参考情報に答えがない場合は、推測せず「参考情報からは確認できません」と回答してください。
回答は簡潔で、必要に応じて手順を箇条書きにしてください。
"""


class OpenAILLM:
    def __init__(self) -> None:
        settings = get_settings()
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def generate(self, question: str, contexts: list[dict]) -> str:
        context_text = "\n\n".join(
            f"[{i + 1}] {item['title']}\n{item['text']}\n出典: {item['source']}"
            for i, item in enumerate(contexts)
        )

        prompt = f"""参考情報:
{context_text}

質問:
{question}
"""

        response = self.client.responses.create(
            model=self.model,
            instructions=SYSTEM_PROMPT,
            input=prompt,
            store=False,
        )
        return response.output_text.strip()
