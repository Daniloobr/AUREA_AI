from services.prompt_engine import generate_prompt, generate_negative_prompt, get_available_styles


class TestPromptEngine:
    def test_generate_prompt_returns_string(self):
        result = generate_prompt(tipo_ensaio="classic")
        assert isinstance(result, str)
        assert len(result) > 50

    def test_generate_prompt_with_subject_description(self):
        result = generate_prompt(tipo_ensaio="boho_chic", subject_description="Teste")
        assert isinstance(result, str)

    def test_generate_prompt_unknown_style(self):
        result = generate_prompt(tipo_ensaio="estilo_inexistente")
        assert "Professional studio" in result

    def test_generate_prompt_respects_max_length(self):
        result = generate_prompt(tipo_ensaio="classic")
        assert len(result) <= 700

    def test_generate_prompt_without_identity_text(self):
        result = generate_prompt(tipo_ensaio="classic", use_identity_text=False)
        assert "Preserve exact identity" not in result

    def test_generate_negative_prompt(self):
        result = generate_negative_prompt()
        assert isinstance(result, str)
        assert "cgi" in result

    def test_get_available_styles(self):
        styles = get_available_styles()
        assert isinstance(styles, list)
        assert len(styles) > 0
        for style in styles:
            assert "id" in style
            assert "name" in style
            assert "category" in style

    def test_generate_prompt_different_framings(self):
        framings = ["full_body", "three_quarters", "medium", "close_up_emotional", "detail_hands_belly"]
        for framing in framings:
            result = generate_prompt(tipo_ensaio="classic", framing=framing)
            assert isinstance(result, str)
            assert len(result) > 50

    def test_generate_prompt_different_expressions(self):
        result = generate_prompt(tipo_ensaio="classic", expression_key="warm")
        assert isinstance(result, str)
