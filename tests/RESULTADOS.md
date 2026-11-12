# Resultados de comprobación local

Fecha: 10 de noviembre de 2026. Entorno: Windows, Python 3.11.15 y modelos ejecutados por Ollama en CPU.

- Dependencias: 122 paquetes instalados; `uv pip check` confirmó su compatibilidad.
- Modelos: `llama3:latest` y `nomic-embed-text:latest` descargados y disponibles.
- Embeddings reales: vector de 768 dimensiones.
- PDF sintético: extracción correcta de texto y eliminación comprobada del temporal.
- Pregunta sobre importe: respuesta correcta de 125 euros y fragmento fuente correspondiente.
- Pregunta sobre teléfono ausente: respuesta exacta «No tengo esa información en el documento proporcionado.»
- Colecciones independientes: sin mezcla del contenido consultado; colecciones eliminadas al terminar.
- Interfaz Streamlit: inicio correcto, rechazo de archivo inválido, consulta con respuesta y fuentes, y botón de borrado verificados mediante AppTest. El upload se inyecta con BytesIO; la extracción, los embeddings y la respuesta son reales.
- Dos pruebas aisladas de limpieza: aprobadas tanto con lectura correcta como con excepción simulada.
- Servidor Streamlit: comprobación HTTP de `/_stcore/health`, respuesta 200 y contenido `ok`.

La primera pregunta del ensayo de integración tardó 65,71 segundos; el ensayo completo, 82,47 segundos, sin contar importaciones previas. No es un benchmark y los tiempos pueden variar. Ollama informó ejecución de ambos modelos en CPU.

Los archivos `last_integration_result.json` y `last_ui_result.json` conservan la evidencia del ensayo. El documento y las preguntas son ficticios; no se utilizaron archivos personales.

Estas comprobaciones prueban el caso descrito. No son una auditoría de seguridad, una evaluación exhaustiva del modelo ni una certificación normativa. No se verificó el aislamiento de red mediante captura de tráfico.

## Revisión de usabilidad

Se sustituyó la carga en la barra lateral por una zona central visible, se añadió el botón visual «Selecionar PDF» y se verificó de nuevo AppTest: carga central, rechazo de archivo inválido, consulta con fuentes y limpieza. Se comprobó además el envío real por el selector del navegador con un PDF ficticio, una pregunta en portugués y la respuesta de 125 euros con su fuente. Se borró el documento de prueba con Limpar y se dejó la pantalla inicial preparada para el usuario. Las capturas reales se guardaron en assets/.
