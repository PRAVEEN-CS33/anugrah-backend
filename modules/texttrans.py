from deep_translator import GoogleTranslator

from .code_mapping import code_map

def translate_text(text, target_lang="english"):
    try:
        target_lang = code_map(target_lang)
        translater = GoogleTranslator(source="auto", target=target_lang)
        translated_text = translater.translate(text)
        return translated_text
    except Exception as e:
        return f"Error: {e}"
