import re

def remove_markdown(md_text: str) -> str:
    if not md_text:
        return ""
        
    text = md_text
    # remove images
    text = re.sub(r'!\[([^\]]*)\]\([^)]*\)', r'\1', text)
    # remove link
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # remove #,##...
    text = re.sub(r'^(#{1,6})\s+', '', text, flags=re.MULTILINE)
    # remove bold or italics
    text = re.sub(r'(\*\*|__|\*|_)(.*?)\1', r'\2', text)
    # remove blockquotes (>)
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    # remove code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # remove code inline
    text = re.sub(r'`(.*?)`', r'\1', text)
    # remove empty or extra spaces
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    
    return text.strip()