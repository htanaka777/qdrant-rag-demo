"use strict";
const byId = (id) => document.getElementById(id);
const form = byId("ask-form");
const question = byId("question");
let busy = false;
question.addEventListener("input", () => {
  question.setCustomValidity("");
  byId("count").textContent = `${question.value.length} / 2000`;
});
document.querySelectorAll("[data-question]").forEach((button) => {
  button.addEventListener("click", () => {
    question.value = button.dataset.question;
    question.dispatchEvent(new Event("input"));
    question.focus();
  });
});
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (busy) return;
  if (!question.value.trim()) {
    question.setCustomValidity("質問を入力してください。");
    question.reportValidity();
    return;
  }
  const payload = { question: question.value.trim(), top_k: Number(byId("top-k").value) };
  busy = true;
  byId("submit").disabled = true;
  byId("result-panel").setAttribute("aria-busy", "true");
  byId("status").textContent = "検索・回答生成中…";
  byId("error").hidden = true;
  byId("empty").hidden = true;
  byId("technical-result").hidden = true;
  byId("output").hidden = true;
  byId("request-json").textContent = JSON.stringify(payload, null, 2);
  byId("response-json").textContent = "応答を待っています…";
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 120000);
  try {
    const response = await fetch("/ask", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload), signal: controller.signal,
    });
    const raw = await response.text();
    let data;
    try { data = JSON.parse(raw); } catch { throw new Error("サーバーから正しいJSONを受信できませんでした。"); }
    byId("response-json").textContent = JSON.stringify(data, null, 2);
    if (!response.ok) throw new Error(`リクエストに失敗しました（HTTP ${response.status}）。APIのログ、OpenAI設定、Qdrant接続とFAQ登録を確認してください。`);
    if (typeof data.answer !== "string" || !Array.isArray(data.sources) ||
        ![data.retrieval_ms, data.generation_ms, data.total_ms].every(Number.isFinite)) {
      throw new Error("レスポンスの形式が想定と異なります。APIの仕様を確認してください。");
    }
    byId("answer").textContent = data.answer || "回答が空でした。質問を変えて再試行してください。";
    byId("request-summary").textContent = `質問：${payload.question}`;
    for (const [id, value] of [["retrieval", data.retrieval_ms], ["generation", data.generation_ms], ["total", data.total_ms]]) {
      byId(id).textContent = `${value.toLocaleString("ja-JP", { maximumFractionDigits: 0 })} ms`;
    }
    byId("total").textContent = `${(data.total_ms / 1000).toFixed(2)} 秒`;
    byId("used-settings").textContent = `この回答の検索設定：Top-K ${payload.top_k}`;
    byId("sources").replaceChildren();
    byId("scores").replaceChildren();
    byId("source-count").textContent = `${data.sources.length} 件`;
    data.sources.forEach((source, index) => {
      const card = document.createElement("article");
      card.className = "source";
      const title = document.createElement("strong");
      title.textContent = `${index + 1}. ${source.title}`;
      const meta = document.createElement("p");
      meta.textContent = source.source;
      card.append(title, meta);
      byId("sources").append(card);
      const score = document.createElement("p");
      score.className = "score-row";
      score.textContent = `${index + 1}. ${source.title} · ${Number(source.score).toFixed(4)}`;
      byId("scores").append(score);
    });
    if (!data.sources.length) byId("sources").textContent = "検索結果がありません。FAQの登録状況や検索条件を確認してください。";
    byId("empty").hidden = true;
    byId("output").hidden = false;
    byId("technical-result").hidden = false;
    byId("status").textContent = "完了";
  } catch (error) {
    const message = error.name === "AbortError"
      ? "応答待ちが120秒を超えました。サーバー側では処理が続いている可能性があります。ログを確認してください。"
      : error instanceof TypeError ? "APIに接続できません。サーバーの起動とネットワークを確認してください。" : error.message;
    byId("error").textContent = message;
    byId("error").hidden = false;
    byId("status").textContent = "エラー";
    if (byId("response-json").textContent === "応答を待っています…") byId("response-json").textContent = message;
  } finally {
    clearTimeout(timeout);
    busy = false;
    byId("submit").disabled = false;
    byId("result-panel").setAttribute("aria-busy", "false");
  }
});
