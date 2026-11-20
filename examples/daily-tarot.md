# Example: Daily Tarot (deterministic demonstration)

This is an **archived v1.1 output snapshot**. The current v1.2 script retains the same `schema_version` and same seeded card, but the new `tool_version` reports `1.2.0`. It is **not** a personal reading and **not** the outcome of an unseeded daily draw.

```bash
python scripts/draw.py tarot --count 1 --seed 2026
```

Relevant output fields (timestamp omitted for readability):

```json
{
  "schema_version": "1.1",
  "tool_version": "1.1.0",
  "method": "Rider-Waite-Smith card names, sampled without replacement",
  "cards": [
    {"id":"rws-15","card":"The Devil","card_zh":"恶魔","orientation":"upright"}
  ],
  "provenance": {
    "source": "seeded_demo",
    "seed": 2026,
    "payload_sha256": "3af4bd2666d987fb494486081b9213fa7d1783571b7f02b17e79cae1b8a114d8"
  }
}
```

Illustrative reply: "这是一个**固定种子演示**，不是今天随机抽出的牌。示例牌是恶魔（正位），传统上可象征习惯与束缚。今天可以观察一件让你觉得被推着走的事，问自己是否真的有选择。"

The SHA-256 is an **outcome checksum**, not an authenticity or randomness certificate.
