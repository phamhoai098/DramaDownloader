"""
drama_downloader.platforms.shortmax
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Extractor for ShortMax platform.
"""

import re
import html
from typing import Optional, List, Dict, Any
from .base import BasePlatform, GOODBOS_TOKEN
from ..models import Series, Episode, Subtitle, CatalogResult, CatalogItem


class ShortMaxPlatform(BasePlatform):
    platform_id = "shortmax"
    display_name = "ShortMax"

    BASE_URL = "https://shortmax.goodbos.online/api/v1"

    def can_handle(self, url: str) -> bool:
        u = url.lower().strip()
        return "shortmax" in u or u.startswith("shortmax:")

    def _extract_id(self, url: str) -> str:
        u = url.strip()
        m = re.search(r"shortmax:[/\\]*([A-Za-z0-9_-]+)", u, re.I)
        if m:
            return m.group(1)
        m = re.search(r"/(?:drama|series|detail|play)/([A-Za-z0-9_-]+)", u, re.I)
        if m:
            return m.group(1)
        m = re.search(r"([A-Za-z0-9_-]{8,})", u)
        return m.group(1) if m else ""

    def _pick_best_video(self, video_dict: Dict[str, Any]) -> Optional[str]:
        if not isinstance(video_dict, dict):
            return None
        for q in ["1080p", "720p", "540p", "480p", "360p"]:
            if video_dict.get(q):
                return video_dict[q]
        for v in video_dict.values():
            if isinstance(v, str) and (v.startswith("http://") or v.startswith("https://")):
                return v
        return None

    def load_series(self, url: str) -> Series:
        sm_key = self._extract_id(url)
        if not sm_key:
            raise ValueError(f"Could not read ShortMax drama ID from: {url}")

        params = {"lang": "en", "code": GOODBOS_TOKEN}
        resp = self.http.get(f"{self.BASE_URL}/alleps/{sm_key}", params=params)
        if resp.status_code != 200:
            raise ValueError(f"ShortMax API error: HTTP {resp.status_code}")

        res_json = resp.json()
        data = res_json.get("data") or {}
        raw_episodes = data.get("episodes") or []

        raw_episodes = sorted(raw_episodes, key=lambda x: x.get("episode", 0))

        series_name = data.get("name") or "ShortMax Drama"
        cover = data.get("cover") or ""
        desc = data.get("summary") or ""

        episodes: List[Episode] = []
        for idx, ep_data in enumerate(raw_episodes):
            ep_num = idx + 1
            v_dict = ep_data.get("video") or {}
            direct_url = self._pick_best_video(v_dict)

            episodes.append(
                Episode(
                    num=ep_num,
                    title=f"Episode {ep_num}",
                    url=f"https://www.shortmax.com/drama/{sm_key}/{ep_num}",
                    direct_url=direct_url,
                    thumb=ep_data.get("cover") or cover,
                    locked=not bool(direct_url),
                    extra={"video": v_dict, "sm_key": sm_key},
                )
            )

        accessible = sum(1 for ep in episodes if not ep.locked)
        return Series(
            name=series_name,
            platform=self.platform_id,
            series_id=f"shortmax:{sm_key}",
            cover=cover,
            description=desc,
            episode_count=len(episodes),
            accessible_count=accessible,
            episodes=episodes,
            url=f"https://www.shortmax.com/drama/{sm_key}",
        )

    def get_catalog(
        self,
        page: int = 1,
        query: Optional[str] = None,
        category: Optional[str] = None,
        language: str = "vi",
    ) -> CatalogResult:
        # Scrape official ShortMax website directly for live catalog & covers
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            resp = self.http.get("https://www.shortmax.com", headers=headers, timeout=12)
            if resp.status_code == 200:
                text = resp.text
                matches = list(re.finditer(r'''href=['"](/drama/[^'"]+)['"]''', text))
                seen = set()
                items = []
                q_lower = query.lower().strip() if query else None

                for m in matches:
                    link = m.group(1)
                    if link in seen:
                        continue
                    seen.add(link)

                    slug = link.replace("/drama/", "").strip()
                    m_id = re.search(r"-(\d+)$", slug)
                    sid = m_id.group(1) if m_id else slug

                    window = text[max(0, m.start() - 600):min(len(text), m.end() + 600)]

                    title = ""
                    t_m = re.search(r'''class=['"][^'"]*(?:card-title|hero-title)[^'"]*['"][^>]*>([^<]+)''', window)
                    if t_m:
                        title = html.unescape(t_m.group(1)).strip()
                    else:
                        title = slug.replace("-", " ").title()

                    if q_lower and q_lower not in title.lower():
                        continue

                    img_m = re.search(r'''(?:src|data-src)=['"](https://[^'"]*shorttv\.live[^'"]*)['"]''', window)
                    cover = img_m.group(1) if img_m else ""
                    if "&amp;" in cover:
                        cover = cover.replace("&amp;", "&")

                    items.append(
                        CatalogItem(
                            id=sid,
                            name=title,
                            cover=cover,
                            episodes=80,
                            desc="ShortMax Original Drama",
                            link=f"https://www.shortmax.com{link}",
                            platform=self.platform_id,
                        )
                    )

                page_size = 24
                total = len(items)
                start_idx = (page - 1) * page_size
                paged_items = items[start_idx:start_idx + page_size]

                if paged_items:
                    return CatalogResult(items=paged_items, total=total, platform=self.platform_id)
        except Exception:
            pass

        return CatalogResult(items=[], total=0, platform=self.platform_id)


    def get_categories(self, language: str = "vi") -> List[Dict[str, str]]:
        return [
            {"id": "", "name": "🔥 Tất Cả (All)"},
            {"id": "trending", "name": "📈 Thịnh Hành (Trending)"},
            {"id": "ceo", "name": "👑 Tổng Tài / CEO"},
            {"id": "revenge", "name": "⚔️ Báo Thù (Revenge)"},
            {"id": "romance", "name": "💕 Lãng Mạn (Romance)"},
            {"id": "werewolf", "name": "🐺 Người Sói (Werewolf)"},
            {"id": "rebirth", "name": "⏳ Trọng Sinh (Rebirth)"},
        ]


