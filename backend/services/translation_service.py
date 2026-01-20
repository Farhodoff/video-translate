from deep_translator import GoogleTranslator

def translate_segments(segments: list, target_lang: str = "uz"):
    translator = GoogleTranslator(source='auto', target=target_lang)
    translated_results = []
    
    for seg in segments:
        text = seg.get('text', '')
        try:
            translated_text = translator.translate(text)
        except:
            translated_text = text # Fallback
            
        translated_results.append({
            "start": seg['start'],
            "end": seg['end'],
            "text": translated_text,
            "original": text
        })
    return translated_results
