"""Prueba de interfaz con carga sintética; inferencia real en Ollama."""
from __future__ import annotations
import io
import json
import sys
from pathlib import Path
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from streamlit.testing.v1 import AppTest
from integration_ollama import fixture_pdf
import streamlit as st


def main() -> None:
    report = {}
    screen = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=240).run()
    assert not screen.exception
    assert screen.title[0].value == 'Seu PDF, uma conversa.'
    report['initial_screen'] = True
    assert len(screen.get('file_uploader')) == 1
    assert not screen.sidebar.get('file_uploader')
    report['upload_visible_on_main_screen'] = True
    with patch.object(st, 'file_uploader', return_value=io.BytesIO(b'not a pdf')):
        screen.run()
        assert screen.error and 'PDF válido' in screen.error[0].value
    report['invalid_pdf_rejected'] = True
    with patch.object(st, 'file_uploader', return_value=io.BytesIO(fixture_pdf())):
        screen.run()
        assert not screen.exception
        assert screen.success, [e.value for e in screen.error]
        screen.text_input[0].set_value('¿Cuál es el importe total del contrato?')
        next(button for button in screen.button if button.label == 'Consultar documento').click().run()
        assert not screen.exception
        assert any('125' in item.value for item in screen.text)
        assert screen.expander[0].label == 'Trechos utilizados como fontes'
    report['ui_question_answer_and_sources'] = True
    next(button for button in screen.button if button.label == 'Limpar').click().run()
    assert not screen.exception
    assert 'store' not in screen.session_state
    assert 'result' not in screen.session_state
    report['clear_button'] = True
    (ROOT / 'tests' / 'last_ui_result.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()


