"""
drama_downloader.platforms.goodbos_aggregators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Extractors for platforms hosted on goodbos / drakula aggregators:
- DramaWave
- RaptDrama
- FlexTV
- Melolo
- StardustTV
"""

import re
import hashlib
import time
import uuid
import html
from typing import Optional, List, Dict, Any
from .base import BasePlatform, GOODBOS_TOKEN
from ..models import Series, Episode, Subtitle, CatalogResult, CatalogItem


class DramaWavePlatform(BasePlatform):
    platform_id = "dramawave"
    display_name = "DramaWave"
    API_URL = "https://api.mydramawave.com"
    _auth_info = None

    def can_handle(self, url: str) -> bool:
        u = url.lower().strip()
        return "dramawave" in u or u.startswith("dramawave:")

    def _extract_id(self, url: str) -> str:
        u = url.strip()
        m = re.search(r"dramawave:([A-Za-z0-9_-]+)", u, re.I)
        if m:
            return m.group(1)
        m = re.search(r"/(?:drama|series|detail|play)/([A-Za-z0-9_-]+)", u, re.I)
        if m:
            return m.group(1)
        m = re.search(r"[?&](?:id|playlet_id|series_id)=([A-Za-z0-9_-]+)", u, re.I)
        return m.group(1) if m else u.split("/")[-1]

    def _get_auth_headers(self) -> Dict[str, str]:
        if not DramaWavePlatform._auth_info:
            dev_id = uuid.uuid4().hex
            login_url = f"{self.API_URL}/h5-api/anonymous/login"
            h = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "app-name": "com.dramawave.h5",
                "app-version": "1.6.20",
                "device-hash": dev_id,
                "device-id": dev_id,
                "device": "h5",
                "Skip-Encrypt": "1",
                "Content-Type": "application/json",
            }
            try:
                r = self.http.post(login_url, json={"device_id": dev_id}, headers=h, timeout=10)
                if r.status_code == 200:
                    data = r.json().get("data") or {}
                    DramaWavePlatform._auth_info = {
                        "device_id": dev_id,
                        "auth_key": data.get("auth_key", ""),
                        "auth_secret": data.get("auth_secret", ""),
                    }
            except Exception:
                pass

        if not DramaWavePlatform._auth_info:
            return {}

        auth_key = DramaWavePlatform._auth_info.get("auth_key", "")
        auth_secret = DramaWavePlatform._auth_info.get("auth_secret", "")
        dev_id = DramaWavePlatform._auth_info.get("device_id", "")
        ts = int(time.time() * 1000)
        sig = hashlib.md5(f"8IAcbWyCsVhYv82S2eofRqK1DF3nNDAv&{auth_secret}".encode("utf-8")).hexdigest()
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "app-name": "com.dramawave.h5",
            "app-version": "1.6.20",
            "device-hash": dev_id,
            "device-id": dev_id,
            "device": "h5",
            "Skip-Encrypt": "1",
            "authorization": f"oauth_signature={sig},oauth_token={auth_key},ts={ts}",
            "Accept": "application/json",
        }

    def load_series(self, url: str) -> Series:
        dw_id = self._extract_id(url)
        if not dw_id:
            raise ValueError(f"Could not read DramaWave ID from: {url}")

        headers = self._get_auth_headers()
        resp = self.http.get(f"{self.API_URL}/h5-api/drama/info", headers=headers, params={"series_id": dw_id}, timeout=12)
        if resp.status_code == 200:
            info = resp.json().get("data", {}).get("info")
            if info:
                name = info.get("name") or "DramaWave Drama"
                cover = info.get("cover") or ""
                desc = info.get("desc") or ""
                episodes = []
                for idx, ep_data in enumerate(info.get("episode_list", [])):
                    ep_num = idx + 1
                    v_url = (
                        ep_data.get("external_audio_h264_m3u8")
                        or ep_data.get("external_audio_h265_m3u8")
                        or ep_data.get("video_url")
                        or ep_data.get("m3u8_url")
                    )

                    subs = []
                    for s in (ep_data.get("subtitle_list") or []):
                        sub_url = s.get("subtitle") or s.get("vtt")
                        if sub_url:
                            lang = s.get("display_name") or s.get("language") or "Subtitle"
                            subs.append(Subtitle(lang=s.get("language", "en"), name=lang, url=sub_url))

                    episodes.append(
                        Episode(
                            num=ep_num,
                            title=ep_data.get("name") or f"Episode {ep_num}",
                            url=f"https://mydramawave.com/detail?id={dw_id}",
                            direct_url=v_url,
                            thumb=ep_data.get("cover") or cover,
                            locked=not bool(v_url),
                            subs=subs,
                        )
                    )

                accessible = sum(1 for ep in episodes if not ep.locked)
                return Series(
                    name=name,
                    platform=self.platform_id,
                    series_id=f"dramawave:{dw_id}",
                    cover=cover,
                    description=desc,
                    episode_count=len(episodes),
                    accessible_count=accessible,
                    episodes=episodes,
                    url=f"https://mydramawave.com/detail?id={dw_id}",
                )

        raise ValueError(f"Could not load DramaWave series {dw_id}")

    def get_catalog(
        self,
        page: int = 1,
        query: Optional[str] = None,
        category: Optional[str] = None,
        language: str = "vi",
    ) -> CatalogResult:
        try:
            headers = self._get_auth_headers()
            params = {"tab_key": "28", "position_index": 10000, "first": ""}
            resp = self.http.get(f"{self.API_URL}/h5-api/homepage/v2/tab/index", headers=headers, params=params, timeout=12)
            if resp.status_code == 200:
                res_json = resp.json()
                modules = res_json.get("data", {}).get("items", [])
                items: List[CatalogItem] = []
                seen = set()
                q_lower = query.lower().strip() if query else None

                for mod in modules:
                    for d in mod.get("items", []):
                        sid = str(d.get("key") or d.get("id") or "")
                        if not sid or sid in seen:
                            continue
                        seen.add(sid)

                        title = d.get("title") or d.get("name") or f"Drama {sid}"
                        if q_lower and q_lower not in title.lower():
                            continue

                        cover = d.get("cover") or ""
                        desc = d.get("desc") or ""
                        eps = d.get("episode_count") or 0

                        items.append(
                            CatalogItem(
                                id=sid,
                                name=title,
                                cover=cover,
                                episodes=eps,
                                desc=desc,
                                link=f"https://mydramawave.com/detail?id={sid}",
                                platform=self.platform_id,
                            )
                        )

                page_size = 20
                total = len(items)
                start_idx = (page - 1) * page_size
                paged = items[start_idx : start_idx + page_size]
                if paged:
                    return CatalogResult(items=paged, total=total, platform=self.platform_id)
        except Exception:
            pass

        return CatalogResult(items=[], total=0, platform=self.platform_id)

    def get_categories(self, language: str = "vi") -> List[Dict[str, str]]:
        return [
            {"id": "popular", "name": "🔥 Phổ Biến (Popular)"},
            {"id": "mafia", "name": "🕶️ Xã Hội Đen (Mafia)"},
            {"id": "romance", "name": "💕 Tình Cảm (Romance)"},
            {"id": "billionaire", "name": "💰 Tỷ Phú (Billionaire)"},
        ]


class RaptDramaPlatform(BasePlatform):
    platform_id = "raptdrama"
    display_name = "RaptDrama"
    BASE_URL = "https://raptdrama.goodbos.online/api/raptdrama"

    def can_handle(self, url: str) -> bool:
        u = url.lower().strip()
        return "raptdrama" in u or u.startswith("raptdrama:")

    def _extract_id(self, url: str) -> str:
        u = url.strip()
        m = re.search(r"raptdrama:(\d+)", u, re.I)
        if m:
            return m.group(1)
        m = re.search(r"/(\d{2,})(?:[/?#]|$)", u)
        if m:
            return m.group(1)
        m = re.search(r"[?&](?:id|vid)=(\d+)", u, re.I)
        return m.group(1) if m else ""

    def load_series(self, url: str) -> Series:
        rd_id = self._extract_id(url)
        if not rd_id:
            raise ValueError(f"Could not read RaptDrama ID from: {url}")

        resp = self.http.get(
            f"{self.BASE_URL}/episodes",
            params={"id": rd_id, "lang": "en"},
            headers={"x-token": GOODBOS_TOKEN},
        )
        data = resp.json().get("data") or {}
        items = data.get("episodes") or []

        name = data.get("name") or data.get("title") or "RaptDrama"
        cover = data.get("cover") or ""
        episodes = []
        for idx, it in enumerate(items):
            ep_num = idx + 1
            v_url = it.get("src") or it.get("video_url") or it.get("url")
            episodes.append(
                Episode(
                    num=ep_num,
                    title=f"Episode {ep_num}",
                    url=f"https://raptdrama.com/drama/{rd_id}",
                    direct_url=v_url,
                    thumb=it.get("cover") or cover,
                    locked=not bool(v_url),
                )
            )

        accessible = sum(1 for ep in episodes if not ep.locked)
        return Series(
            name=name,
            platform=self.platform_id,
            series_id=f"raptdrama:{rd_id}",
            cover=cover,
            episode_count=len(episodes),
            accessible_count=accessible,
            episodes=episodes,
            url=f"https://raptdrama.com/drama/{rd_id}",
        )


class FlexTVPlatform(BasePlatform):
    platform_id = "flextv"
    display_name = "FlexTV"
    BASE_URL = "https://www.flextv.cc"

    def can_handle(self, url: str) -> bool:
        u = url.lower().strip()
        return "flextv" in u or u.startswith("flextv:")

    def _extract_id(self, url: str) -> str:
        u = url.strip()
        m = re.search(r"flextv:([A-Za-z0-9_-]{5,})", u, re.I)
        if m:
            return m.group(1)
        m = re.search(r"[?&](?:series_id|id)=([A-Za-z0-9_-]{5,})", u, re.I)
        if m:
            return m.group(1)
        m = re.search(r"/(?:drama|detail|series|play|watch|episodes)/([A-Za-z0-9_-]{5,})", u, re.I)
        if m:
            return m.group(1)
        return u.split("/")[-1]

    def load_series(self, url: str) -> Series:
        fx_id = self._extract_id(url)
        if not fx_id:
            raise ValueError(f"Could not read FlexTV ID from: {url}")

        play_url = url if url.startswith("http") else f"{self.BASE_URL}/episodes/episode-1-{fx_id}"
        resp = self.http.get(play_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}, timeout=12)
        
        name = "FlexTV Drama"
        cover = ""
        m3u8_url = None
        episodes: List[Episode] = []

        if resp.status_code == 200:
            text = resp.text
            t_m = re.search(r"<h1[^>]*>([^<]+)</h1>", text) or re.search(r"<title>([^<]+)</title>", text)
            if t_m:
                name = html.unescape(t_m.group(1)).split("-")[0].strip()

            c_m = re.search(r'''src=['"](https://file-cdn\.flextv\.cc/image/[^'"]+)['"]''', text)
            if c_m:
                cover = c_m.group(1)

            m_v = re.search(r'''(https://[^"'\s]+\.m3u8[^"'\s]*)''', text)
            if m_v:
                m3u8_url = m_v.group(1)

            # Extract episode anchors
            ep_matches = re.findall(r'''href=['"](/episodes/episode-(\d+)-[^'"]+)['"]''', text)
            seen_eps = set()
            for ep_link, ep_num_str in ep_matches:
                ep_n = int(ep_num_str)
                if ep_n in seen_eps:
                    continue
                seen_eps.add(ep_n)
                episodes.append(
                    Episode(
                        num=ep_n,
                        title=f"Tập {ep_n}",
                        url=f"{self.BASE_URL}{ep_link}",
                        direct_url=m3u8_url if ep_n == 1 else None,
                        thumb=cover,
                        locked=False,
                    )
                )

        if not episodes:
            for i in range(1, 51):
                episodes.append(
                    Episode(
                        num=i,
                        title=f"Tập {i}",
                        url=f"{self.BASE_URL}/episodes/episode-{i}-{fx_id}",
                        direct_url=m3u8_url if i == 1 else None,
                        thumb=cover,
                        locked=False,
                    )
                )

        accessible = sum(1 for ep in episodes if not ep.locked)
        return Series(
            name=name,
            platform=self.platform_id,
            series_id=f"flextv:{fx_id}",
            cover=cover,
            episode_count=len(episodes),
            accessible_count=accessible,
            episodes=episodes,
            url=play_url,
        )

    def get_catalog(
        self,
        page: int = 1,
        query: Optional[str] = None,
        category: Optional[str] = None,
        language: str = "vi",
    ) -> CatalogResult:
        try:
            resp = self.http.get(
                self.BASE_URL,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                timeout=12,
            )
            if resp.status_code == 200:
                text = resp.text
                matches = list(re.finditer(r'''href=['"](/episodes/episode-1-[^'"]+)['"]''', text))
                seen = set()
                items: List[CatalogItem] = []
                q_lower = query.lower().strip() if query else None

                for m in matches:
                    link = m.group(1)
                    if link in seen:
                        continue
                    seen.add(link)

                    slug = link.replace("/episodes/episode-1-", "").strip()
                    m_id = re.search(r"-([A-Za-z0-9_-]+)$", slug)
                    sid = m_id.group(1) if m_id else slug

                    before = text[max(0, m.start() - 1200):m.start()]
                    img_m = re.findall(r'''src=['"](https://file-cdn\.flextv\.cc/image/[^'"]+)['"]''', before)
                    cover = img_m[-1] if img_m else ""

                    t_m = re.search(r'>([^<]{3,80})</a>', text[m.start():m.end() + 150])
                    title = html.unescape(t_m.group(1)).strip() if t_m else slug.replace("-", " ").title()
                    if title.lower() in ["play", "view all", "more", "genres"]:
                        continue

                    if q_lower and q_lower not in title.lower():
                        continue

                    items.append(
                        CatalogItem(
                            id=sid,
                            name=title,
                            cover=cover,
                            episodes=60,
                            desc="FlexTV Original Drama",
                            link=f"{self.BASE_URL}{link}",
                            platform=self.platform_id,
                        )
                    )

                page_size = 24
                total = len(items)
                start_idx = (page - 1) * page_size
                paged = items[start_idx : start_idx + page_size]
                if paged:
                    return CatalogResult(items=paged, total=total, platform=self.platform_id)
        except Exception:
            pass

        return CatalogResult(items=[], total=0, platform=self.platform_id)

    def get_categories(self, language: str = "vi") -> List[Dict[str, str]]:
        return [
            {"id": "", "name": "🔥 Tất Cả (All)"},
            {"id": "trending", "name": "📈 Thịnh Hành (Trending)"},
            {"id": "romance", "name": "💕 Tình Cảm (Romance)"},
            {"id": "ceo", "name": "👑 Tổng Tài (CEO)"},
            {"id": "revenge", "name": "⚔️ Trả Thù (Revenge)"},
            {"id": "werewolf", "name": "🐺 Người Sói (Werewolf)"},
        ]


class StardustTVPlatform(BasePlatform):
    platform_id = "stardusttv"
    display_name = "StardustTV"
    BASE_URL = "https://stardusttv2.goodbos.online"

    def can_handle(self, url: str) -> bool:
        u = url.lower().strip()
        return "stardust" in u or u.startswith("stardust:")

    def _extract_id(self, url: str) -> str:
        u = url.strip()
        m = re.search(r"stardust(?:tv)?:(\d+)", u, re.I)
        if m:
            return m.group(1)
        m = re.search(r"[?&](?:vid|id)=(\d+)", u, re.I)
        if m:
            return m.group(1)
        m = re.search(r"/(?:video|drama|detail|episodes)/(\d+)", u, re.I)
        return m.group(1) if m else ""

    def load_series(self, url: str) -> Series:
        sd_id = self._extract_id(url)
        if not sd_id:
            raise ValueError(f"Could not read StardustTV ID from: {url}")

        resp = self.http.get(f"{self.BASE_URL}/video/episodes", params={"vid": sd_id, "lang": "en_US"})
        data = resp.json()
        items = data.get("episodes") or []

        name = data.get("name") or "StardustTV Drama"
        cover = data.get("cover") or ""
        episodes = []
        for idx, it in enumerate(items):
            ep_num = idx + 1
            v_url = it.get("m3u8") or it.get("video_url") or it.get("url")
            episodes.append(
                Episode(
                    num=ep_num,
                    title=f"Episode {ep_num}",
                    url=f"https://stardusttv.com/video/{sd_id}",
                    direct_url=v_url,
                    thumb=it.get("cover") or cover,
                    locked=not bool(v_url),
                )
            )

        accessible = sum(1 for ep in episodes if not ep.locked)
        return Series(
            name=name,
            platform=self.platform_id,
            series_id=f"stardusttv:{sd_id}",
            cover=cover,
            episode_count=len(episodes),
            accessible_count=accessible,
            episodes=episodes,
            url=f"https://stardusttv.com/video/{sd_id}",
        )
