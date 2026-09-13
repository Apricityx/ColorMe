import string

from color_me.i18n import DEFAULT_LANGUAGE, TRANSLATIONS, translate


def _placeholders(template: str) -> set[str]:
    return {field for _, field, _, _ in string.Formatter().parse(template) if field}


def test_all_languages_have_the_same_keys():
    reference = set(TRANSLATIONS[DEFAULT_LANGUAGE])
    for language, mapping in TRANSLATIONS.items():
        assert set(mapping) == reference, language


def test_placeholders_match_across_languages():
    reference = TRANSLATIONS[DEFAULT_LANGUAGE]
    for key, template in reference.items():
        for language, mapping in TRANSLATIONS.items():
            assert _placeholders(mapping[key]) == _placeholders(template), (language, key)


def test_translate_formats_arguments():
    assert translate('en_us', 'colors', colors='red, blue') == 'Available colors: red, blue'
    assert translate('zh_cn', 'colors', colors='red, blue') == '可用颜色：red, blue'


def test_translate_falls_back_from_zh_tw_to_zh_cn():
    assert translate('zh_tw', 'install_done') == TRANSLATIONS['zh_cn']['install_done']


def test_translate_falls_back_to_default_language():
    assert translate('fr_fr', 'install_done') == TRANSLATIONS[DEFAULT_LANGUAGE]['install_done']
    assert translate(None, 'install_done') == TRANSLATIONS[DEFAULT_LANGUAGE]['install_done']


def test_translate_returns_the_key_for_unknown_keys():
    assert translate('en_us', 'no.such.key') == 'no.such.key'
