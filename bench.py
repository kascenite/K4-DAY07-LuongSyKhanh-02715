"""Benchmark truy xuat cho corpus Shopee (mục 3 REPORT_NHOM).

Moi thanh vien chi doi DUNG MOT DONG: bien CHUNKER ben duoi.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
import unicodedata
from pathlib import Path

from dotenv import load_dotenv

from src.chunking import FixedSizeChunker, RecursiveChunker, SentenceChunker  # noqa: F401
from src.models import Document
from src.store import EmbeddingStore

# ---------------------------------------------------------------- chien luoc
# >>> DONG DUY NHAT MOI THANH VIEN DOI <<<
CHUNKER = RecursiveChunker(chunk_size=500)
STRATEGY_NAME = "recursive (chunk_size=500)"
# ---------------------------------------------------------------------------

DATA_DIR = Path("data/ecommerce")
SKIP_FILES = {"return-refund-policy", "seller-warranty-policy"}
TOP_K = 3
CACHE_PATH = Path(".emb_cache.json")

QUESTIONS = [
    {
        "id": 1,
        "query": "Đơn hàng thực phẩm đông lạnh đã giao thành công 2 ngày trước, tôi đổi ý không muốn dùng nữa thì trả hàng được không?",
        "gold_docs": ["quy-dinh-chung-tra-hang-hoan-tien-buyer", "san-pham-han-che-tra-hang"],
        "must_contain": ["24 giờ", "không áp dụng lý do trả hàng"],
        "filter": None,
    },
    {
        "id": 2,
        "query": "Shop Voucher do Người bán phát hành có được hoàn lại khi yêu cầu Trả hàng/Hoàn tiền được chấp nhận không?",
        "gold_docs": ["quy-dinh-chung-tra-hang-hoan-tien-seller"],
        "must_contain": ["không được hoàn lại trong bất cứ trường hợp nào"],
        "filter": {"audience": "seller"},
    },
    {
        "id": 3,
        "query": "Tôi trả hàng bằng hình thức Tự sắp xếp, đơn không thuộc Shopee Mall, địa chỉ khác tỉnh với Người bán thì được hỗ trợ phí trả hàng bao nhiêu và trong bao lâu?",
        "gold_docs": ["phuong-thuc-phi-gui-hang-hoan-tra"],
        "must_contain": ["40,000 shopee xu", "3 - 5 ngày làm việc"],
        "filter": None,
    },
    {
        "id": 4,
        "query": "Khi gửi bằng chứng cho yêu cầu Trả hàng/Hoàn tiền, ảnh và video được phép dung lượng tối đa bao nhiêu?",
        "gold_docs": ["chuan-bi-bang-chung-tra-hang"],
        "must_contain": ["5mb", "100 mb"],
        "filter": None,
    },
    {
        "id": 5,
        "query": "Đơn hàng thanh toán bằng thẻ tín dụng thì bao lâu nhận được tiền hoàn?",
        "gold_docs": ["thoi-gian-nhan-tien-hoan"],
        "must_contain": ["7 - 14 ngày làm việc"],
        "filter": None,
    },
]


# ------------------------------------------------------------------ helpers
def norm(text: str) -> str:
    """Chuan hoa de so khop chuoi dac trung: NFC, thuong, gop khoang trang."""
    text = unicodedata.normalize("NFC", text).lower()
    text = text.replace("’", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", text)


def parse_frontmatter(raw: str) -> tuple[dict, str]:
    if not raw.startswith("---"):
        return {}, raw
    end = raw.find("\n---", 3)
    if end == -1:
        return {}, raw
    head, body = raw[3:end], raw[end + 4 :]
    meta = {}
    for line in head.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta, body.lstrip("\n")


def build_embedder():
    load_dotenv(override=False)
    provider = os.getenv("EMBEDDING_PROVIDER", "mock").strip().lower()
    if provider == "gemini":
        from src.embeddings import GeminiEmbedder

        backend = GeminiEmbedder()
    elif provider == "local":
        from src.embeddings import LocalEmbedder

        backend = LocalEmbedder()
    elif provider == "openai":
        from src.embeddings import OpenAIEmbedder

        backend = OpenAIEmbedder()
    else:
        from src.embeddings import _mock_embed

        backend = _mock_embed

    cache = json.loads(CACHE_PATH.read_text()) if CACHE_PATH.exists() else {}
    name = getattr(backend, "_backend_name", backend.__class__.__name__)

    def cached(text: str) -> list[float]:
        key = hashlib.md5(f"{name}|{text}".encode()).hexdigest()
        if key in cache:
            return cache[key]
        for attempt in range(5):
            try:
                vector = backend(text)
                break
            except Exception as exc:  # rate limit / loi mang -> lui dan roi thu lai
                if attempt == 4:
                    raise
                print(f"    retry {attempt + 1}/4 sau loi: {type(exc).__name__}", file=sys.stderr)
                time.sleep(2 * (attempt + 1))
        cache[key] = vector
        CACHE_PATH.write_text(json.dumps(cache))
        return vector

    return cached, name


def load_chunked_documents() -> tuple[list[Document], dict]:
    docs: list[Document] = []
    per_file: dict[str, int] = {}
    for path in sorted(DATA_DIR.glob("*.md")):
        if path.stem in SKIP_FILES:
            continue
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        chunks = CHUNKER.chunk(body)
        per_file[path.stem] = len(chunks)
        for i, chunk in enumerate(chunks):
            docs.append(
                Document(
                    id=f"{path.stem}#{i}",
                    content=chunk,
                    metadata={**meta, "doc_id": path.stem, "chunk_index": i},
                )
            )
    return docs, per_file


def show(results: list[dict]) -> None:
    for rank, result in enumerate(results, start=1):
        preview = re.sub(r"\s+", " ", result["content"])[:110]
        # LSK's EmbeddingStore.search doesn't return an "id" key (valid — tests
        # don't require it), so fall back to metadata for the display label.
        meta = result.get("metadata", {})
        label = result.get("id") or f"{meta.get('doc_id', '?')}#{meta.get('chunk_index', '?')}"
        print(f"    {rank}. score={result['score']:.4f}  {label}")
        print(f"       {preview}...")


def grade(question: dict, results: list[dict]) -> tuple[int, str]:
    if not results:
        return 0, "khong co ket qua"
    context = norm(" ".join(r["content"] for r in results))
    missing = [s for s in question["must_contain"] if norm(s) not in context]
    top_docs = [r["metadata"]["doc_id"] for r in results]
    gold = set(question["gold_docs"])
    hit_rank = next((i for i, d in enumerate(top_docs, start=1) if d in gold), None)

    if missing:
        return 0, f"ngu canh thieu: {missing}"
    if hit_rank is None:
        return 0, "khong co tai lieu gold trong top-3"
    if hit_rank == 1:
        return 2, "gold o top-1 + ngu canh tra loi duoc"
    return 1, f"gold o top-{hit_rank}"


def main() -> int:
    print("=" * 78)
    print(f"BENCHMARK — chien luoc: {STRATEGY_NAME}")
    print("=" * 78)

    docs, per_file = load_chunked_documents()
    embedder, backend_name = build_embedder()
    print(f"\nEmbedding backend : {backend_name}")
    print(f"So file           : {len(per_file)}")
    print(f"So chunk           : {len(docs)}")
    print("\nChunk / file:")
    for stem, count in sorted(per_file.items(), key=lambda kv: -kv[1]):
        print(f"  {count:3d}  {stem}")

    lengths = [len(d.content) for d in docs]
    print(f"\nDo dai chunk: min={min(lengths)} max={max(lengths)} avg={sum(lengths) / len(lengths):.0f}")

    print(f"\nDang nhung {len(docs)} chunk...")
    store = EmbeddingStore(collection_name="shopee_returns", embedding_fn=embedder)
    store.add_documents(docs)
    print(f"Store size: {store.get_collection_size()}")

    total = 0
    rows = []
    for question in QUESTIONS:
        print("\n" + "-" * 78)
        print(f"[Cau {question['id']}] {question['query']}")
        if question["filter"]:
            print(f"  metadata_filter = {question['filter']}")
        results = store.search_with_filter(question["query"], top_k=TOP_K, metadata_filter=question["filter"])
        show(results)
        points, note = grade(question, results)
        total += points
        rows.append((question["id"], points, note, [r["metadata"]["doc_id"] for r in results]))
        print(f"  => {points}/2 diem — {note}")

        # A/B bat buoc cho cau can filter
        if question["filter"]:
            print("\n  [A/B] chay lai KHONG filter:")
            no_filter = store.search_with_filter(question["query"], top_k=TOP_K, metadata_filter=None)
            show(no_filter)
            points_nf, note_nf = grade(question, no_filter)
            print(f"  => khong filter: {points_nf}/2 — {note_nf}")

    print("\n" + "=" * 78)
    print(f"TONG: {total}/10")
    for qid, points, note, docs_top in rows:
        print(f"  Cau {qid}: {points}/2  top3={docs_top}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
