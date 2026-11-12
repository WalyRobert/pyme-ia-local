"""Comprobación real del RAG con PDF sintético y Ollama local."""
from __future__ import annotations

import io
import json
import sys
import time
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pypdf import PdfWriter
from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject
import app


def fixture_pdf() -> bytes:
    writer = PdfWriter()
    page = writer.add_blank_page(width=595, height=842)
    font = DictionaryObject({NameObject('/Type'): NameObject('/Font'),
                             NameObject('/Subtype'): NameObject('/Type1'),
                             NameObject('/BaseFont'): NameObject('/Helvetica')})
    page[NameObject('/Resources')] = DictionaryObject({
        NameObject('/Font'): DictionaryObject({NameObject('/F1'): writer._add_object(font)})
    })
    stream = DecodedStreamObject()
    stream.set_data(b'BT /F1 12 Tf 50 780 Td (Contrato ficticio de prueba.) Tj 0 -22 Td '
                    b'(El importe total del contrato es de 125 euros.) Tj 0 -22 Td '
                    b'(La fecha de vencimiento es el 15 de diciembre de 2026.) Tj ET')
    page[NameObject('/Contents')] = writer._add_object(stream)
    target = io.BytesIO()
    writer.write(target)
    return target.getvalue()


def main() -> None:
    report = {'checks': {}, 'answers': {}, 'timings_seconds': {}}
    started = time.perf_counter()
    app.check_ollama()
    report['checks']['ollama_models_available'] = True
    llm, embeddings = app.load_models()
    vector = embeddings.embed_query('Contrato de 125 euros')
    assert len(vector) > 0
    report['embedding_dimensions'] = len(vector)
    report['checks']['real_embeddings'] = True
    data = fixture_pdf()
    paths = []
    original_tempfile = app.tempfile.NamedTemporaryFile
    def tracked_temporary(*args, **kwargs):
        handle = original_tempfile(*args, **kwargs)
        paths.append(handle.name)
        return handle
    with patch.object(app.tempfile, 'NamedTemporaryFile', tracked_temporary):
        pages = app.read_pdf(data)
    assert '125 euros' in pages[0].page_content
    assert all(not Path(path).exists() for path in paths)
    assert all('source' not in doc.metadata for doc in pages)
    report['checks']['real_pdf_and_temporary_deletion'] = True
    store = app.build_index(pages, embeddings)
    second = None
    try:
        t = time.perf_counter()
        known = app.answer_question('¿Cuál es el importe total del contrato?', store, llm)
        report['timings_seconds']['known_question'] = round(time.perf_counter() - t, 2)
        report['answers']['known'] = known['answer']
        assert '125' in known['answer'], known['answer']
        assert known['context'] and '125' in known['context'][0].page_content
        report['checks']['known_answer_and_sources'] = True
        unknown = app.answer_question('¿Cuál es el número de teléfono de la empresa?', store, llm)
        report['answers']['unknown'] = unknown['answer']
        assert unknown['answer'].strip() == app.FALLBACK, unknown['answer']
        report['checks']['unknown_answer_abstains'] = True
        second = app.build_index([app.Document(page_content='Documento independiente: clave AZUL.', metadata={'page': 0})], embeddings)
        assert store._collection.name != second._collection.name
        assert all('125' not in d.page_content for d in second.similarity_search('importe', k=1))
        report['checks']['collection_isolation'] = True
    finally:
        store.delete_collection()
        if second is not None:
            second.delete_collection()
    report['checks']['collections_deleted'] = True
    report['timings_seconds']['total'] = round(time.perf_counter() - started, 2)
    (ROOT / 'tests' / 'last_integration_result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
