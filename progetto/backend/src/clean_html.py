import re

def clean_html(raw_html:str, char_limit:int) -> str:
    if not raw_html:
        return ""
 
    #html cleanup
    clean_html = re.sub(r'<(head|script|style|svg|noscript|nav|footer|iframe|span|href|li|section)[^>]*>.*?</\1>', '', raw_html, flags=re.IGNORECASE | re.DOTALL)
    clean_html = re.sub(r'<!--.*?-->', '', clean_html, flags=re.DOTALL)
    clean_html = re.sub(r'\n\s*\n', '\n', clean_html).strip()

    safe_html = clean_html[:char_limit]
    if len(clean_html) > char_limit:
        safe_html += "\n[...truncated text for memory limits...]"
        
    return safe_html