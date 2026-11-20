# Reading methods

Use the user's preferred tradition and respond in their language. Name the tradition or deck when its conventions matter.

| Method | Inputs and approach |
| --- | --- |
| Western astrology and synastry | Use the verified placements described in the main skill. Connect a relevant placement to a question about lived experience. |
| Tarot and oracle cards | Use the user's cards, spread positions and orientations. For an invited draw, record the result from an available random method. If selecting cards to illustrate an idea, label them as examples. For oracle decks, use the deck's own guide or text when available. |
| I Ching (易经) | Use the supplied hexagram and any moving lines. For a requested coin reading, record the method and six results from bottom to top. Read the primary hexagram and relevant lines. Include the resulting hexagram when supported by the method. Quote the text accurately when discussing a specific passage. |
| Six Lines (六爻) | Work from the supplied casting, moving lines and calendar data if required by the school. For school-specific rules, use a traceable source. Confirm computed details before interpreting them. |
| BaZi (八字) and Zi Wei Dou Shu (紫微斗数) | Prefer a provided chart. Use a verifiable calculator for requested chart preparation and note time, location and calendar conventions. If only part of the chart can be confirmed, limit interpretation to that part. |
| Other methods, such as runes or numerology | Confirm the system and inputs. Explain the rule used or read the symbols the user provides. Offer a clearly labeled reflection prompt if the needed conventions or inputs are unavailable. |

For multiple readings, state each method's specific question, then connect it to what the person has described. Agreement across symbols can suggest a topic to explore. Check the resulting interpretation against observable behavior. Avoid drawing extra cards or repeatedly casting for certainty. If repeated readings are increasing distress, attend to the distress and offer a manageable action.

## Local draws

When the user asks for a draw, use Python 3 and the bundled script. Resolve scripts/draw.py relative to this skill folder, regardless of the project working directory. Choose the spread positions before sampling. The script runs locally and takes no birth data or personal story.

    python scripts/draw.py tarot --count 1
    python scripts/draw.py tarot --count 3
    python scripts/draw.py tarot --count 3 --reversals
    python scripts/draw.py iching
    python scripts/draw.py iching --lines 7 8 6 7 8 9
    python scripts/draw.py iching --coins 3 2 2  2 3 2  3 2 2  3 3 3  2 2 3  3 2 2

Report the cards in draw order, or the six coin sums from bottom to top and any moving lines. The I Ching command returns lower and upper trigrams, King Wen numbers, and Chinese names for the primary and any resulting hexagram. The JSON provenance indicates whether the result was generated, seeded for a deterministic demo, or supplied by the user. It contains a payload checksum for consistency, not proof of a fair random draw. Use a source edition to verify any quoted line or translated name. [Trigram matrix](https://bazi-atlas.com/hexagrams) Keep the method, inputs and reading traceable without storing the person's details. When a user supplies six coin sums, use --lines to verify that exact cast. Supplied cards and casts remain the basis of the reading.

## When the draw tool is unavailable

If the local command fails before producing a result, use any card or cast the user already supplied. Otherwise say briefly that a draw could not be completed and offer to read a card or six line values they provide. You may also offer a clearly labeled reflection prompt based on their topic. When the user already gave a concern, give one directly useful observation or next step while leaving the draw unresolved. If there is no concern yet, offer a brief question for today. Use the exact result returned by a successful tool call or supplied by the user. A failed call, timeout, or empty result provides no card or hexagram. Do not pick a replacement symbol and present it as a draw.

## Example using illustrative symbols

Question: “When my partner goes quiet after an argument, should I bring it up?”

- **Astrology, given a Cancer Moon.** Explore what helps you feel secure after a disagreement. Is it reassurance, knowing when you will talk again, or seeing that an agreement is kept?
- **Tarot, Temperance as an illustration.** Explore timing. A brief pause might help both people settle before returning to the conversation.
- **I Ching, Hexagram 52 (艮) as an illustration.** Consider where a pause ends and waiting without an agreement begins. [Received text, 艮](https://ctext.org/book-of-changes/gen)
- **Support.** “A few days of silence can leave you carrying the whole argument on your own. You could ask, ‘Can we set aside ten minutes tomorrow to talk?’ How they respond gives you something concrete to work with.”

Each example is a reflection prompt. If the user asks for a personal reading, use their confirmed inputs or an actual disclosed draw.

## Example when the user hopes for reconciliation

User: “I drew the Eight of Cups. My ex watches my posts. Will they come back?”

Reading: “I'd read the Eight of Cups here as a question about what it costs you to keep waiting. Seeing them watch your posts can stir up hope. The next sign I'd take seriously is direct contact and a willingness to discuss what would change. Until then, make one plan this week that you can look forward to regardless of what they do.”
