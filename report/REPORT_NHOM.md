# Báo Cáo Nhóm — Lab 7: Embedding &amp; Vector Store

**Nhóm:** Studo.h (T114)
**Thành viên:** Văn Quốc Dũng, Nguyễn Đức Thịnh, Đào Quang Thái Anh, Lương Sỹ Khánh
**Ngày:** 20/09/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) &amp; Lý Do Chọn

**Chủ đề:** Chính sách Trả hàng/Hoàn tiền trên Shopee (help.shopee.vn) — đúng phạm vi K4-L3B (đổi trả / bảo hành / quy định người mua–người bán thương mại điện tử).

**Tại sao nhóm chọn chủ đề này?**

> Nhóm lấy bộ FAQ chính thức của Shopee vì đây là nguồn công khai, có cấu trúc mục/điều khoản, và chứa số liệu có thể kiểm chứng (thời hạn 15 ngày / 24 giờ, phản hồi 3–5 ngày làm việc, điều kiện “Đổi ý”, danh mục hạn chế trả hàng, phí hoàn trả, SPayLater). Các trang phủ trọn luồng người mua: điều kiện → bằng chứng → gửi yêu cầu → đóng gói/vận chuyển → theo dõi → nhận tiền hoàn, nên phù hợp để so sánh chunking và gắn metadata `audience`/`category`. Không dùng trang sau đăng nhập hay dữ liệu nội bộ.

**Cách thu thập:** Sao chép `scripts/urls.example.csv` thành `data/urls.csv` (11 URL Help Center), kiểm tra `https://help.shopee.vn/robots.txt` (`User-Agent: *` / `Allow: /`), rồi chạy crawler mẫu của repo:

```bash
python scripts/fetch_public_pages.py data/urls.csv --output-dir data/ecommerce --delay 1.0 --timeout 30 --overwrite
```

Kết quả crawl: **11 saved, 0 skipped**. Sau đó tách bài 188931 (`audience: both`) thành **2 file** `buyer` / `seller` theo `day7-lab-data-foundations.md`: nếu để chung một file thì `metadata_filter={"audience":"buyer"}` không lọc được vì hai đáp án nằm cùng tài liệu. Mỗi file `.md` UTF-8 có YAML front matter; kiểm kê tại `data/ecommerce/sources.csv`. User-Agent: `Day7DataFoundationsCourse/1.0 (+educational-lab)`. `document_version` để `not-stated` vì nguồn không nêu số hiệu phiên bản.

### Danh sách tài liệu (Data Inventory)

Corpus dùng cho benchmark: **12 file** trong `data/ecommerce/` (11 URL Help Center; bài 188931 tách thành 2 audience). Không tính 2 file khởi động `return-refund-policy.md` / `seller-warranty-policy.md` vì vẫn là template `example.com`. Số ký tự = phần nội dung sau front matter.


| #   | Tên tài liệu                                                     | Nguồn (Source URL)                                                                               | Ngày lấy / Phiên bản    | Số ký tự | Metadata đã gán                                                                                                |
| --- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | ----------------------- | -------- | -------------------------------------------------------------------------------------------------------------- |
| 1   | Những điều cần biết về Trả hàng do Đổi ý/không còn nhu cầu       | [https://help.shopee.vn/portal/4/article/204305](https://help.shopee.vn/portal/4/article/204305) | 2026-09-20 / not-stated | 7371     | `doc_id=doi-y-khong-con-nhu-cau`; `audience=buyer`; `category=returns-policy`; `language=vi`                   |
| 2a  | Quy định Trả hàng/Hoàn tiền dành cho Người mua                   | [https://help.shopee.vn/portal/4/article/188931](https://help.shopee.vn/portal/4/article/188931) | 2026-09-20 / not-stated | 5886     | `doc_id=quy-dinh-chung-tra-hang-hoan-tien-buyer`; `audience=buyer`; `category=returns-policy`; `language=vi`   |
| 2b  | Quy định Trả hàng/Hoàn tiền dành cho Người bán                   | [https://help.shopee.vn/portal/4/article/188931](https://help.shopee.vn/portal/4/article/188931) | 2026-09-20 / not-stated | 1472     | `doc_id=quy-dinh-chung-tra-hang-hoan-tien-seller`; `audience=seller`; `category=returns-policy`; `language=vi` |
| 3   | Sản phẩm hạn chế trả hàng là gì                                  | [https://help.shopee.vn/portal/4/article/79465](https://help.shopee.vn/portal/4/article/79465)   | 2026-09-20 / not-stated | 1463     | `doc_id=san-pham-han-che-tra-hang`; `audience=buyer`; `category=restricted-returns`; `language=vi`             |
| 4   | Hướng dẫn chuẩn bị bằng chứng khi yêu cầu Trả hàng/Hoàn tiền     | [https://help.shopee.vn/portal/4/article/79467](https://help.shopee.vn/portal/4/article/79467)   | 2026-09-20 / not-stated | 3469     | `doc_id=chuan-bi-bang-chung-tra-hang`; `audience=buyer`; `category=return-evidence`; `language=vi`             |
| 5   | Hướng dẫn gửi yêu cầu Trả hàng/Hoàn tiền                         | [https://help.shopee.vn/portal/4/article/79233](https://help.shopee.vn/portal/4/article/79233)   | 2026-09-20 / not-stated | 2518     | `doc_id=gui-yeu-cau-tra-hang-hoan-tien`; `audience=buyer`; `category=return-request`; `language=vi`            |
| 6   | Các phương thức gửi hàng hoàn trả và phí hoàn trả                | [https://help.shopee.vn/portal/4/article/189477](https://help.shopee.vn/portal/4/article/189477) | 2026-09-20 / not-stated | 5930     | `doc_id=phuong-thuc-phi-gui-hang-hoan-tra`; `audience=buyer`; `category=return-shipping`; `language=vi`        |
| 7   | Cách đóng gói đơn hàng hoàn trả                                  | [https://help.shopee.vn/portal/4/article/79508](https://help.shopee.vn/portal/4/article/79508)   | 2026-09-20 / not-stated | 3618     | `doc_id=dong-goi-don-hang-hoan-tra`; `audience=buyer`; `category=return-packaging`; `language=vi`              |
| 8   | Cách theo dõi tình trạng vận chuyển hàng hoàn trả                | [https://help.shopee.vn/portal/4/article/189476](https://help.shopee.vn/portal/4/article/189476) | 2026-09-20 / not-stated | 975      | `doc_id=theo-doi-van-chuyen-hang-hoan-tra`; `audience=buyer`; `category=return-tracking`; `language=vi`        |
| 9   | Hướng dẫn Người mua trả lời đề xuất Hoàn Tiền Ngay của Người bán | [https://help.shopee.vn/portal/4/article/190387](https://help.shopee.vn/portal/4/article/190387) | 2026-09-20 / not-stated | 1360     | `doc_id=tra-loi-de-xuat-hoan-tien-ngay`; `audience=buyer`; `category=instant-refund`; `language=vi`            |
| 10  | Làm sao để kiểm tra tiền đã hoàn vào SPayLater hay chưa          | [https://help.shopee.vn/portal/4/article/164831](https://help.shopee.vn/portal/4/article/164831) | 2026-09-20 / not-stated | 5933     | `doc_id=kiem-tra-hoan-tien-spaylater`; `audience=buyer`; `category=refund-spaylater`; `language=vi`            |
| 11  | Thời gian nhận tiền hoàn và cách kiểm tra tiền hoàn              | [https://help.shopee.vn/portal/4/article/189473](https://help.shopee.vn/portal/4/article/189473) | 2026-09-20 / not-stated | 3898     | `doc_id=thoi-gian-nhan-tien-hoan`; `audience=buyer`; `category=refund-timeline`; `language=vi`                 |


**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**

- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ. (`robots.txt` cho phép; không đăng nhập; không CAPTCHA; chỉ HTML Help Center.)
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata. (`retrieved_at=2026-09-20`; `document_version=not-stated`; khớp 1-1 với `data/ecommerce/sources.csv`.)

**Ghi chú cho retrieval:** `audience` có 2 giá trị (`buyer` / `seller`). File buyer giữ thời hạn gửi yêu cầu (24 giờ / 15 ngày / 20 ngày) và hoàn mã Shopee/Xu; file seller giữ Shop Voucher **không được Shopee hoàn** và quyết định hàng hạn chế trả. Cùng nguồn 188931 nhưng đáp án khác nhau — `metadata_filter={"audience": "buyer"}` (hoặc `"seller"`) mới tách được. Không bịa thời hạn xử lý 30 ngày cho seller vì nguồn không nêu. `category` tách các bước trong luồng trả hàng (policy, evidence, shipping, refund).

### Cấu trúc Metadata (Metadata Schema)


| Trường metadata    | Kiểu              | Ví dụ giá trị                                           | Tại sao hữu ích cho truy xuất (retrieval)?                                                                                                                                                   |
| ------------------ | ----------------- | ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `doc_id`           | string (slug)     | `quy-dinh-chung-tra-hang-hoan-tien-buyer`               | Định danh ổn định khi ingest / `delete_document()`; trùng tên file.                                                                                                                          |
| `title`            | string            | `Thời gian nhận tiền hoàn và cách kiểm tra tiền hoàn`   | Giúp người đọc/agent nhận đúng văn bản nguồn khi trích dẫn.                                                                                                                                  |
| `source_url`       | URL               | `https://help.shopee.vn/portal/4/article/188931`        | Truy vết gold answer về đúng trang Shopee, không dùng link tìm kiếm.                                                                                                                         |
| `retrieved_at`     | date `YYYY-MM-DD` | `2026-09-20`                                            | Kiểm tra độ mới của corpus khi chính sách Help Center đổi.                                                                                                                                   |
| `document_version` | string            | `not-stated`                                            | Chừa chỗ cho ngày hiệu lực; không bịa số hiệu nếu nguồn không nêu.                                                                                                                           |
| `audience`         | enum              | `buyer` | `seller`                                      | Lọc đúng đối tượng. Câu benchmark không nêu người hỏi cần `metadata_filter={"audience": "buyer"}` (hoặc `"seller"`) kẻo lẫn thời hạn 15 ngày của buyer với quy định Shop Voucher của seller. |
| `category`         | string            | `returns-policy`, `return-evidence`, `refund-spaylater` | Lọc theo bước quy trình (điều kiện / bằng chứng / vận chuyển / hoàn tiền) khi câu hỏi cùng chủ đề “trả hàng”.                                                                                |
| `language`         | string            | `vi`                                                    | Đánh dấu corpus tiếng Việt; tránh lẫn tài liệu mẫu tiếng Anh trong `data/`.                                                                                                                  |


---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `bench.py --all` với model nhúng thực tế `text-embedding-3-small` (OpenAI) lưu trữ trên **ChromaDB Vector Store** (`_HAS_CHROMA = True`):

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Tổng điểm (/10) | Giữ được ngữ cảnh không? |
| --- | --- | --- | --- | --- | --- |
| Shopee Corpus (12 files) | FixedSizeChunker (`fixed_size`, size=500, overlap=50) | 99 | 477 | **3/10** | 🔴 Kém - Cắt cứng tại mốc 500 ký tự làm đứt câu chứa cụm từ mốc thời gian quy định. |
| Shopee Corpus (12 files) | SentenceChunker (`by_sentences`, max_sentences=3) | 80 | 531 | **8/10** | 🟢 Xuất sắc - Giữ nguyên vẹn ranh giới câu, đạt điểm tuyệt đối 2/2 tại các câu 2, 3, 4, 5. |
| Shopee Corpus (12 files) | RecursiveChunker (`recursive`, size=500) | 107 | 399 | **6/10** | 🟢 Tốt - Bảo toàn đoạn văn bản Markdown, đạt 2/2 điểm ở các câu 2, 3, 4. |
| Shopee Corpus (12 files) | SemanticChunker (`semantic`, thresh=0.5, max=500) | 229 | 185 | **4/10** | 🟡 Trung bình - Tách theo độ tương đồng làm vụn văn bản (trung bình 185 ký tự), mất cụm từ kiểm chứng. |

### Phương pháp Đánh giá Khách quan với `must_contain` (Deterministic Context Evaluation)

> 🔴 **ĐIỂM NHẤN QUAN TRỌNG VỀ PHƯƠNG PHÁP ĐÁNH GIÁ:**
> Thay vì cho LLM Agent tự sinh câu trả lời rồi tự đối chiếu (phương pháp dễ bị ảo giác - hallucination, phụ thuộc vào prompt và thiếu tính tái tạo), hệ thống Benchmark áp dụng phương pháp **kiểm tra định tính cứng bằng tập cụm từ bắt buộc (`must_contain`)**:
> 1. Hàm `grade(question, results)` kiểm tra xem **tất cả cụm từ từ khóa trong `must_contain`** (ví dụ `"40,000 shopee xu"`, `"3 - 5 ngày làm việc"`, `"7 - 14 ngày làm việc"`, `"5mb"`, `"100 mb"`) có xuất hiện nguyên vẹn trong top-3 ngữ cảnh trích xuất hay không.
> 2. Đánh giá xếp hạng tài liệu chuẩn (`gold_docs`): Đạt **2/2 điểm** nếu tài liệu chuẩn nằm ở **Top-1** và chứa đầy đủ `must_contain`; đạt **1/2 điểm** nếu tài liệu nằm ở **Top-2/Top-3**; đạt **0/2 điểm** nếu thiếu từ khóa hoặc không có gold doc trong Top-3.

### Chiến lược của từng thành viên

**Thành viên 1 — Văn Quốc Dũng**

- **Loại chiến lược:** FixedSize (`FixedSizeChunker`, `chunk_size=500`, `overlap=50`)
- **Kết quả Benchmark:** **3/10 điểm** (Câu 2 đạt 2/2 điểm; Câu 4 đạt 1/2 điểm với Gold Doc ở Top-2).
- **Mô tả & lý do chọn cho chủ đề này:** Làm đường cơ sở (baseline) chuẩn cố định để so sánh với các phương pháp linh hoạt.
- **Code snippet:**
```python
from src.chunking import FixedSizeChunker

chunker = FixedSizeChunker(chunk_size=500, overlap=50)
chunks = chunker.chunk(body)
```

**Thành viên 2 — Nguyễn Đức Thịnh**

- **Loại chiến lược:** SentenceChunker (`SentenceChunker`, `max_sentences_per_chunk=3`)
- **Kết quả Benchmark:** **8/10 điểm** (Đạt tuyệt đối 2/2 điểm ở cả 4 câu: Câu 2, Câu 3, Câu 4, Câu 5).
- **Mô tả & lý do chọn:** Nhắm vào đặc thù văn bản FAQ Shopee gồm các điều khoản viết thành từng câu hoàn chỉnh. Gom 3 câu giúp giữ nguyên vẹn trọn vẹn ngữ nghĩa của từng quy định.
- **Code snippet:**
```python
class SentenceChunker:
    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip())]
        sentences = [s for s in sentences if s]

        n = self.max_sentences_per_chunk
        return [" ".join(sentences[i : i + n]) for i in range(0, len(sentences), n)]
```

**Thành viên 3 — Lương Sỹ Khánh**

- **Loại chiến lược:** RecursiveChunker (`RecursiveChunker`, `chunk_size=500`)
- **Kết quả Benchmark:** **6/10 điểm** (Đạt tuyệt đối 2/2 điểm ở Câu 2, Câu 3, Câu 4).
- **Mô tả & lý do chọn:** Phù hợp với định dạng Markdown của Shopee (chứa tiêu đề, danh sách). Tách theo ranh giới phân cấp `["\n\n", "\n", ". ", " ", ""]`.
- **Code snippet:**
```python
class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        text = current_text
        if not text:
            return []
        # Base case 1: da vua kich thuoc, khong can cat them.
        if len(text) <= self.chunk_size:
            return [text]
        # Base case 2: het separator (hoac separator rong) -> cat cung theo do dai.
        if not remaining_separators or remaining_separators[0] == "":
            return self._hard_split(text)

        separator = remaining_separators[0]
        rest = remaining_separators[1:]
        parts = [p for p in text.split(separator) if p]
        # Base case 3: separator khong xuat hien -> ha xuong separator nho hon.
        if len(parts) <= 1:
            return self._split(text, rest)

        # Di xuong: manh nao con dai hon chunk_size thi cat tiep bang separator nho hon.
        pieces: list[str] = []
        for part in parts:
            if len(part) <= self.chunk_size:
                pieces.append(part)
            else:
                pieces.extend(self._split(part, rest))

        return self._merge(pieces, separator)

    def _hard_split(self, text: str) -> list[str]:
        size = max(1, self.chunk_size)
        return [text[i : i + size] for i in range(0, len(text), size)]

    def _merge(self, pieces: list[str], separator: str) -> list[str]:
        """Gom cac manh nho lien ke lai cho toi sat chunk_size."""
        merged: list[str] = []
        buffer = ""
        for piece in pieces:
            candidate = piece if not buffer else buffer + separator + piece
            if len(candidate) <= self.chunk_size:
                buffer = candidate
                continue
            if buffer:
                merged.append(buffer)
            buffer = piece
        if buffer:
            merged.append(buffer)
        return merged
```

**Thành viên 4 — Đào Quang Thái Anh**

- **Loại chiến lược:** SemanticChunker (`SemanticChunker`, `similarity_threshold=0.5`, `max_chunk_size=500`)
- **Kết quả Benchmark:** **4/10 điểm** (Đạt 2/2 điểm ở Câu 2 và Câu 3).
- **Mô tả & lý do chọn:** Gom các câu có điểm tương đồng Cosine cao dựa trên embedding vector `text-embedding-3-small`.
- **Code snippet:**
```python
class SemanticChunker:
    """
    Split text based on semantic similarity of consecutive sentences.

    Method:
        1. Break text into sentences.
        2. Embed each sentence using an embedding function.
        3. Compute cosine similarity between adjacent sentences.
        4. Group adjacent sentences into the same chunk as long as similarity
           is above `similarity_threshold` and chunk length does not exceed `max_chunk_size`.
    """

    def __init__(
        self,
        similarity_threshold: float = 0.5,
        max_chunk_size: int = 500,
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self.similarity_threshold = similarity_threshold
        self.max_chunk_size = max_chunk_size
        from .embeddings import _mock_embed

        self.embedding_fn = embedding_fn or _mock_embed

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        sentence_chunker = SentenceChunker(max_sentences_per_chunk=1)
        sentences = sentence_chunker.chunk(text)

        if not sentences:
            return []
        if len(sentences) == 1:
            return sentences

        embeddings = [self.embedding_fn(s) for s in sentences]
        similarities = [
            compute_similarity(embeddings[i], embeddings[i + 1])
            for i in range(len(sentences) - 1)
        ]

        chunks: list[str] = []
        current_sentences = [sentences[0]]

        for i, sim in enumerate(similarities):
            next_sentence = sentences[i + 1]
            combined_candidate = " ".join(current_sentences + [next_sentence])

            if sim >= self.similarity_threshold and len(combined_candidate) <= self.max_chunk_size:
                current_sentences.append(next_sentence)
            else:
                chunks.append(" ".join(current_sentences))
                current_sentences = [next_sentence]

        if current_sentences:
            chunks.append(" ".join(current_sentences))

        return chunks
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
| --- | --- | --- | --- | --- |
| Văn Quốc Dũng | FixedSizeChunker | 3/10 | Đơn giản, kích thước cố định. | Cắt ngang ranh giới câu làm thiếu cụm từ kiểm chứng `must_contain` ở Câu 3 & 5. |
| Nguyễn Đức Thịnh | SentenceChunker | **8/10** | Giữ trọn vẹn ranh giới câu; ngữ cảnh chứa đầy đủ từ khóa `must_contain` ở 4/5 câu. | Độ dài chunk không đồng đều (min=51, max=2361). |
| Lương Sỹ Khánh | RecursiveChunker | 6/10 | Tôn trọng cấu trúc đoạn Markdown (~399 ký tự/chunk), đạt 2/2 điểm ở 3 câu. | Bị thiếu cụm `"7 - 14 ngày làm việc"` ở Câu 5 khi tách theo đoạn. |
| Đào Quang Thái Anh | SemanticChunker | 4/10 | Gom cụm câu theo ngữ nghĩa tự nhiên. | Tạo ra quá nhiều chunk vụn (229 chunks, trung bình 185 ký tự), làm đứt đoạn từ khóa như `"100 mb"`. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**

> **`SentenceChunker` là chiến lược hiệu quả nhất (đạt 8/10 điểm)** trên tập tài liệu Shopee FAQ. Do quy định thương mại điện tử chứa các thông số kỹ thuật và thời hạn pháp lý (như `"40,000 shopee xu"`, `"3 - 5 ngày làm việc"`, `"5mb"`, `"100 mb"`), việc giữ nguyên ranh giới câu ngăn không cho các mốc số liệu này bị cắt ngang hay chia rẽ qua các chunk khác nhau.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Cụm từ bắt buộc (`must_contain`) | Tài liệu Gold (`gold_docs`) |
|---|-------|-------------------------------|--------------------------|
| 1 | Đơn hàng thực phẩm đông lạnh đã giao thành công 2 ngày trước, tôi đổi ý không muốn dùng nữa thì trả hàng được không? | `["24 giờ", "không áp dụng lý do trả hàng"]` | `quy-dinh-chung-tra-hang-hoan-tien-buyer`, `san-pham-han-che-tra-hang` |
| 2 | Shop Voucher do Người bán phát hành có được hoàn lại khi yêu cầu Trả hàng/Hoàn tiền được chấp nhận không? | `["không được hoàn lại trong bất cứ trường hợp nào"]` | `quy-dinh-chung-tra-hang-hoan-tien-seller` (với `metadata_filter={"audience": "seller"}`) |
| 3 | Tôi trả hàng bằng hình thức “Tự sắp xếp”, đơn không thuộc Shopee Mall, địa chỉ của tôi khác tỉnh với Người bán — được hỗ trợ phí trả hàng bao nhiêu và trong bao lâu? | `["40,000 shopee xu", "3 - 5 ngày làm việc"]` | `phuong-thuc-phi-gui-hang-hoan-tra` |
| 4 | Khi gửi bằng chứng cho yêu cầu Trả hàng/Hoàn tiền, ảnh và video được phép dung lượng tối đa bao nhiêu, và nếu Shopee yêu cầu bổ sung thì tôi có bao lâu? | `["5mb", "100 mb"]` | `chuan-bi-bang-chung-tra-hang` |
| 5 | Đơn hàng thanh toán bằng thẻ tín dụng thì bao lâu nhận được tiền hoàn, so với Ví ShopeePay? | `["7 - 14 ngày làm việc"]` | `thoi-gian-nhan-tien-hoan` |

### Tổng hợp kết quả đánh giá theo `must_contain` (Log chạy thực tế với OpenAI `text-embedding-3-small` & ChromaDB)

| # | Câu hỏi | FixedSize (3/10) | Sentence (8/10) | Recursive (6/10) | Semantic (4/10) | Nguyên nhân & Ghi chú |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Thực phẩm đông lạnh đổi ý | 0/2 (thiếu mốc 24h & hạn chế) | 0/2 (thiếu mốc 24h & hạn chế) | 0/2 (thiếu điều kiện hạn chế) | 0/2 (thiếu mốc 24h & hạn chế) | Đa tài liệu (vừa cần file quy định chung vừa cần file sản phẩm hạn chế trả hàng). |
| 2 | Hoàn Shop Voucher Người bán | **2/2** (Gold Top-1) | **2/2** (Gold Top-1) | **2/2** (Gold Top-1) | **2/2** (Gold Top-1) | 🎯 Đạt 2/2 điểm nhờ `metadata_filter={"audience": "seller"}` lọc đúng tài liệu Seller trên ChromaDB. |
| 3 | Phí tự sắp xếp khác tỉnh | 0/2 (thiếu 3-5 ngày) | **2/2** (Gold Top-1) | **2/2** (Gold Top-1) | **2/2** (Gold Top-1) | `SentenceChunker` & `RecursiveChunker` giữ trọn vẹn cụm `"40,000 shopee xu"` và `"3 - 5 ngày làm việc"`. |
| 4 | Dung lượng ảnh/video bằng chứng | 1/2 (Gold Top-2) | **2/2** (Gold Top-1) | **2/2** (Gold Top-1) | 0/2 (thiếu `"100 mb"`) | `SentenceChunker` & `RecursiveChunker` chứa đủ cả `"5mb"` và `"100 mb"`. `SemanticChunker` cắt quá vụn làm rách mốc 100MB. |
| 5 | Thời gian hoàn tiền thẻ tín dụng | 0/2 (thiếu 7-14 ngày) | **2/2** (Gold Top-1) | 0/2 (thiếu 7-14 ngày) | 0/2 (thiếu 7-14 ngày) | Chỉ `SentenceChunker` giữ nguyên dòng bảng trích xuất đủ cụm từ `"7 - 14 ngày làm việc"`. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**

> Lọc bằng metadata đóng vai trò quyết định ở **Câu hỏi số 2**. Bài viết quy định chung (URL 188931) gồm cả phần dành cho Người mua lẫn Người bán; nếu không pre-filter `metadata_filter={"audience": "seller"}`, kết quả tìm kiếm vector bị nhiễu bởi phần dành cho Buyer (vốn ghi mã giảm giá Shopee *được hoàn*). Nhờ pre-filtering trên ChromaDB, hệ thống lọc chính xác tài liệu Seller và kiểm tra khớp 100% cụm từ `must_contain`: `"không được hoàn lại trong bất cứ trường hợp nào"`.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

1. **Phương pháp Đánh giá Khách quan bằng `must_contain`:** Đánh giá RAG thông qua kiểm tra cụm từ bắt buộc (`must_contain`) trực tiếp trên ngữ cảnh trích xuất thay vì để LLM tự chấm, loại bỏ hoàn toàn hiện tượng ảo giác (hallucination) và đảm bảo kết quả benchmark 100% tái tạo được.
2. **Sự cần thiết của Metadata Pre-filtering trên Vector DB:** Đảm bảo độ chính xác khi truy xuất các tài liệu cùng nguồn URL nhưng khác đối tượng áp dụng (`buyer` vs `seller`).
3. **Ưu thế của SentenceChunker với văn bản pháp lý/FAQ:** Bảo toàn nguyên vẹn ranh giới câu giúp giữ trọn vẹn các thông số mốc thời gian và chi phí mà không bị cắt đứt đoạn.

**Bài học rút ra khi so sánh trong nhóm:**

> Model nhúng mạnh (`text-embedding-3-small`) kết hợp với ChromaDB Vector DB giúp tăng mạnh điểm số retrieval (SentenceChunker tăng từ 2/10 lên 8/10 so với mock), nhưng ranh giới chunking (`SentenceChunker`) vẫn là yếu tố quyết định để chứa đủ cụm từ kiểm chứng `must_contain`.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**

> Nhóm sẽ phát triển cơ chế **Hybrid Markdown Chunking** (kết hợp lưu Heading Context vào từng Sentence Chunk) để giải quyết dứt điểm Câu hỏi 1 (câu hỏi đa tài liệu cần liên kết thông tin giữa mốc thời gian 24 giờ và danh mục hàng hạn chế).

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
| ---------------------------------------- | ---------------- |
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |

