from __future__ import annotations

import re
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Iterable

STOPWORDS = {
    "the",
    "and",
    "for",
    "that",
    "with",
    "this",
    "from",
    "your",
    "you",
    "are",
    "was",
    "but",
    "have",
    "has",
    "not",
    "what",
    "when",
    "where",
    "who",
    "why",
    "how",
    "about",
    "into",
    "just",
    "like",
    "episode",
    "podcast",
    "show",
    "raw",
}

PLATFORM_TEMPLATES = {
    "facebook": {
        "headline": "Big moments from {title}",
        "cta": "Drop your favorite moment in the comments and share this with someone who needs the take.",
        "length_hint": "best for discovery-friendly, conversational posts",
    },
    "instagram": {
        "headline": "{title} is live",
        "cta": "Save this for later, tag a friend, and check the highlight reel.",
        "length_hint": "best for short captions, Reels hooks, and tight hashtag sets",
    },
    "youtube": {
        "headline": "{title} | {guest}",
        "cta": "Watch for the full conversation, then comment with the timestamp that hit hardest.",
        "length_hint": "best for searchable titles, clean descriptions, and chapter-style notes",
    },
}


@dataclass(frozen=True)
class EpisodeInput:
    title: str
    guest: str
    topics: str
    highlights: str
    quotes: str
    cta: str
    direction: str
    platform: str
    tone: str
    transcript_text: str


def _split_lines(value: str) -> list[str]:
    return [line.strip() for line in re.split(r"[\n\r,;]+", value) if line.strip()]


def _keywords_from_text(*values: str, limit: int = 6) -> list[str]:
    words: list[str] = []
    for value in values:
        words.extend(re.findall(r"[A-Za-z][A-Za-z0-9']+", value.lower()))

    filtered = [word for word in words if word not in STOPWORDS and len(word) > 2]
    if not filtered:
        return []

    counts = Counter(filtered)
    return [word for word, _ in counts.most_common(limit)]


def _normalize(value: str, fallback: str) -> str:
    cleaned = re.sub(r"\s+", " ", value or "").strip()
    return cleaned or fallback


def _build_episode_payload(form: dict, transcript_text: str) -> EpisodeInput:
    return EpisodeInput(
        title=_normalize(form.get("title", ""), "Serving It Up Raw"),
        guest=_normalize(form.get("guest", ""), "the host"),
        topics=_normalize(form.get("topics", ""), "conversation highlights"),
        highlights=_normalize(form.get("highlights", ""), "best moments from the episode"),
        quotes=_normalize(form.get("quotes", ""), "memorable quotes and reactions"),
        cta=_normalize(form.get("cta", ""), "Listen, watch, and share the episode."),
        direction=_normalize(form.get("direction", ""), "warm, punchy, and conversational"),
        platform=_normalize(form.get("platform", ""), "all"),
        tone=_normalize(form.get("tone", ""), "warm and conversational"),
        transcript_text=_normalize(transcript_text, ""),
    )


def _variant_hooks(base_title: str, guest: str, keywords: Iterable[str]) -> list[str]:
    keyword_list = list(keywords)
    keyword_phrase = ", ".join(keyword_list[:3]) if keyword_list else "the best moments"
    return [
        f"{base_title}: the moments everyone will be talking about",
        f"{guest} gets into {keyword_phrase}",
        f"A raw, funny, and real conversation from {base_title}",
    ]


def _build_platform_pack(platform: str, episode: EpisodeInput, transcript_keywords: list[str]) -> dict:
    template = PLATFORM_TEMPLATES.get(platform, PLATFORM_TEMPLATES["facebook"])
    title = episode.title
    guest = episode.guest
    keyword_phrase = ", ".join(transcript_keywords[:4]) if transcript_keywords else episode.topics
    highlight_lines = _split_lines(episode.highlights)
    quote_lines = _split_lines(episode.quotes)

    hooks = _variant_hooks(title, guest, transcript_keywords)
    descriptions = [
        f"{template['headline'].format(title=title, guest=guest)}\n\n{episode.direction}. {episode.cta}",
        f"{guest} and the team break down {keyword_phrase}. {episode.cta}",
        f"If you want the quick-hit version of {title}, start here: {hooks[0]}. {episode.cta}",
    ]

    hashtags = [f"#{word.replace(' ', '')[:24].title()}" for word in transcript_keywords[:8]]
    hashtags.append("#ServingItUpRaw")
    hashtags.append("#PodcastHighlights")

    youtube_title_variants = [
        template["headline"].format(title=title, guest=guest),
        f"{title}: {keyword_phrase[:60].title()}",
        f"{guest} on {keyword_phrase[:60].title()} | Serving It Up Raw",
    ]

    return {
        "platform": platform,
        "lengthHint": template["length_hint"],
        "headline": template["headline"].format(title=title, guest=guest),
        "hooks": hooks,
        "descriptions": descriptions,
        "hashtags": hashtags,
        "highlightHooks": [
            f"Highlight: {line}" for line in (highlight_lines or [episode.highlights])
        ],
        "quotes": quote_lines or [episode.quotes],
        "youtubeTitles": youtube_title_variants,
        "metadata": {
            "tone": episode.tone,
            "direction": episode.direction,
            "keywords": transcript_keywords,
        },
    }


def generate_copy_pack(form: dict, transcript_text: str) -> dict:
    episode = _build_episode_payload(form, transcript_text)
    transcript_keywords = _keywords_from_text(
        episode.title,
        episode.guest,
        episode.topics,
        episode.highlights,
        episode.quotes,
        episode.direction,
        episode.transcript_text,
        limit=10,
    )

    requested_platform = episode.platform.lower()
    platforms = ["facebook", "instagram", "youtube"] if requested_platform in {"", "all", "general"} else [requested_platform]
    platform_packs = {platform: _build_platform_pack(platform, episode, transcript_keywords) for platform in platforms}

    return {
        "episode": asdict(episode),
        "platforms": platform_packs,
        "export": {
            "bundleName": f"{episode.title} social copy pack",
            "summary": f"{episode.title} with {episode.guest}",
            "suggestedUses": [
                "Use the first description variant as the main post",
                "Use hooks as highlight captions or Reel overlays",
                "Use the hashtags block for Instagram and Facebook",
                "Use the YouTube titles for A/B testing",
            ],
        },
    }