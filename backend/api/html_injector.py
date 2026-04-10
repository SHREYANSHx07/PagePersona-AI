"""
html_injector.py — Surgically injects personalized copy into the original page HTML.
"""
import re
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

PERSONALIZATION_BADGE = """
<div id="pg-personalization-badge" style="
  position: fixed;
  top: 16px;
  right: 16px;
  z-index: 99999;
  background: linear-gradient(135deg, #7c3aed, #06b6d4);
  color: white;
  padding: 8px 16px;
  border-radius: 24px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.3px;
  box-shadow: 0 4px 20px rgba(124, 58, 237, 0.4);
  display: flex;
  align-items: center;
  gap: 6px;
  pointer-events: none;
">
  <span>✨</span> Personalized for You
</div>
"""


def inject_personalization(html: str, personalization: dict) -> tuple[str, list]:
    """
    Injects personalized copy into the original HTML.

    Changes made:
    - h1 → new_headline
    - h2 → new_subheadline
    - CTA buttons → new_cta_text
    - Hero paragraph → new_hero_description
    - Social proof injection (appended near hero)
    - Personalization badge added

    Returns:
        (modified_html, change_log)
    """
    change_log = []

    try:
        soup = BeautifulSoup(html, 'lxml')
        reasoning = personalization.get('reasoning', {})

        # --- 1. Headline (h1) ---
        new_headline = personalization.get('new_headline', '')
        original_headline = ''
        h1 = soup.find('h1')
        if h1 and new_headline:
            original_headline = h1.get_text(strip=True)
            h1.clear()
            h1.append(new_headline)
            change_log.append({
                "type": "headline",
                "icon": "🎯",
                "label": "Headline",
                "original": original_headline,
                "updated": new_headline,
                "reasoning": reasoning.get('headline', 'Aligned with ad message scent for better continuity.'),
            })
            logger.info(f"Injected headline: {new_headline[:50]}")

        # --- 2. Subheadline (h2) ---
        new_subheadline = personalization.get('new_subheadline', '')
        h2 = soup.find('h2')
        if h2 and new_subheadline:
            original_sub = h2.get_text(strip=True)
            h2.clear()
            h2.append(new_subheadline)
            change_log.append({
                "type": "subheadline",
                "icon": "📝",
                "label": "Subheadline",
                "original": original_sub,
                "updated": new_subheadline,
                "reasoning": reasoning.get('subheadline', 'Improves message clarity and audience resonance.'),
            })

        # --- 3. Primary CTA (first matching button/link) ---
        new_cta = personalization.get('new_cta_text', '')
        if new_cta:
            cta_changed = False
            original_cta = ''

            cta_buttons = soup.find_all(
                ['button', 'a'],
                class_=re.compile(r'btn|button|cta', re.I),
            )
            if not cta_buttons:
                cta_buttons = soup.find_all('button')
            if not cta_buttons:
                cta_buttons = [a for a in soup.find_all('a', href=True) if a.get_text(strip=True)]

            for btn in cta_buttons:
                btn_text = btn.get_text(strip=True)
                if not btn_text or len(btn_text) >= 80:
                    continue
                original_cta = btn_text
                btn.clear()
                btn.append(new_cta)
                cta_changed = True
                break

            if cta_changed:
                change_log.append({
                    "type": "cta",
                    "icon": "🚀",
                    "label": "Call to Action",
                    "original": original_cta,
                    "updated": new_cta,
                    "reasoning": reasoning.get('cta', 'Matches the ad promise for higher conversion intent.'),
                })

        # --- 4. Hero Description ---
        new_hero = personalization.get('new_hero_description', '')
        if new_hero:
            hero_changed = False
            original_hero = ''

            # Look for hero/banner section first
            hero_section = soup.find(
                ['section', 'div', 'header'],
                class_=re.compile(r'hero|banner|jumbotron|intro|landing', re.I)
            )
            if not hero_section:
                hero_section = soup.find(
                    ['section', 'div', 'header'],
                    id=re.compile(r'hero|banner|home|intro', re.I)
                )

            if hero_section:
                p = hero_section.find('p')
                if p:
                    original_hero = p.get_text(strip=True)
                    p.clear()
                    p.append(new_hero)
                    hero_changed = True
            else:
                # Fallback: first paragraph after h1
                h1 = soup.find('h1')
                if h1:
                    for sibling in h1.find_next_siblings():
                        if sibling.name == 'p':
                            text = sibling.get_text(strip=True)
                            if len(text) > 20:
                                original_hero = text
                                sibling.clear()
                                sibling.append(new_hero)
                                hero_changed = True
                                break

            if hero_changed:
                change_log.append({
                    "type": "hero",
                    "icon": "💬",
                    "label": "Hero Description",
                    "original": original_hero[:150] + ('...' if len(original_hero) > 150 else ''),
                    "updated": new_hero,
                    "reasoning": reasoning.get('hero_description', 'Speaks directly to the pain point raised in the ad.'),
                })

        # --- 5. Social Proof ---
        new_social = personalization.get('new_social_proof', '')
        if new_social:
            social_tag = soup.new_tag('div')
            social_tag['id'] = 'pg-social-proof'
            social_tag['style'] = (
                'background: rgba(124,58,237,0.08); '
                'border-left: 3px solid #7c3aed; '
                'padding: 12px 20px; '
                'margin: 16px 0; '
                'font-style: italic; '
                'font-family: -apple-system, BlinkMacSystemFont, sans-serif; '
                'color: #374151; '
                'border-radius: 4px;'
            )
            social_tag.string = f'⭐ {new_social}'

            # Insert after h1 or at top of body
            h1 = soup.find('h1')
            if h1:
                h1.insert_after(social_tag)
            else:
                body = soup.find('body')
                if body:
                    body.insert(0, social_tag)

            change_log.append({
                "type": "social_proof",
                "icon": "⭐",
                "label": "Social Proof",
                "original": "",
                "updated": new_social,
                "reasoning": reasoning.get('social_proof', 'Builds trust with audience segment from the ad.'),
            })

        # --- 6. Personalization Badge ---
        badge_soup = BeautifulSoup(PERSONALIZATION_BADGE, 'html.parser')
        body = soup.find('body')
        if body:
            body.append(badge_soup)

        modified_html = str(soup)
        return modified_html, change_log

    except Exception as e:
        logger.error(f"Error in html_injector: {e}", exc_info=True)
        return html, []  # Return original on failure
