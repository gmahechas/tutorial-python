# Notas Generales del Curso de Anthropic Claude API

Estas notas resumen las ideas más importantes, patrones y mejores prácticas de cada módulo y clase dentro de `anthropic/stephen/claude_api`. El objetivo es retener los conceptos, los patrones reutilizables y las advertencias prácticas — no cada línea de implementación.

Cada clase tiene tres secciones cuando aplica:
- **Tema** — de qué trata la clase.
- **Idea clave** — la lección central.
- **Mejores prácticas / gotchas** — reglas concretas a nivel de código sacadas de la implementación que vas a reutilizar en proyectos reales.

---

## Módulo 01 - Getting Started
`helper.py` centraliza el cliente `Anthropic`, el id del modelo, `chat()` y `stream_chat()`. Trata `helper.py` como la **única fuente de verdad** para el id del modelo y la configuración del cliente — cuando salga un modelo nuevo, solo cambias una línea. Reutiliza este patrón en todos los módulos de tus proyectos.

Patrones comunes introducidos aquí:
- `add_user_message(messages, text)` y `add_assistant_message(messages, text)` mutan la lista in place. El caller es dueño del estado de la conversación; el helper no tiene globales.
- `client.messages.create(**params)` es la llamada base. `system`, `tools`, `tool_choice`, `temperature`, `stop_sequences` se pasan todos por el mismo dict de params — arma los params condicionalmente para no enviar campos vacíos.

### Clase 01 - `chat_01.py`
- **Tema:** chat multi-turno con historia.
- **Idea clave:** Claude no tiene memoria del lado del servidor. Cada request debe incluir el array `messages` completo, incluyendo respuestas previas del assistant. Si no agregas la respuesta del assistant antes del siguiente turno del usuario, Claude efectivamente "olvida".
- **Mejores prácticas:**
  - Persiste `messages` (DB, Redis, archivo) si las conversaciones cruzan sesiones.
  - Vigila el conteo de tokens: las conversaciones largas crecen linealmente. Resume o trunca cuando te acerques al context window.
  - Re-envía `system` en cada llamada — también es stateless.

### Clase 02 - `system_prompt_02.py`
- **Tema:** controlar rol, tono y límites con `system`.
- **Idea clave:** El system prompt es para el comportamiento global estable ("tutor paciente", "no des la respuesta directa"). El user prompt es para la tarea específica. Mantén los dos limpiamente separados.
- **Mejores prácticas:**
  - Pon políticas, persona, reglas de formato y reglas de rechazo en `system`.
  - Pon la pregunta real, los datos y la variación one-shot en el user message.
  - Los system prompts pueden ser muy largos; combínalos con prompt caching (ver Módulo 04) cuando se reusan en muchas llamadas.

### Clase 03 - `system_prompt_exercise_03.py`
- **Tema:** ejercicio de debugging — definir un system prompt no es suficiente.
- **Idea clave:** El archivo construye `system_prompt` pero llama `chat(messages)` sin pasarlo. El bug es silencioso — el modelo simplemente se comporta como si las reglas nunca se hubieran fijado.
- **Mejores prácticas:**
  - Cuando una instrucción global "no se está cumpliendo", la primera hipótesis siempre es: *¿la estoy enviando?* Inspecciona el dict de params real antes de culpar al modelo.
  - Agrega un log de sanidad alrededor de `client.messages.create(**params)` mientras debugueas.

### Clase 04 - `temperature_04.py`
- **Tema:** creatividad vs. consistencia.
- **Idea clave:** `temperature` (0.0 – 1.0) controla aleatoriedad en el sampling del siguiente token. No es una perilla de calidad — es una perilla de determinismo.
- **Mejores prácticas:**
  - Bajo (`0.0`–`0.3`) para extracción, clasificación, structured output, generación de código que debe compilar.
  - Alto (`0.7`–`1.0`) para brainstorming, escritura creativa, generar alternativas diversas.
  - Para evaluaciones y bug repros reproducibles, fija temperature en `0`.

### Clase 05 - `streaming_05.py`
- **Tema:** streaming de texto vía `client.messages.stream(...)`.
- **Idea clave:** `stream.text_stream` produce tokens conforme se generan. El tiempo de pared es similar; la latencia percibida es dramáticamente mejor.
- **Mejores prácticas:**
  - Usa un bloque `with`; el SDK maneja cleanup y la reconstrucción del mensaje final.
  - Para UIs de chat, streaming debería ser default a menos que necesites post-procesar la respuesta completa (p.ej., parsear JSON) antes de mostrar nada.
  - Combina con `stop_sequences` para detener temprano cuando aparezca un delimitador (ver siguiente clase).

### Clase 06 - `structure_data_06.py`
- **Tema:** prefilling + `stop_sequences` para forzar JSON limpio.
- **Idea clave:** Pre-siembra el turno del assistant con un fence de apertura (`` ```json ``) y detente en el fence de cierre (`` ``` ``). Claude debe continuar dentro del fence; el stop sequence corta cualquier comentario que normalmente seguiría.
- **Mejores prácticas:**
  - El texto del prefill *se vuelve parte del output del modelo*. Quita el fence de apertura tú mismo al parsear.
  - Combina con temperature baja (`0.0`–`0.2`) y reglas de formato explícitas en el system prompt.
  - Para máxima confiabilidad de structured output, prefiere **tools** (Módulo 03 Clase 05) sobre prefill — los tools imponen un schema, el prefill solo impone un delimitador.

### Clase 07 - `structure_data_exercise_07.py`
- **Tema:** la misma técnica prefill+stop, aplicada a bash / AWS CLI.
- **Idea clave:** El patrón es agnóstico al formato — cambia `json` por `bash`, `xml`, `sql`, `python` y sigue funcionando.
- **Mejores prácticas:**
  - El prefill del assistant también puede incluir una frase de protección ("here are three sample AWS CLI commands without any comment") para suprimir prosa al final.
  - Útil cuando necesitas mandar el output directamente a otra herramienta sin parsing.

---

## Módulo 02 - Prompting / Prompt Evaluation
`helper.py` agrega generación de datasets, un LLM-as-judge y validación de sintaxis. La tesis del módulo: **los prompts son software; los evalúas, no solo iteras a ojo.**

### Clase 01 - `generating_test_datasets_01.py`
- **Tema:** generación automática de datasets con Claude.
- **Idea clave:** En vez de escribir test cases a mano, le pides a Claude que produzca `task`, `solution_criteria`, `format`. El ejemplo enfoca AWS, con formatos restringidos a `python`, `json` o `regex` para que el output se mantenga pequeño y verificable.
- **Mejores prácticas:**
  - Guarda el dataset a disco (`dataset.json`) para que las corridas sean repetibles.
  - Siempre valida el dataset generado en sí antes de evaluar prompts contra él — un test case malformado envenena cada score.

### Clase 02 - `run_eval_02.py`
- **Tema:** pipeline de evaluación = correr prompt → calificar.
- **Idea clave:** Combina un **LLM judge** (corrección semántica) con un **validador programático** (`ast.parse`, `json.loads`, `re.compile`). Score final = `(model_score + syntax_score) / 2`.
- **Mejores prácticas:**
  - Fuerza al judge a devolver JSON estricto con prefill (`` ```json ``) + `stop_sequences=["```"]`.
  - Pídele al judge `strengths`, `weaknesses`, `reasoning`, `score` en una forma fija — los schemas conducen consistencia.
  - Los validadores programáticos atrapan sintaxis alucinada que un LLM judge calificaría con demasiada amabilidad.
  - Mantén los judges deterministas (`temperature=0`) para que re-correr la eval dé scores estables.

---

## Módulo 02.1 - Prompting Engineer
Este módulo convierte la evaluación ad-hoc en un framework reusable: `PromptEvaluator` agrega **concurrencia**, **criterios globales** y **reportes HTML**.

### Clase 01 - `generating_datasets_01.py`
- **Tema:** generación estructurada de datasets a partir de inputs reales del prompt.
- **Idea clave:** Generación en dos fases. Primero Claude propone *ideas de escenarios* diversas; luego elabora cada una en un caso concreto con `prompt_inputs`, `solution_criteria`, `scenario`, `task_description`. Ejemplo: planes alimenticios para atletas parametrizados por `height`, `weight`, `goal`, `restrictions`.
- **Mejores prácticas:**
  - Separar "ideas" de "casos detallados" produce datasets medibles más variados que pedir casos terminados de un tirón.
  - Mantén `num_cases` bajo (p.ej., 3) mientras iteras para evitar rate limits de Voyage / Anthropic.

### Clase 02 - `run_eval_02.py`
- **Tema:** evaluación concurrente con criterios requeridos y reportes HTML/JSON.
- **Idea clave:** `run_evaluation()` corre casos en paralelo, superpone `extra_criteria` (reglas globales) sobre los criterios por-caso, y emite tanto `output.json` (legible por máquina) como `output.html` (legible por humanos).
- **Mejores prácticas:**
  - Usa `extra_criteria` para reglas transversales (debe incluir macros, debe ser JSON, debe evitar PII) para no duplicarlas en cada caso.
  - `max_concurrent_tasks=3` es un default conservador — súbelo después de confirmar que te mantienes bajo el rate limit del API.
  - Siempre inspecciona el reporte HTML cuando un score caiga; usualmente expone el mismo modo de falla en múltiples casos.

---

## Módulo 03 - Tools
`helper.py` implementa el tool loop estándar: enviar messages → si la respuesta tiene `tool_use`, ejecutar el tool localmente, devolver `tool_result`, repetir. `tools.py` contiene las implementaciones y los schemas JSON. **Este patrón de loop es la base de cada agente en el curso.**

### Clase 01 - `handling_message_block_01.py`
- **Tema:** el ciclo mínimo de tool-use, manualmente.
- **Idea clave:** Una llamada de tool es un baile de dos mensajes:
  1. Claude devuelve un bloque `tool_use` con un `id` y `input`.
  2. Tú agregas un user message conteniendo un bloque `tool_result` referenciado por el mismo `tool_use_id`.
  Solo después de eso Claude puede producir una respuesta final de texto.
- **Mejores prácticas:**
  - El `tool_use_id` debe matchear exacto — así es como Claude correlaciona el resultado con la solicitud.
  - Siempre agrega tanto la respuesta `tool_use` del assistant como tu `tool_result` a `messages` antes de la siguiente llamada. Saltarte cualquiera rompe la cadena.

### Clase 02 - `multiple_tools_02.py`
- **Tema:** automatizando el loop con `run_conversation()`.
- **Idea clave:** Una sola respuesta puede contener *múltiples* bloques `tool_use`. Itera sobre todos, junta cada resultado, y devuélvelos en **un** user message conteniendo todos los bloques `tool_result`.
- **Mejores prácticas:**
  - Loopea hasta que `response.stop_reason != "tool_use"`.
  - Envuelve cada llamada `run_tool` en `try/except`; en falla devuelve `{"type": "tool_result", "is_error": True, "content": f"Error: {e}"}`. Claude puede leer el error y recuperarse (p.ej., re-llamar con input corregido).
  - Mantén el loop acotado con un guard de máx-iteraciones en producción para prevenir agentes que se desbocan.

### Clase 03 - `multiple_tools_03.py`
- **Tema:** componiendo tools para resolver tareas multi-paso.
- **Idea clave:** "Pon un recordatorio 177 días después del 1 Ene 2050" requiere `get_current_datetime` → `add_duration_to_datetime` → `set_reminder`. Claude los encadena solo.
- **Mejores prácticas:**
  - Diseña **tools pequeños y de propósito único** con inputs/outputs limpios. Claude los compone mejor que un super-tool monolítico.
  - Haz que las descripciones de los tools se lean como API docs — Claude elige el tool correcto basado en la descripción, no en el nombre.

### Clase 04 - `batch_tools_04.py`
- **Tema:** el meta-patrón del batch tool.
- **Idea clave:** `batch_tool` es un meta-tool cuyo schema es un array de invocaciones `{name, arguments}`. Permite que Claude pida varias llamadas de tool en un solo turno en vez de separadas.
- **Mejores prácticas:**
  - Alterna comportamiento incluyendo o excluyendo `batch_tool_schema` de la lista `tools` — mismo código, estrategia de agente diferente.
  - Trade-offs: menos round trips y agrupamiento atómico vs. manejo de errores más grueso (una invocación mala puede complicar el reporte de error).
  - Útil cuando las acciones son independientes y prefieres determinismo sobre paralelismo.

### Clase 05 - `tools_for_structure_data_05.py`
- **Tema:** usar tools como mecanismo de structured output.
- **Idea clave:** Genera el artículo como texto libre primero, luego en una llamada de seguimiento fuerza `tool_choice={"type":"tool","name":"article_summary"}`. Los campos estructurados (`title`, `author`, `key_insights`) regresan en `response.content[0].input` — tipados y validados por schema.
- **Mejores prácticas:**
  - Para structured output, **prefiere tools sobre prefill+regex**. El schema lo impone el API, no tu parser.
  - Usa `tool_choice={"type":"tool","name":...}` para forzar un tool específico cuando no quieras que Claude decida.
  - Usa `tool_choice={"type":"any"}` para requerir *algún* tool pero dejar que Claude elija cuál.

### Clase 06 - `fine_grained_tool_calling_stream_06.py` / `fine_grained_tool_calling_stream_06_2.py`
- **Tema:** streaming de argumentos de tool.
- **Idea clave:** El streaming default bufferea los argumentos del tool y los valida como JSON antes de soltar chunks. Con `betas=["fine-grained-tool-streaming-2025-05-14"]` recibes JSON parcial más temprano — pero pierdes la validación. El segundo archivo deliberadamente produce `meta.word_count = undefined` para demostrar la falla.
- **Mejores prácticas:**
  - Default a **streaming estándar**. Solo activa fine-grained cuando necesitas reaccionar a inputs parciales del tool en tiempo real (p.ej., updates de UI en vivo mientras el modelo aún compone la llamada).
  - Cuando fine-grained está activo, escribe código defensivo en el cliente: asume que cualquier JSON parcial podría estar malformado.

### Clase 07 - `text_edit_tool_07.py`
- **Tema:** el text-edit tool predefinido de Anthropic (`str_replace_based_edit_tool`).
- **Idea clave:** Claude ya conoce el schema (`view`, `str_replace`, `create`, `insert`, `undo_edit`) — tú implementas el comportamiento. `TextEditorTool` agrega path sandboxing, backups en disco, semánticas exactas de string para `str_replace`, y un stack de undo.
- **Mejores prácticas:**
  - **Siempre sandboxea el directorio de trabajo.** Rechaza paths con `..`, paths absolutos fuera del sandbox, o symlinks apuntando hacia afuera.
  - Respalda archivos antes de mutarlos; expón `undo_edit` para que Claude (o un humano) pueda hacer rollback.
  - `str_replace` requiere el string viejo *exacto* — falla ruidosamente cuando no es único.

### Clase 08 - `web_search_tool_08.py`
- **Tema:** el web search tool nativo de Anthropic (`web_search_20250305`).
- **Idea clave:** A diferencia de text-edit, la búsqueda en sí corre del lado de Anthropic. Tú declaras solo el schema y opcionalmente fijas límites.
- **Mejores prácticas:**
  - Limita con `max_uses` para prevenir presupuestos de query desbocados.
  - Usa `allowed_domains` (o `blocked_domains`) cuando necesites fuentes confiables — p.ej., restringir a docs oficiales, publishers peer-reviewed, o tu propio dominio.
  - Si ruteas por un proxy (LiteLLM, gateway custom), confirma que el proxy soporte server tools de Anthropic, no solo generación de texto.

---

## Módulo 04 - Advanced
Este módulo agrupa las capacidades más potentes del API: extended thinking, vision, PDFs, citations, prompt caching y code execution. Estas son palancas — jálalas después de tener un baseline funcionando y una evaluación, no antes.

### Clase 01 - `extended_thinking_01.py`
- **Tema:** extended thinking.
- **Idea clave:** Claude devuelve un bloque `thinking` además del texto final. Pagas más tokens y latencia por razonamiento medible-mente mejor en tareas duras.
- **Mejores prácticas:**
  - `thinking={"type":"enabled","budget_tokens":N}` con `N >= 1024`; `max_tokens` debe ser **estrictamente mayor** que `budget_tokens`.
  - Al continuar una conversación, **regresa el bloque `thinking` sin modificar**, incluyendo su campo `signature`. Mutar el bloque invalida la signature y el API rechazará el request.
  - Puedes recibir bloques `redacted_thinking` (razonamiento interno encriptado). No puedes leerlos pero debes incluirlos en turnos siguientes.
  - Usa thinking después de optimizar el prompt, no como curita para un prompt débil.

### Clase 02 - `image_support_02.py`
- **Tema:** vision con imágenes.
- **Idea clave:** Hasta 100 imágenes por request, codificadas en base64 como `{"type":"image","source":{"type":"base64","media_type":"image/png","data":<b64>}}`. El ejemplo pide un fire-risk rating con checklist numerada; el prompt hace la mayor parte del trabajo.
- **Mejores prácticas:**
  - Trata vision como **un problema de prompt engineering**: dale a Claude pasos explícitos, criterios y un formato numérico de output. "¿Qué ves?" produce output vago; una checklist estructurada produce una respuesta calificable.
  - Para PNG/JPG/WebP/GIF usa el `media_type` que matchee. Evita imágenes enormes — escala a ~1568px en el lado largo; más grande cuesta más tokens sin ganancia de calidad.

### Clase 03 - `pdf_support_03.py`
- **Tema:** PDFs como bloques `document`.
- **Idea clave:** `{"type":"document","source":{"type":"base64","media_type":"application/pdf","data":<b64>}}`. Claude lee texto, tablas, charts e imágenes nativamente — no necesitas pipeline separado de extracción.
- **Mejores prácticas:**
  - Prueba el PDF support nativo antes de armar tu propio parser; para la mayoría de tareas de summarización/Q&A es suficiente.
  - Los PDFs pueden ser caros — combínalos con prompt caching cuando el mismo PDF se consulte muchas veces.

### Clase 04 - `citations_04.py`
- **Tema:** respuestas con grounding y citations.
- **Idea clave:** Pon `"citations": {"enabled": true}` en un bloque document. La respuesta contiene snippets y ubicaciones de la fuente — números de página para PDFs, rangos de caracteres para texto plano. El ejemplo muestra una fuente de texto plano con `{"type":"text","media_type":"text/plain","data":...}`.
- **Mejores prácticas:**
  - Usa citations para cualquier UI donde el usuario debe verificar afirmaciones (legal, médico, compliance, herramientas de soporte).
  - Renderiza citations en la UI como highlights cliqueables apuntando al source original — ese es el punto entero.
  - Citations funcionan mejor cuando el documento está razonablemente estructurado; blobs largos sin estructura producen rangos más vagos.

### Clase 05 - `prompt_caching_05.py`
- **Tema:** prompt caching.
- **Idea clave:** Marca un bloque de contenido con `cache_control={"type":"ephemeral"}`. Todo **antes e incluyendo** ese bloque se cachea; requests siguientes con el mismo prefijo reusan el trabajo de preprocesamiento de Claude.
- **Mejores prácticas:**
  - Los breakpoints de cache van en **prefijos estables**: system prompts largos, schemas de tools, documentos grandes, knowledge bases.
  - Cualquier cambio de carácter *antes* del breakpoint invalida el cache. Mantén contenido dinámico (query del usuario, timestamp actual) **después** del último breakpoint.
  - Hay un mínimo de tamaño antes de que se dispare un cache write (~1024 tokens para Sonnet/Haiku, ~4096 para Opus). Prefijos pequeños no se cachean.
  - TTL default ~5 minutos; long-TTL caching es un beta separado. Planea workflows para que los hits repetidos caigan dentro de la ventana.
  - Hasta 4 breakpoints de cache por request — los breakpoints más tempranos sirven como fallback si el prefijo más largo falla.

### Clase 06 - `code_execution_06.py`
- **Tema:** Files API + code execution tool (`code_execution_20250825`).
- **Idea clave:** `upload(FILE_PATH)` devuelve `file_metadata`. Inyéctalo como `{"type":"container_upload","file_id":file_metadata.id}`. Claude corre Python en un container aislado sin acceso a red.
- **Mejores prácticas:**
  - El container es **stateless entre ejecuciones** — cada bloque de código debe re-importar librerías y re-declarar variables. Dile esto a Claude explícitamente en el prompt (el ejemplo lo hace).
  - Úsalo para análisis de CSV, plotting, transformaciones de data — cualquier cosa donde correr código real sea más confiable que razonar sobre texto.
  - Los artefactos generados (charts, archivos transformados) regresan con sus propios `file_id`s y se pueden descargar.
  - No dependas de acceso a internet desde dentro del sandbox; está intencionalmente ausente por seguridad.

---

## Módulo 05 - MCP
Model Context Protocol es una forma estandarizada de darle a Claude acceso a tools, resources y prompts a través de un servidor. El `cli_project` del curso muestra el flujo completo con cliente y servidor en el mismo repo (solo por enseñanza — en producción viven separados).

### Clase 01 - `mcp_01.txt`
- **Tema:** qué es MCP y por qué existe.
- **Idea clave:** Sin MCP, cada integración son tools hechos a mano. Con MCP, publicas/consumes una interfaz y cualquier cliente compatible obtiene las mismas capacidades.
- **Mejores prácticas:**
  - Usa MCP cuando tienes integraciones que quieres compartir entre múltiples apps u organizaciones, o quieres consumir tooling de terceros sin escribir glue code.

### Clase 02 - `mcp_02.txt`
- **Tema:** el cliente MCP y el flujo del protocolo.
- **Idea clave:** El cliente lista tools, llama tools, y transporta mensajes. El protocolo es agnóstico al transporte: stdio, HTTP, WebSocket.
- **Mejores prácticas:**
  - Elige stdio para servidores de subproceso local, HTTP/WebSocket para remotos. La API del cliente es la misma.
  - Trata MCP como **una capa de integración**, no como un tool. Plomea tools/resources/prompts; no reemplaza tu lógica de negocio.

### Clase 03 - `mcp_03.txt`
- **Tema:** setup del proyecto CLI.
- **Idea clave:** Cliente+servidor en el mismo repo es puramente pedagógico. El proyecto simula documentos en memoria para darle al resto del módulo algo concreto que leer y editar.
- **Mejores prácticas:**
  - En sistemas reales, versiona el servidor independientemente y consúmelo como dependencia externa.

### Clase 04 - `mcp_04.txt`
- **Tema:** MCP Inspector.
- **Idea clave:** Inspector se conecta directamente a tu servidor, lista tools, y te deja llamarlos a mano. Es la forma más rápida de validar schemas y outputs.
- **Mejores prácticas:**
  - Siempre pasa los schemas por Inspector antes de cablearlos a Claude. Si Inspector no puede listar/llamar tus tools, Claude no tiene oportunidad.
  - Cuando algo se rompe, descarta el servidor con Inspector primero; solo entonces sospecha del modelo o del cliente.

### Clase 05 - `mcp_05.txt`
- **Tema:** tools en el lado del cliente MCP.
- **Idea clave:** `await session.list_tools()` devuelve definiciones de tools. `await session.call_tool(name, input)` ejecuta uno. Envuelve la sesión en una clase para manejar el ciclo de vida de la conexión.
- **Mejores prácticas:**
  - `ClientSession` requiere setup/teardown explícito — envuélvelo en un context manager `async` (`__aenter__`/`__aexit__`) para que las leaks no ocurran en paths de excepción.
  - Tu clase cliente es el puente entre la app host y el servidor; **mantén la lógica de negocio fuera de ella**.

### Clase 06 - `mcp_06.txt`
- **Tema:** resources en el servidor.
- **Idea clave:** Los resources son data read-only con un URI y `mime_type`. Pueden ser estáticos (`docs://list`) o templated (`docs://document/{id}`).
- **Mejores prácticas:**
  - Usa resources para contenido que **la app necesita conocer**, no el modelo: listas de autocomplete, índices de documentos, contexto precargado.
  - Elige URIs estables — la app y los tests las van a hardcodear.

### Clase 07 - `mcp_07.txt`
- **Tema:** resources del lado del cliente y menciones `@`.
- **Idea clave:** La app lee un resource (usando su `mimeType`) e inyecta el contenido al prompt antes de llamar a Claude. La UX de `@document` en herramientas de chat se construye sobre esto.
- **Mejores prácticas:**
  - Los resources son perfectos para UIs de mención `@` porque el usuario elige de una lista que la app *ya* trajo.

### Clase 08 - `mcp_08.txt`
- **Tema:** prompts en el servidor.
- **Idea clave:** Los prompts MCP son workflows predefinidos y parametrizados. Típicamente coordinan tools y contexto para hacer una tarea recurrente de manera conocida.
- **Mejores prácticas:**
  - Usa prompts cuando el mismo workflow multi-paso corre una y otra vez (formatear, resumir, transformar) y el usuario — no el modelo — debe dispararlo.

### Clase 09 - `mcp_09.txt`
- **Tema:** prompts en el lado del cliente y comandos `/`.
- **Idea clave:** El cliente puede `list_prompts`, `get_prompt(name, args)` e inyectar los mensajes resultantes a la conversación. Slash commands como `/format doc_id` mapean limpiamente a prompts.
- **Mejores prácticas:**
  - Los slash commands le dan a los usuarios una manera descubrible y de baja fricción de invocar prompts MCP en UIs de chat.

### Clase 10 - `mcp_10.txt`
- **Tema:** cuándo usar tools vs. resources vs. prompts.
- **Idea clave:** Los tools son **controlados-por-modelo**, los resources **controlados-por-app**, los prompts **controlados-por-usuario**. Este trío es la idea central de diseño de MCP.
- **Mejores prácticas:**
  - Antes de diseñar cualquier capacidad, pregunta: *¿quién jala el gatillo — el modelo, la app, o el usuario?*
    - Modelo → tool.
    - App → resource.
    - Usuario → prompt.

---

## Módulo 06 - RAG
`rag_02.md` es el corpus de ejemplo. Las clases 02, 03, 05, 06, 07, 08 y 09 contienen código; el resto son transcripts que construyen el modelo conceptual.

### Clase 01 - `rag_01.txt`
- **Tema:** qué es RAG y cuándo tiene sentido.
- **Idea clave:** Meter documentos enteros al context window no escala en costo, latencia o calidad. RAG parte el contenido, recupera solo las piezas relevantes, y envía esas.
- **Mejores prácticas:**
  - Antes de meterle a RAG, verifica si el documento cabe cómodamente en el context window. Si sí, solo pásalo (y usa prompt caching para queries repetidas — Módulo 04 Clase 05).
  - RAG es la herramienta correcta cuando el corpus es más grande que el context window, o las queries pegan solo a una fracción pequeña del contenido.

### Clase 02 - `text_to_chunks_02.py` / `rag_02.txt`
- **Tema:** estrategias de chunking.
- **Idea clave:** El chunking moldea una fracción grande de tu calidad de retrieval. Tres estrategias cubren la mayoría de casos:
  - **Por carácter** (`chunk_by_char`, default 150 chars + 20 overlap): baseline agnóstica al formato. Úsala cuando el input no tenga estructura.
  - **Por oración** (`chunk_by_sentence`, regex `(?<=[.!?])\s+`, 5 oraciones/chunk + 1 overlap): preserva unidades semánticas cuando no hay estructura Markdown.
  - **Por sección** (`chunk_by_section`, split en `\n## `): el gold standard cuando el documento es Markdown bien estructurado.
- **Mejores prácticas:**
  - **Siempre incluye overlap** para que una oración partida entre dos chunks no se pierda.
  - Un chunk malo que mezcla temas confunde el retrieval — verifica chunks visualmente antes de indexar el corpus completo.
  - Cuando dudes, empieza con chunking por sección; cae a chunking por carácter solo si la estructura no es confiable.

### Clase 03 - `embedding_03.py` / `rag_03.txt`
- **Tema:** embeddings.
- **Idea clave:** Un embedding mapea texto a un vector de floats de dimensión fija para que puedas comparar significado numéricamente. Anthropic no provee su propio modelo de embedding, así que el curso usa **Voyage AI** (`voyage-3-large`).
- **Mejores prácticas:**
  - Indexa documentos y queries con el **mismo modelo de embedding exacto**. Vectores de modelos diferentes no son comparables.
  - Usa `input_type="document"` al indexar, `input_type="query"` al hacer search. Los modelos Voyage especializan embeddings para cada rol y la calidad mejora medible-mente.
  - Pon `VOYAGE_API_KEY` en `.env` y cárgalo con `python-dotenv` (`load_dotenv()`).

### Clase 04 - `rag_04.txt`
- **Tema:** el pipeline RAG completo + cosine similarity.
- **Idea clave:** Pre-procesar → chunk → embed → normalizar → guardar en vector DB. En tiempo de query → embed query → búsqueda nearest-neighbor → ensamblar prompt → Claude. El retrieval rankea por **cosine similarity** (o su complemento, **cosine distance**).
  - `cosine_similarity = (A · B) / (|A| * |B|)`, rango `[-1, 1]`. `1` = misma dirección, `0` = sin relación, `-1` = opuestos.
  - `cosine_distance = 1 - cosine_similarity`, rango `[0, 2]`. **Más bajo es mejor.**
- **Mejores prácticas:**
  - La mayoría de vector DBs reportan cosine **distance**, no similarity — invierte tu modelo mental.
  - La normalización (magnitud → 1.0) usualmente la hace el API de embedding; rara vez la implementas tú mismo.

### Clase 05 - `implement_rag_05.py` / `rag_05.txt`
- **Tema:** implementando el `VectorIndex` en memoria y el retrieval.
- **Idea clave:** Cinco pasos concretos:
  1. Chunk del texto.
  2. `generate_embedding(chunks)` — batch-friendly (acepta string o lista).
  3. Guarda cada par `(embedding, {"content": chunk})` en `VectorIndex`.
  4. Embed la query del usuario.
  5. `store.search(user_embedding, k=2)` — devuelve los `k` chunks más cercanos con distancias.
- **Mejores prácticas:**
  - **Siempre guarda el texto del chunk original (o al menos un ID del chunk) como payload junto al vector.** Un embedding pelado no se puede ensamblar a un prompt.
  - Embed en batches (`generate_embedding(lista_de_chunks)`) para esquivar rate limits por request.
  - El ejemplo usa `k=2`, no `k=1` — muchas preguntas reales necesitan combinar info de múltiples secciones. Tunea `k` contra tu eval set.
  - `VectorIndex` clamp-ea `cosine_similarity` a `[-1, 1]` antes de calcular distance para evitar excursiones de floating-point como `1.00000001`.
  - Este ejemplo se detiene en el retrieval; en producción agregas los chunks recuperados más la pregunta del usuario en un prompt y mandas eso a Claude.

### Clase 06 - `bm25_06.py` / `rag_06.txt`
- **Tema:** límites de la búsqueda semántica pura → BM25 (Best Match 25) → búsqueda híbrida.
- **Idea clave:** La búsqueda semántica falla en strings exactos raros (`INC-2023-Q4-011`, números de ticket, códigos de error). En el demo del profesor, buscar "what happened with incident 2023" devolvió correctamente Sección 10 (que es sobre el incidente) **pero también Sección 3 financial analysis, que no menciona el incidente para nada**, y *no* devolvió Sección 2 que sí lo menciona tres veces. Pura semántica se distrae con la "vibe" del query y se pierde el identificador exacto.
- **Cómo funciona BM25 a alto nivel** (replicado en `BM25Index`):
  1. **Tokenizar** la query y cada documento. El tokenizer default baja a minúsculas y splittea en `\W+` (cualquier no-palabra). Puedes inyectar un tokenizer custom si tu dominio lo necesita.
  2. **Frecuencias de documento** (`_doc_freqs`): cuántos chunks contienen cada término al menos una vez.
  3. **IDF** (inverse document frequency, Okapi smoothed):
     `idf(t) = log(((N - df(t) + 0.5) / (df(t) + 0.5)) + 1)`. Términos raros pesan alto, términos comunes pesan casi cero.
  4. **Score BM25** por chunk:
     `score = Σ idf(t) * tf(t,d) * (k1+1) / (tf(t,d) + k1 * (1 - b + b * (|d|/avg_dl)))`
     donde `k1=1.5` controla cuánto penaliza la saturación de term frequency y `b=0.75` controla cuánto normaliza por largo del documento. Esos son los defaults estándar — no los toques sin un eval.
  5. Ordenar por score descendente, devolver top-k.
- **Mejores prácticas:**
  - Si tu dominio tiene IDs, números de ticket, códigos de error, nombres de modelo, SKUs, versiones (`v1.2.3`), o cualquier identificador raro-pero-exacto, **usa búsqueda híbrida desde el día uno**. El curso lo confirma con un ejemplo concreto donde semántica sola falla.
  - Mantén ambos índices (`VectorIndex` + `BM25Index`) detrás de la **misma forma de API** (`add_document({"content": chunk})` + `search(query, k)`) — así el merge step se vuelve mecánico y puedes intercambiar implementaciones.
  - **Build del índice diferido**: `BM25Index` recalcula `avg_doc_len` e `idf` solo cuando llamas `search()` por primera vez después de un `add_document()` (vía el flag `_index_built`). Útil para batch-add sin recomputar IDF en cada inserción.
  - **Normalización del score a "distance-like"**: la implementación convierte el score crudo BM25 (más alto = mejor) a `exp(-factor * raw_score)` (más bajo = mejor) con `score_normalization_factor=0.1`. Esto alinea la convención con la cosine distance del vector DB y permite que el merger híbrido las trate uniformemente.
  - **Tokenizer custom** vale la pena cuando tus IDs llevan puntuación significativa. El default `\W+` rompe `INC-2023-Q4-011` en `["inc", "2023", "q4", "011"]` — funciona porque cada parte es rara individualmente, pero un tokenizer que conserve el ID completo daría hits aún más precisos.
  - Para el merge step híbrido, los enfoques comunes son **reciprocal rank fusion (RRF)** o blending de scores ponderados — empieza con RRF, no tiene perillas que tunear.
  - BM25 **no entiende sinónimos** ("car" vs "vehicle") — ese sigue siendo el trabajo del lado semántico. Por eso son complementarios, no sustitutos.

### Clase 07 - `multi_index_rag_07.py` / `rag_07.txt`
- **Tema:** unir búsqueda semántica + BM25 en un solo `Retriever` y fusionar resultados con **Reciprocal Rank Fusion (RRF)**.
- **Idea clave:** Como `VectorIndex` y `BM25Index` exponen el mismo contrato (`add_document`/`add_documents`/`search`), envolverlos en una clase `Retriever` es trivial. El `Retriever` reenvía la query a *cada* índice, recolecta los resultados, y los fusiona con RRF para producir un ranking único. El demo confirma el fix: la query problemática `"what happened with incident 2023 Q4 011"` antes devolvía Sección 10 + Sección 3 (irrelevante); con híbrido devuelve **Sección 10 + Sección 2** (correcto), que era exactamente lo esperado.
- **Cómo funciona RRF** (la implementación está en `Retriever.search`):
  1. **Cada índice rankea por su cuenta**. Para query `"incident..."`, supón vector devuelve `[2, 7, 6]` y BM25 devuelve `[6, 2, 7]`.
  2. **Tabla de ranks por documento** — cada chunk junta el rango que recibió en cada índice (`inf` si no apareció).

     | chunk | rank vector | rank BM25 |
     |-------|-------------|-----------|
     | 2     | 1           | 2         |
     | 7     | 2           | 3         |
     | 6     | 3           | 1         |
  3. **Fórmula RRF**: `score(d) = Σ 1 / (k_rrf + rank_i(d))`, sumando sobre cada índice donde el doc apareció. `k_rrf=60` es el default canónico de la literatura — amortigua a los rankings altos para que un primer-lugar no aplaste todo lo demás.
  4. **Ordenar descendente por score**, devolver top-k. En el ejemplo: chunk 2 = `1/61 + 1/62 ≈ 0.0326` (gana), chunk 6 = `1/63 + 1/61 ≈ 0.0323`, chunk 7 = `1/62 + 1/63 ≈ 0.0320`.
- **Patrones de código que vale la pena copiar:**
  - **`SearchIndex` Protocol** (typing): contrato estructural que tanto `VectorIndex` como `BM25Index` cumplen sin herencia. Permite agregar un tercer índice mañana (p.ej., un knowledge graph, full-text search clásico) sin tocar el `Retriever`.
  - **`Retriever(*indexes: SearchIndex)`**: constructor variádico — el orden no importa porque RRF es simétrico. Se pasan tantos índices como se quiera.
  - **Over-fetch antes de fusionar**: `Retriever.search` pide `k * 5` resultados a cada índice antes de mergear, pero solo devuelve los `k` finales. Razón: un doc puede rankear bajo en un índice y altísimo en otro; si hubieras pedido solo `k`, lo descartarías antes de poder fusionarlo. Sobre-buscar es barato y mejora el recall.
  - **`id(doc)` como llave de dedup**: la implementación usa `id(doc_obj)` (identidad de Python) para identificar documentos únicos entre índices. Funciona porque ambos índices guardan el *mismo* dict cuando llamas `Retriever.add_document`. Si tus índices clonaran los docs, tendrías que dedupear por `content` o un ID explícito.
  - **`add_documents` bulk**: tanto `VectorIndex` como `BM25Index` exponen `add_documents([...])` para cargar todo en una llamada. Crítico con Voyage para no chocar contra rate limits — el comentario en el código (`Note: converted to a bulk operation to avoid rate limiting errors from VoyageAI`) lo confirma como gotcha real.
- **Mejores prácticas:**
  - **`k_rrf=60` es el default que sale en casi toda la literatura**. No lo toques sin un eval set — los efectos son sutiles y la sensibilidad es baja en ese rango.
  - **El `Retriever` es agnóstico al número de índices**. Mañana puedes agregar un tercer índice (full-text Postgres, Elasticsearch, knowledge graph) y el merge sigue funcionando idéntico — esa es la fuerza de RRF: fusiona N rankings sin requerir scores comparables entre sistemas.
  - **Sobre-buscar (`k * 5`) es barato y crítico**. No skimpees aquí; la calidad del resultado depende de tener un pool grande antes de fusionar.
  - **RRF ignora los scores absolutos** y solo usa rangos. Esa es feature, no bug — significa que no necesitas normalizar cosine distance vs BM25 score para que se hablen, RRF los homologa por posición.
  - **Cuando un documento aparece en *un solo* índice**, su contribución RRF es solo `1/(k_rrf + rank)` (la otra entrada se filtra por `inf`). Eso baja su score relativo a docs que aparecieron en múltiples índices — comportamiento deseado: queremos premiar el consenso.
  - Si un caso de uso requiere ponderar un índice más que otro (p.ej., BM25 más importante en dominios con muchos IDs), multiplica los términos de RRF: `score = w_v * 1/(k+rank_v) + w_b * 1/(k+rank_b)`. Empieza sin pesos.

### Clase 08 - `reranking_08.py` / `rag_08.txt`
- **Tema:** **re-ranking** con Claude como post-procesamiento sobre los resultados de retrieval híbrido para arreglar los casos de borde que ni semántica ni BM25 resuelven solos.
- **Idea clave:** Aún con búsqueda híbrida, queries con matices ("**eng** team" en vez de "engineering", combinar identificador exacto + intent semántico) pueden devolver el orden equivocado. Demo del profesor: query `"what did the engineering team do with incident 2023"` con híbrido sigue devolviendo Sección 10 primero, pero la realmente más relevante es Sección 2 (software engineering team). Solución: tomar los top-k del híbrido y mandárselos a Claude con un prompt que diga *"reordena estos documentos por relevancia a esta query"*. Después del re-ranker, Sección 2 sube al primer lugar — exactamente lo esperado.
- **Cómo funciona el re-ranker** (la implementación está en `reranker_fn` + `Retriever`):
  1. `Retriever.search` corre el híbrido normal (vector + BM25 + RRF) y obtiene top-k docs.
  2. Si `reranker_fn` está configurado, le pasa esos k docs + la query original.
  3. `reranker_fn` arma un prompt con cada doc envuelto en XML:
     ```
     <document>
       <document_id>{doc["id"]}</document_id>
       <document_content>{doc["content"]}</document_content>
     </document>
     ```
     y le pide a Claude que devuelva `{"document_ids": [...]}` ordenado por relevancia decreciente.
  4. Claude responde con la lista de IDs en el nuevo orden. El `Retriever` reordena los docs según esa lista, **preservando los scores RRF originales** (`original_scores = {id(doc): score for doc, score in result}`).
- **Por qué IDs en vez de texto completo** (esto es la sutileza más importante de la clase):
  - Si le pides a Claude que devuelva los chunks completos reordenados, tiene que **re-emitir todo el texto** — costoso en tokens y en latencia (decenas de miles de tokens copiados por nada).
  - En su lugar: `Retriever.add_document` auto-genera un ID aleatorio de 4 caracteres (`random.choices(ascii_letters + digits, k=4)`) si el doc no trae uno. Claude solo devuelve esa lista de IDs. La respuesta cabe en ~50 tokens en vez de miles.
  - Trade-off explícito: pagas un poco de complejidad de mapping (`doc_lookup = {doc["id"]: doc for doc in docs_only}`) a cambio de un orden de magnitud de ahorro en tokens de salida.
- **Patrones de código que vale la pena copiar:**
  - **`reranker_fn` como callback inyectado al `Retriever`** — el re-ranking es **opt-in**. Puedes correr el `Retriever` sin reranker para latencia mínima, o activarlo cuando la calidad importa más. No es una capa hardcoded.
  - **Modelo barato para el re-ranker**: el código usa `claude-haiku-4-5`, no Opus. El re-ranking es una tarea pequeña y enfocada (ordenar 2-10 docs por relevancia) — Haiku es más que suficiente y dramáticamente más barato/rápido.
  - **Prefill `` ```json `` + `stop_sequences=["```"]`**: el profesor explícitamente reconoce que se podría usar tools (Módulo 03 Clase 05) para forzar JSON estructurado, pero para este caso simple — un solo array de strings — el patrón prefill+stop es suficiente y mucho menos código. **Trade-off pragmático**: tools cuando el schema es complejo, prefill cuando es trivial.
  - **XML para listas de items repetidos**: Claude está muy bien entrenado en XML y maneja `<document>...<document>...` repetido sin confusión. Más confiable que markdown o listas planas cuando los items son grandes.
  - **Preservar scores originales**: el reranker solo cambia el orden, no los scores. La implementación mantiene los scores RRF originales para que el caller siga teniendo una métrica de confianza.
  - **`text_from_message` helper**: extrae solo bloques de tipo `text` de la respuesta de Claude — útil cuando una respuesta puede tener múltiples bloques (text + tool_use mezclados).
- **Mejores prácticas:**
  - **Re-rank solo el top-k del híbrido, nunca el corpus completo**. Si el híbrido falló en surfacar el doc correcto, el re-ranker no puede recuperarlo. **Por eso el over-fetch (`k * 5`) en RRF importa aún más cuando hay re-ranker después** — le da al re-ranker un pool más grande para escoger.
  - **Acepta el trade-off de latencia conscientemente**: re-ranker = 1 llamada extra a Claude por query (típicamente 500ms-2s con Haiku). Para chat asíncrono está bien; para autocompletado en tiempo real probablemente no.
  - **Usa Haiku (o el modelo más pequeño que cumpla el eval)** para re-ranking. La tarea no requiere razonamiento complejo, requiere comparación de relevancia — Haiku la borda al ~10% del costo de Opus.
  - **Genera IDs en `add_document`, no en search-time**. El ejemplo lo hace en `add_document` (con fallback en search por seguridad). Razón: si el mismo doc se mete en múltiples índices, debe tener el mismo ID en todos.
  - **IDs cortos están bien** (4 chars random = 14M+ combinaciones — suficiente para un retriever en memoria con cientos de chunks). Para corpus gigantes usa UUIDs.
  - **El re-ranker ve solo lo que el retriever surfaceó** — es una capa de refinamiento, no de descubrimiento. Si tu pipeline está perdiendo docs en el retrieval, mejorar el re-ranker no te va a salvar; mejora chunking, embeddings o el over-fetch primero.
  - **Mide el lift antes de poner en producción**: re-ranking siempre suena bien en teoría pero a veces el delta de calidad sobre híbrido bien tuneado es menor de lo que cuesta. Corre tu eval set con y sin re-ranker; el número decide.
  - **Combina con prompt caching** (Módulo 04 Clase 05) si el sistema/instrucciones del re-ranker son estables — solo la query y los docs cambian por request, así que el prefijo cacheado puede recortar costo y latencia significativamente.

### Clase 09 - `context_retrievals_09.py` / `rag_09.txt`
- **Tema:** **contextual retrieval** — agregar contexto generado por Claude a cada chunk *antes de indexarlo* para que no pierda referencia al documento original.
- **Idea clave:** Cuando partes un documento en chunks, cada chunk se vuelve un fragmento huérfano: la "Sección 2" no sabe que es parte de un reporte mayor, ni que viene después de la metodología, ni que el incidente que menciona también aparece en otra sección. Contextual retrieval arregla esto **antes** de indexar: para cada chunk, le pides a Claude que escriba un párrafo corto situando ese chunk dentro del documento completo, lo concatenas al chunk original (`context + "\n" + chunk`), y *eso* es lo que metes al `VectorIndex` y al `BM25Index`. El chunk ahora carga su propia metadata semántica y léxica → mejora retrieval en ambos índices simultáneamente.
- **Cómo funciona el pipeline** (la implementación está en `add_context` + el loop de contextualización):
  1. Para cada chunk, arma un prompt con: la fuente (todo el documento o un subset) en un tag `<document>` y el chunk objetivo en un tag `<chunk>`.
  2. Pide: *"Write a short and succinct snippet of text to situate this chunk within the overall source document for the purposes of improving search retrieval"*. Crítico: la instrucción explícita de **succinct** y *"answer only with the succinct context and nothing else"* — sin esto, Claude se va a poner verboso y ahogará la señal del chunk original.
  3. La función devuelve `context + "\n" + text_chunk` — el contexto al inicio, el chunk original abajo. Ese es el **contextualized chunk** que entra al retriever.
  4. Repetir para los N chunks → indexar todo de una vez.
- **El problema del documento que no cabe** (gotcha que el profesor cubre explícitamente):
  - Si tu documento original es más grande que el context window, no puedes meterlo entero en cada llamada de `add_context`.
  - **Solución del notebook**: combinar dos heurísticas al construir el "source text" para cada chunk:
    - `num_start_chunks=2` — primeros 2 chunks (típicamente abstract / TOC / intro → da contexto de qué es el documento entero).
    - `num_prev_chunks=2` — los 2 chunks justo antes del chunk objetivo (da contexto local inmediato).
  - El razonamiento: chunks de la mitad del documento que no son ni el intro ni vecinos directos contribuyen poco al contexto del chunk objetivo y solo gastarían tokens.
  - El código:
    ```python
    context_parts.extend(chunks[: min(num_start_chunks, len(chunks))])
    context_parts.extend(chunks[max(0, i - num_prev_chunks):i])
    ```
- **Ejemplo del demo**: para `chunks[5]` (Sección 2 software engineering), Claude generó algo como *"This is a chunk of section two from this larger report, and it is following the methodology and it's before financial analysis, and is a part of a larger report that covers 10 separate research domains."* — exactamente la metadata semántica que el chunk pelado no tenía.
- **Patrones de código que vale la pena copiar:**
  - **Modelo barato (`claude-haiku-4-5`)** para la contextualización. Misma lógica que el re-ranker: tarea pequeña y enfocada → Haiku basta y es ~10× más barato que Opus.
  - **`add_context` retorna concatenado**: el caller no tiene que recordar pegar el contexto al chunk — el helper lo hace en una línea: `return text_from_message(result) + "\n" + text_chunk`.
  - **Configurable, no hardcoded**: `num_start_chunks` y `num_prev_chunks` son variables explícitas. Cambia `(2, 2)` por `(0, 5)` o `(3, 3)` según tu corpus sin tocar el resto del código.
  - **Indexación bulk al final**: `retriever.add_documents([{"content": chunk} for chunk in contextualized_chunks])`. Una sola llamada para evitar rate limits de Voyage.
  - **Prompt mínimo + tags XML**: solo dos tags (`<document>`, `<chunk>`), una instrucción clara, una restricción de output (*"Answer only with..."*). El prompt entero cabe en ~150 tokens.
- **Mejores prácticas:**
  - **Esto es preprocesamiento, no query-time**. Pagas el costo *una vez* al indexar; las queries no cargan ese overhead. Es lo opuesto al re-ranker (Clase 08), que paga por-query.
  - **Costo lineal en número de chunks**: N chunks = N llamadas a Claude. Para 100 chunks con Haiku son centavos; para 100k chunks es un proyecto serio. Estima antes de correr.
  - **Combina obligatoriamente con prompt caching (Módulo 04 Clase 05)** si el documento fuente es grande y se repite en cada llamada. Anthropic publicó el blog "Introducing Contextual Retrieval" donde con caching el costo cae ~90%. Pones el documento fuente en un bloque `cache_control: ephemeral`, y solo el chunk objetivo cambia por llamada.
  - **El contexto debe ser CORTO** (1-3 oraciones). Si Claude escribe medio párrafo, el embedding del chunk se diluye y el chunk pierde especificidad — peor retrieval, no mejor. Refuerza la restricción en el prompt.
  - **Mejora ambos índices a la vez**: el contexto generado contiene tanto keywords útiles para BM25 (nombres de secciones, IDs vecinos, términos del título) como significado para embeddings. Por eso es complementario con la búsqueda híbrida — no la reemplaza.
  - **Re-indexar es caro**: si tu corpus muta a menudo, diseña para indexación incremental (solo contextualizar chunks nuevos/modificados) en vez de regenerar todo.
  - **Cuidado con la alucinación de contexto**: si los `num_start_chunks + num_prev_chunks` son muy poco representativos, Claude puede inventar relaciones que no existen ("este chunk habla de X, mencionado también en la sección Y" cuando Y ni existe). Si el corpus es ambiguo, sube `num_start_chunks` para anclar mejor o pasa el documento completo (con caching).
  - **Lugar en el stack**: contextual retrieval **se suma** a chunking + embeddings + BM25 + RRF + re-ranker. No los reemplaza. El paper de Anthropic mide ~49% de reducción en fallos de retrieval combinando contextual retrieval + re-ranking sobre baseline. La ganancia es mayor en documentos con muchos cross-references entre secciones.
  - **Pequeño detalle del demo**: el profesor admite que con la query del notebook ya teníamos buenos resultados sin contextual retrieval — la mejora se nota más en corpus complejos con interconexiones (legal, médico, reportes técnicos largos), no en queries que ya funcionaban con híbrido + reranker.

---

## Módulo 07 - Claude Code & Computer Use
Este módulo cambia de tono: en vez de armar piezas del API tú mismo, examinas **dos productos terminados de Anthropic** — Claude Code y Computer Use — como casos de estudio de agentes reales en producción. La idea no es solo aprender a usarlos, sino **destilar el patrón "agente"** observándolos por dentro: cómo deciden qué hacer, qué tools les dan, cómo manejan estado, dónde fallan.

### Clase 01 - `claude_code_01.txt`
- **Tema:** intro al módulo. Vista panorámica de Claude Code y Computer Use, y por qué son los ejemplos de agente que el curso usa.
- **Idea clave:** Un **agente** no es magia ni un modelo más grande — es el patrón que ya construiste en Módulo 03: `tool loop` + `system prompt` + `tools` + `state`. Claude Code y Computer Use son ese mismo loop, **escalado y endurecido**:
  - **Claude Code** = asistente de código en terminal. Sus tools típicos son leer/escribir archivos (Módulo 03 Clase 07), correr comandos shell, búsqueda en el repo.
  - **Computer Use** = un set de tools que le da a Claude la habilidad de mover mouse, escribir teclado, tomar screenshots — efectivamente operar una computadora como humano.
- **Por qué importan estos casos de estudio:**
  - Claude Code y Computer Use son **referencias canónicas** de cómo Anthropic mismo arma agentes — no ejemplos de tutorial. Si vas a construir un agente, copiar su forma te ahorra meses de re-aprender patrones que ya están resueltos.
  - Te permiten reconocer la diferencia entre "un chatbot con un tool" (no es agente) y un agente real: **autonomía multi-paso**, **observación → decisión → acción → re-observación**, **manejo de errores que no aborta el loop**, **memoria de progreso dentro de la tarea**.
- **Mejores prácticas (anticipadas para todo el módulo):**
  - **Antes de construir tu propio agente, usa Claude Code y Computer Use por al menos un día.** Te ahorras las primeras 10 ideas malas que ya están refutadas.
  - **El loop de Módulo 03 (`run_conversation`) es la espina dorsal**: cualquier agente que construyas va a ser una variante de ese loop. La diferencia entre un chatbot toy y un agente productivo está en los **tools que le des** y en el **system prompt** que defina su rol y límites — no en una arquitectura nueva.
  - **El system prompt de un agente es un documento operativo**, no una línea de tono. Define identidad, herramientas disponibles, política de errores, política de confirmación destructiva, formato de output, cuándo parar. Claude Code es 80% prompt + 20% tools.
  - **Sandbox primero, capacidades después**: tanto Claude Code como Computer Use operan con paths sandboxeados (Claude Code) o sesiones aisladas (Computer Use). Cuando construyas un agente que toca el sistema, sandbox antes de la primera demo, no después del primer incidente.
  - **Confirmación humana para acciones irreversibles**: borrar archivos, push, deploys, mensajes externos. Claude Code pregunta antes de ejecutar comandos potencialmente destructivos — copia ese patrón.
  - **Streaming + tool-use es el UX por defecto** para agentes interactivos: el usuario ve qué está haciendo Claude *mientras* lo hace, no después de 30 segundos en negro. Combina Módulo 01 Clase 05 (streaming) con Módulo 03 (tool loop).
  - **Evals son obligatorios para agentes de verdad**: un agente sin eval set es una demo. Aplica Módulo 02 / 02.1 a las tareas que tu agente debe poder hacer end-to-end, no solo a llamadas individuales.

### Clase 02 - `claude_code_02.txt`
- **Tema:** qué es Claude Code, qué tools trae de fábrica y cómo instalarlo.
- **Idea clave:** Claude Code es un programa que corre en tu terminal y combina tres tipos de capacidades en un solo agente:
  - **Tools básicos integrados**: search, read, edit de archivos. Estos cubren la mayoría del trabajo de programación día a día.
  - **Tools avanzados integrados**: web fetching y terminal access (correr comandos shell). Aquí Claude Code deja de ser "editor con AI" y se convierte en un agente que puede investigar, instalar dependencias, correr tests, hacer commits.
  - **Cliente MCP**: Claude Code consume servidores MCP (Módulo 05). Cualquier MCP server que escribas o instales se vuelve parte del toolset de Claude Code automáticamente — extensión sin tocar el binario.
- **Setup en 3 pasos** (los del transcript):
  1. **Verifica Node.js**: `npm help` en terminal. Si responde, ya lo tienes; si no, instala Node primero.
  2. **Instala Claude Code**: vía `npm install` (típicamente `npm install -g @anthropic-ai/claude-code` — checa docs oficiales para el comando exacto y actualizado).
  3. **Login**: corre `claude` en cualquier terminal — abrirá un flujo de autenticación contra tu cuenta Anthropic.
- **Guía oficial**: `docs.anthropic.com` — la fuente de verdad para flags, settings, troubleshooting y nuevos tools que se vayan agregando.
- **Mejores prácticas:**
  - **Cuenta de billing antes que nada**: cada sesión de Claude Code consume tokens contra tu cuenta Anthropic. Antes de soltarlo en un proyecto grande, revisa tu plan / límites — un agente loopeando sobre un repo entero puede ser caro.
  - **Encadena Claude Code con MCP servers que ya tienes**: si construiste un MCP server en Módulo 05 (o consumes uno de tu organización), Claude Code lo levanta como cliente. Tus integraciones se vuelven herramientas de codear sin escribir glue.
  - **Trata `claude` como un comando, no como una app**: corre `claude` dentro del directorio del proyecto que quieres tocar. El cwd al lanzar define el sandbox de archivos y el contexto.
  - **Empieza preguntando, no ordenando**: en sesiones nuevas, primero pídele a Claude Code que explore el repo (`"explica la arquitectura de este proyecto"`, `"qué hace este archivo"`). Le das contexto antes de pedir cambios — los cambios salen mejor.
  - **Conoce los slash commands**: Claude Code expone comandos como `/help`, `/clear`, `/config`, etc. (similar a los slash commands MCP del Módulo 05 Clase 09). Aprenderlos al inicio te ahorra pelearte con la UI después.
  - **Permisos antes de autonomía**: por defecto Claude Code pide confirmación antes de comandos shell potencialmente destructivos. Resiste la tentación de ponerlo en modo "yolo" hasta que confíes en el flujo de tu tarea — un `rm -rf` mal disparado no se deshace.
  - **Mismo patrón que tu propio agente**: lo que estás viendo bajo el capó es exactamente el `run_conversation` de Módulo 03 con el `text_edit_tool` (Clase 07) + acceso a shell + cliente MCP. No hay magia nueva — es composición de piezas que ya construiste.

### Clase 03 - `claude_code_03.txt`
- **Tema:** mindset, memoria persistente (`CLAUDE.md`), y dos workflows de alto rendimiento (plan-first y TDD) para usar Claude Code como un ingeniero más en el equipo, no como un autocomplete glorificado.
- **Idea clave central:** **Claude Code no es un escritor de código — es un colega ingeniero al que delegas trabajo end-to-end**. El cambio de mindset es: en vez de "ayúdame a escribir esta función", piensa "delégate este ticket". Setup inicial, diseño de features, escritura de código, escritura de tests, deployment, soporte — todo es delegable. El profesor lo demuestra desde el primer paso pidiéndole a Claude que lea el README y ejecute el setup completo (crear venv, activarlo, instalar deps).

#### `/init` y el sistema de memoria persistente (`CLAUDE.md`)
- `/init` escanea el repo y escribe lo que entendió sobre arquitectura, comandos importantes y coding style en un archivo `CLAUDE.md` (en el transcript dicho como "clod.md").
- **Ese archivo se incluye automáticamente como contexto en cada sesión futura** — es la memoria de largo plazo de Claude Code para tu proyecto. Sin él, cada sesión empieza desde cero.
- Puedes pasar directivas especiales al `/init` (p.ej., *"include detailed notes on defining MCP tools"*) para que Claude enfoque la escritura del `CLAUDE.md` en áreas que sabes que vas a necesitar.
- **Tres niveles de memoria** (los que el transcript llama "project, local, user"):
  - **Project memory** (`CLAUDE.md` versionado): compartida con todo el equipo. Va al repo, todos lo ven en sus sesiones.
  - **Local memory** (gitignored): tuya en este proyecto pero no compartida. Útil para preferencias personales que no quieres imponer al equipo.
  - **User memory**: aplica a todos tus proyectos en esta máquina. Para reglas que sigues siempre (p.ej., "siempre tipa los argumentos de funciones").
- **Atajo `#`**: si escribes `#` seguido de una nota dentro de Claude Code, te pregunta a cuál de las tres memorias agregarla y la appendea. Forma rápida de capturar reglas sin salir del flujo.
- Re-correr `/init` actualiza el `CLAUDE.md` cuando el proyecto evoluciona (nuevos comandos, nuevo coding style). También puedes editarlo a mano cuando sea trivial.

#### Git delegado
- Después de generar `CLAUDE.md`, el profesor delega *"stage y commit todos los cambios"* a Claude Code. Claude inspecciona el diff, escribe un mensaje descriptivo, y commitea — el humano no toca git.

#### Filosofía: "effort multiplier"
- Frase central del profesor: **"Claude Code es un effort multiplier. Pones poco esfuerzo, sale algo decente. Pones esfuerzo en cómo lo diriges, sale dramáticamente mejor."**
- Pedir *"haz una tool de Word/PDF a Markdown"* funciona — pero los dos workflows que siguen funcionan **mucho** mejor con solo unos minutos extra.

#### Workflow #1: Plan-first (3 pasos)
1. **Aterriza contexto**: identifica tú mismo los archivos relevantes y pídele a Claude que los lea (en el demo: `tools/math.py` para que vea cómo está armado un tool existente, `document.py` para que conozca `binary_document_to_markdown`).
2. **Pídele un plan, NO código**: describe la feature y di explícitamente *"plan it out, don't write code yet"*. Claude devuelve pasos detallados.
3. **Pídele que implemente el plan**: Claude ejecuta los pasos. En el demo: actualizó `document.py`, actualizó `main.py`, escribió tests, los corrió, **y agregó manejo de errores para archivos inexistentes / no soportados que el profesor ni siquiera pidió** — un buen plan deja a Claude espacio para hacer el trabajo bien.

#### Workflow #2: Test-Driven Development (TDD) con Claude
1. **`/clear`** — limpia la conversación. Crítico aquí porque el profesor está re-haciendo la misma feature; sin `/clear` Claude "copiaría" su solución anterior y el demo no probaría nada.
2. **Aterriza contexto** otra vez (los mismos archivos relevantes).
3. **Pídele tests, NO código**: *"qué tests podrías escribir para esta feature, no escribas código todavía"*. Claude propone una lista (en el demo: 8 tests).
4. **Selecciona los tests relevantes**: el profesor pide implementar tests 1-5 y descarta los más especializados. **Filtras tú, Claude no decide qué cubrir.**
5. **Pídele código que pase los tests**: Claude escribe la implementación iterando hasta que los tests pasan.
- TDD requiere más esfuerzo upfront (revisar tests propuestos) pero deja un suite ejecutable como red de seguridad — el código que sale ya tiene cobertura, no es un "trust me" del LLM.

#### Trucos del profesor
- **`git stash` para retry**: cuando quieres comparar dos enfoques sobre la misma feature, stashea los cambios de Claude del primer intento, vuelves a clean slate, y pruebas el segundo workflow.
- **`/clear` antes de cualquier task que no debe heredar contexto previo**: cuando arrancas una feature nueva no relacionada, cuando estás probando enfoques alternativos, o cuando notas que Claude se está "anclando" a una conversación previa que ya no aplica.

#### Mejores prácticas
- **Trata cada sesión como una colaboración con un ingeniero junior brillante pero amnésico**: brillante porque puede leer todo el repo y planear features completas; amnésico porque cada `/clear` reinicia su memoria. La memoria estable vive en `CLAUDE.md`, no en la conversación.
- **`CLAUDE.md` es un documento vivo, no autogenerado y olvidado**: trátalo como cualquier doc de onboarding del proyecto. Cuando agregues un nuevo comando, una nueva convención, o una decisión de arquitectura, anótalo (con `#` o editando directo).
- **No mezcles project memory con preferencias personales**: si quieres que Claude siempre te ponga emojis en commits pero el equipo no, eso va a **user memory** o **local memory** — no a project memory commiteada.
- **Plan-first es el default; TDD es para código crítico**: para features pequeñas o exploratorias, el workflow de 3 pasos (read → plan → implement) es suficiente. Para código en hot path (auth, billing, datos sensibles), el TDD justifica el overhead — los tests son la red real.
- **Identifica los archivos relevantes tú mismo, no le delegues eso a Claude al inicio**: tú sabes qué archivos son relevantes para una feature mejor que un grep. Decirle *"lee `document.py` y `tools/math.py`"* es 100× más confiable que *"busca lo que sea relevante en el repo"*.
- **Pedir un plan antes del código no es solo para Claude — también es para ti**: revisar el plan te obliga a pensar la feature antes de que el código exista. Si el plan está mal, lo corriges en 30 segundos; si lo descubres en el código ya escrito, son 10 minutos de retrabajo.
- **El truco de "describe la feature, di NO escribas código"** funciona porque Claude por defecto tiende a saltar a implementar. La instrucción explícita lo frena en seco y separa fases que en su cabeza están fundidas.
- **Cuando Claude agregue cosas que no pediste pero son razonables (manejo de errores, validaciones, tests adicionales), revísalas en vez de borrarlas**: Claude Code está calibrado para "lo que un ingeniero senior haría" — sus extras suelen ser correctos. Si no lo son, ese es feedback para ajustar el `CLAUDE.md`.
- **Combina el `CLAUDE.md` con prompt caching**: igual que cualquier prefijo estable largo, `CLAUDE.md` es candidato natural a cache (Módulo 04 Clase 05). Claude Code lo maneja internamente, pero recordar el principio importa cuando construyas tu propio agente.

### Clase 04 - `claude_code_04.txt`
- **Tema:** Claude Code como **cliente MCP**: conectar servidores MCP para expandir dinámicamente sus capacidades sin tocar el binario.
- **Idea clave:** Claude Code lleva un **cliente MCP embebido** (Módulo 05). Cualquier servidor MCP que registres pasa a formar parte de su toolset junto con los tools nativos (read/edit/shell). Esto convierte a Claude Code en una **plataforma extensible**: tu propio dominio (errores de prod, tickets, mensajería de equipo) se vuelve parte del flujo de codear sin que tengas que modificar Claude Code en sí.
- **Demo del profesor:** conecta Claude Code al mismo MCP server que construyó en clases previas (el que expone `document_path_to_markdown`). Una vez conectado, le pide a Claude Code *"convierte el contenido de este Word/PDF a Markdown"* — y Claude Code automáticamente descubre el tool nuevo y lo usa.
- **Setup en 3 pasos** (los del transcript):
  1. **Sal de la sesión activa** con `Ctrl+C` (no puedes registrar mientras `claude` corre).
  2. **Registra el server**: `claude mcp add` → te pide un nombre libre (en el demo: `Documents`) → te pide el comando que arranca el server (en el demo: `uv run main.py`).
  3. **Reinicia Claude Code** con `claude`. El nuevo tool ya aparece en su lista junto con los tools nativos.
- **Casos de uso sugeridos por el profesor** (estos definen para qué *vale la pena* registrar un MCP server):
  - **Sentry MCP**: Claude Code consulta detalles de errores de producción mientras debuggeas → no tienes que copiar stack traces a mano.
  - **Jira MCP**: Claude Code lee el ticket que estás trabajando → entiende el "por qué" de la feature, no solo el "qué".
  - **Slack MCP**: Claude Code te notifica cuando termina una tarea larga → no tienes que babysittear la terminal.
- **Mejores prácticas:**
  - **Nombre del MCP server** = identificador local; ponlo descriptivo (`Documents`, `Sentry`, `Jira-Acme`) porque vas a verlo en `/help` y en logs cuando algo falle.
  - **El comando de arranque debe poder correr sin estado del cwd actual**: si registras `uv run main.py`, Claude Code lo va a invocar desde donde sea que tú estés. Usa paths absolutos en el comando si el server depende de archivos específicos, o cd dentro del comando.
  - **Registra una vez, usa siempre**: `claude mcp add` persiste el registro. No tienes que volver a configurarlo en cada sesión — pero sí tienes que **reiniciar `claude`** después de agregar/quitar servers para que recargue.
  - **Valida con MCP Inspector primero** (Módulo 05 Clase 04): si `claude` no ve tu tool, antes de blame Claude Code, conecta Inspector al server y confirma que `list_tools` lo expone correctamente.
  - **Empieza con un MCP "documental" antes que uno "ejecutor"**: Sentry/Jira (read-only) son apuestas seguras para tu primer MCP en Claude Code. Slack (write) y deploys requieren más cuidado con permisos — agrégalos cuando ya confíes en el flujo.
  - **MCPs personales vs del equipo**: registros de `claude mcp add` por defecto son tuyos. Si tu equipo se va a beneficiar del mismo set de MCPs, documenta los comandos de registro en el README del proyecto (o en el `CLAUDE.md`) para que cada miembro corra los mismos.
  - **Combina con el patrón "delegar tickets" de la Clase 03**: con Jira MCP + Sentry MCP + el repo + Slack MCP en una sesión, Claude Code puede leer un ticket → consultar el error en Sentry → escribir el fix → correr tests → commitear → mensajearte por Slack cuando termina. Eso es agente productivo, no demo de tutorial.
  - **Trata MCP servers como un toolkit extensible, no como un add-on**: la diferencia entre "Claude Code que escribe código" y "Claude Code que opera tu workflow" son los MCPs que enchufes. Esa es la palanca de mayor ROI del módulo.
  - **Cuidado con `Ctrl+C` para salir**: el transcript menciona que el profesor termina la sesión con `Ctrl+C` antes de registrar — confirma que no estás en medio de una tarea destructiva (el agente puede estar a media operación de archivos).

### Clase 05 - `claude_code_05.txt`
- **Tema:** **paralelismo con git worktrees + custom slash commands** — comandar varios Claude Codes a la vez como un equipo de ingenieros virtuales, sin que se pisen los archivos entre ellos.
- **Idea clave:** Claude Code es un proceso ligero — puedes correr **N instancias en paralelo**, cada una atacando un ticket distinto. El cuello de botella deja de ser cuán rápido escribe Claude y pasa a ser cuántas branches puedes revisar al mismo tiempo. La frase del profesor: *"un solo developer comandando su propio equipo de ingenieros virtuales"*.
- **El problema (race condition de archivos):** dos instancias de Claude editando el mismo archivo al mismo tiempo escriben código conflictivo o inválido — ninguna sabe de la otra. La solución no es coordinación entre Claudes (imposible, son procesos independientes), es **aislarlos físicamente**: cada uno en su propio workspace.

#### Git worktrees como primitive de aislamiento
- `git worktree` permite tener **una copia completa del repo en un directorio separado, en su propia branch**. Es como branching pero con árbol de archivos físico, no solo lógico.
- Cada worktree → su propio Claude Code → su propia feature → no se pisan.
- Cuando una feature está lista, se commitea en su branch y se mergea a `main` como cualquier branch normal.
- En el demo: el profesor crea `trees/feature_A`, `trees/feature_B`, etc. — un subdirectorio por feature.

#### Delegar la creación del worktree a Claude
- Crear un worktree a mano es repetitivo (`git worktree add`, symlinkear venv/`.env`, abrir editor). El profesor delega ese flujo a Claude Code mismo con un prompt:
  *"crea un worktree en `trees/feature_A`, symlinkea las dependencias que no están en git, y abre el editor en ese directorio"*.
- **Por qué symlink y no copy de las dependencias**: los archivos no versionados (venv, `.env`, `node_modules`) no se copian al worktree. Symlinkearlos hace que cada Claude vea el mismo entorno sin duplicar gigabytes ni perder las API keys.

#### Custom slash commands (`.claude/commands/*.md`)
- Repetir el prompt del worktree cada vez es tedioso. Claude Code soporta **comandos personalizados** definidos como archivos Markdown:
  - Crea `.claude/commands/create_worktree.md` en tu repo.
  - Pega el prompt completo dentro.
  - Reinicia `claude`.
  - Ahora puedes invocar `/project:create_worktree` desde cualquier sesión.
- **Argumentos dinámicos con `$ARGUMENTS`**: reemplaza la parte hardcoded del prompt (p.ej., `feature_A`) por el placeholder literal `$ARGUMENTS` (mayúsculas, exacto). Al ejecutar `/project:create_worktree feature_B`, Claude Code sustituye `$ARGUMENTS` por `feature_B`.
- El nombre del archivo (`create_worktree.md`) define el nombre del comando (`/project:create_worktree`).
- **Versionado del slash command**: como vive en `.claude/commands/`, el archivo va al repo — todo el equipo recibe el mismo comando al pull.

#### Demo del flujo paralelo completo
1. El profesor corre `/project:create_worktree` cuatro veces, una por feature: tests de documentos, logging, dos tools nuevos, una tool de subtract.
2. Termina con cuatro editores abiertos, cada uno con su Claude Code corriendo, cada uno trabajando una feature distinta en paralelo.
3. Cuando cada Claude termina, le pide *"commitea los cambios"* en su worktree.
4. Para mergear, define **otro custom command** `/project:merge_worktree` cuyo prompt es: *"ve al worktree X, mira el último commit para entender qué se hizo, e intenta mergearlo a main"*.
5. Lo corre cuatro veces. **Cuando hay conflicto en el merge de subtract, Claude Code resuelve el conflicto automáticamente** — no por magia sino porque tiene el contexto del commit y puede inspeccionar el conflicto.
6. Cleanup: pide a Claude que borre los worktrees al final.

#### Mejores prácticas
- **Tu cuello de botella es el review, no la generación**: 4 Claudes en paralelo son geniales si puedes revisar 4 PRs decentemente. Si terminas mergeando código sin leer porque "Claude lo escribió", estás auto-introduciendo bugs a velocidad 4×. Empieza con 2 instancias en paralelo y sube cuando confíes en tu velocidad de review.
- **Una feature = una worktree = una branch**: mantén el mapping 1:1. Worktrees compartidos entre tareas re-introducen el problema que estabas resolviendo.
- **Symlinkea, no copies, los archivos no versionados**: venvs y `.env` son grandes y/o sensibles. Symlinks comparten el mismo archivo físico — un cambio en un worktree se refleja en todos. Si necesitas entornos *aislados* (p.ej., diferente versión de Python), entonces sí copias o creas venvs nuevos.
- **`.claude/commands/*.md` es el mecanismo de "playbook compartido"**: cualquier flujo que tu equipo ejecuta más de dos veces (crear worktree, mergear, deploy a staging, generar release notes) es candidato a custom command. El equipo entero los hereda al hacer pull.
- **`$ARGUMENTS` es literal y único**: el placeholder es exactamente `$ARGUMENTS` (en mayúsculas). Si necesitas múltiples argumentos posicionales, parsea dentro del prompt (*"el primer argumento es la feature, el segundo es la branch base"*) — Claude Code te da una sola string.
- **Reinicia `claude` después de agregar/editar commands**: igual que con MCP servers, los commands se cargan al arranque. Ediciones en caliente no se ven sin restart.
- **No auto-mergees ramas críticas**: que Claude pueda resolver conflictos no significa que deba hacerlo en `main` de producción sin review. Para hot paths (auth, billing, schemas de DB), el merge sigue siendo manual aunque la branch venga de un worktree de Claude.
- **Convención de nombres de worktrees**: el profesor usa `trees/feature_A`. Mantén una convención (`trees/`, `worktrees/`, `wt/`) y agrégala a `.gitignore` para no commitear accidentalmente metadata local. Git ya ignora subworktrees, pero los archivos symlinkeados pueden filtrarse según cómo los crees.
- **Limpia worktrees al terminar**: `git worktree list` muestra todos los activos; `git worktree remove <path>` los borra cuando ya no se necesitan. Worktrees viejos sin limpiar acumulan disk y confunden al equipo.
- **Combina con el "delegar tickets" de Clase 03 + MCPs de Clase 04**: el endgame del módulo es: cliente Jira lee 4 tickets → un script crea 4 worktrees con `/project:create_worktree` → cada Claude resuelve su ticket → custom command mergea → Slack te avisa. Eso ya no es "usar Claude Code", es **operar un equipo virtual con un comando**.
- **El patrón generaliza más allá de Claude Code**: la idea de "aislar workspace por agente paralelo" aplica a cualquier sistema multi-agente que toque archivos compartidos. Worktrees es la implementación específica para agentes-de-código; para agentes-de-data podrías usar databases temporales o branches de S3.

### Clase 06 - `claude_code_06.txt`
- **Tema:** **Claude Code en CI/CD** — correr Claude Code de forma no-interactiva en GitHub Actions para monitorear logs de producción, detectar errores, escribir el fix y abrir el PR automáticamente.
- **Idea clave:** Claude Code no tiene que vivir solo en tu terminal. Es un binario que se instala con `npm`, así que puedes meterlo dentro de un GitHub Action y darle un prompt como input. Lo que cambia respecto al uso interactivo es que ahora Claude **arranca con una directiva, ejecuta hasta cumplirla, abre PR y termina** — no espera que un humano se siente a teclear. Eso convierte el patrón "Claude como ingeniero virtual" (Clases 03–05) en algo que corre 24/7 sin que estés ahí.
- **Demo del profesor:** Una app chatbot que funciona en local pero falla en producción (AWS Amplify). Local responde *"1+1 = 2"* y genera un spreadsheet con data fake; producción genera el mismo spreadsheet **vacío**. La causa real (vista en CloudWatch): *"the provided model identifier is invalid"* — un typo en el ID del modelo que solo se usa en el env de producción. El engineer podría haberlo encontrado a mano, pero el demo muestra Claude haciéndolo solo:
  1. GitHub Action programado para correr **temprano cada mañana** (`cron`).
  2. Action hace checkout del repo, instala dependencias, **instala Claude Code y AWS CLI**.
  3. Pasa un prompt a Claude: *"consulta CloudWatch, trae los errores de las últimas 24 h, dedup y trúncalos a una cantidad manejable, e intenta corregir cada uno"*.
  4. Claude itera errores, escribe los fixes, **commitea**, **abre un Pull Request**.
  5. El engineer despierta y encuentra un PR con: descripción del problema en lenguaje claro + diff con el fix. Solo revisa y mergea.
- **Por qué funciona** (la sutileza pedagógica que el profesor nombra al final):
  - Claude Code es **flexible**: no es una app, es un comando. Cualquier flujo que un humano haría con él puede empaquetarse como prompt + script.
  - El **PR como output** es el control de seguridad: Claude no toca producción, solo propone cambios que pasan por el code review normal del equipo.
  - El humano sigue siendo el aprobador final — Claude reduce el time-to-fix-proposal, no salta el gate de calidad.
- **Mejores prácticas:**
  - **Dedup + truncate de logs antes de pasarlos al modelo**: CloudWatch puede escupir miles de líneas idénticas (mismo error N veces). Métete el dedup en el prompt o pre-procesa con `awk`/`jq` antes — pasarle 10k errores idénticos a Claude no ayuda y consume context window. El profesor lo nombra explícitamente como parte del prompt.
  - **Programa el job en ventana de baja actividad**: el demo lo corre **temprano en la mañana**. Razón: si abres PRs durante el horario laboral, compiten con el trabajo activo del equipo y el reviewer no está fresco. Tener el PR listo *antes* del standup cambia la dinámica.
  - **Cap de errores por iteración**: Claude tiene un context window finito. Si tu app genera 200 errores únicos al día, no se los mandes todos; toma top-N por frecuencia o por severidad. Mejor 5 fixes correctos que 50 fixes confusos.
  - **PR, nunca auto-commit a `main`**: el demo abre un PR — copia ese patrón. **No le des permiso de merge**, ni siquiera para fixes "obvios". El branch + PR + review + merge es la separación de poderes que te salva cuando Claude tiene un mal día.
  - **API keys en GitHub Actions Secrets**: la key de Anthropic, credenciales AWS, cualquier token va en `Settings → Secrets and variables → Actions`, nunca hardcodeado en el workflow. El job lee `${{ secrets.ANTHROPIC_API_KEY }}`, etc.
  - **Permisos mínimos para el bot de PR**: si Claude abre PRs como un user dedicado (recomendado vs. tu propia identidad), dale solo permisos de `contents: write` + `pull-requests: write`. No le des `admin`, ni `deployments`, ni acceso a otros repos.
  - **Vincula el flujo a tu observability stack actual**: el demo usa CloudWatch porque la app está en AWS. Si usas Sentry, Datadog, GCP Logging, Honeycomb — el patrón es idéntico, solo cambia el CLI/SDK que el job invoque para traer logs. Combina con el MCP server de Sentry de la Clase 04 si prefieres no instalar CLIs.
  - **Limita el costo del job**: cada corrida es 1+ llamadas a Claude. Pon `timeout-minutes` en el step de GitHub Actions. Si el job se desboca (loop infinito de fixes), el límite te corta antes de quemar el presupuesto.
  - **No esperes que Claude arregle bugs de infra/config**: Claude solo ve el código del repo. Si el error es por un IAM role mal configurado, una env var faltante en el deploy, o una versión de runtime distinta — Claude va a *parecer* que arregla algo (puede tocar variables) pero no resuelve la causa raíz. El patrón funciona mejor para bugs que viven en el código (typos, edge cases, validaciones faltantes).
  - **El PR debe explicarse solo**: pídele a Claude en el prompt que el PR description incluya: el error original con stack trace, la causa raíz que detectó, el fix aplicado, y por qué ese fix es correcto. Sin eso, el reviewer tiene que reconstruir el razonamiento — y termina haciendo el debug que Claude ya hizo.
  - **El patrón generaliza a "agente de mantenimiento"**: misma idea aplica a cron jobs que actualicen dependencias (`npm audit fix` + tests + PR), corran linters fix-mode, completen TODOs marcados, traigan changelog summaries. Una vez que tienes la plomería de "Claude Code en CI", agregar más jobs es solo escribir más prompts.
  - **Cierra el loop de oncall**: este patrón cambia el SLO de "humano oncall responde en 15 min" a "Claude tiene un PR listo para cuando el humano abra el laptop". No reemplaza al oncall para incidentes graves (que requieren rollback inmediato), pero sí baja el ruido de bugs no-críticos que tradicionalmente se acumulan en el backlog.
  - **Mide el hit rate**: rastrea qué fracción de PRs autogenerados son útiles (mergeados sin cambios), parcialmente útiles (mergeados con tweaks), o descartados. Si <30% mergean limpios, ajusta el prompt o los criterios de error que recibe — el job está produciendo más ruido que valor.

### Clase 07 - `claude_code_07.txt`
- **Tema:** intro a **Computer Use** — Claude operando una computadora con mouse/teclado/screenshots dentro de un container Docker aislado, demostrado como un caso de uso de **QA testing automatizado** sobre una UI con bugs.
- **Idea clave:** Computer Use es la **otra cara del agente** del módulo. Mientras Claude Code te da un agente que opera sobre **archivos y shell** (un dominio textual y deterministra), Computer Use te da un agente que opera sobre **píxeles, cursor y eventos de teclado** (un dominio visual e impreciso). Mismo loop subyacente del Módulo 03, distinto set de tools. El cambio mental: pasar de *"Claude lee y edita código"* a *"Claude usa una app como un humano"*.
- **El problema del demo:** una app web pequeña con un text area que soporta menciones con `@` (estilo `@usuario`). Funciona bien al primer vistazo, pero tiene un bug *jankoso*: si agregas dos menciones y luego presionas backspace, aparece un popup en la **esquina superior izquierda** de la pantalla en vez de debajo del cursor. Encontrar y reproducir bugs visuales así a mano es lento y aburrido. Aquí entra Computer Use.
- **Setup que el profesor muestra (será replicado en clase próxima):**
  - **Lado derecho**: un browser corriendo **dentro de un container Docker** — el sandbox visual. El browser está totalmente aislado del sistema host: si Claude hace algo raro, no toca tu máquina real.
  - **Lado izquierdo**: un chat interface donde le das instrucciones a Claude. Claude lee, decide qué acción ejecutar (click, type, screenshot), la ejecuta dentro del container, observa el resultado, y vuelve a decidir.
- **El prompt (estructura QA):** el profesor le manda a Claude un prompt grande con cuatro partes:
  1. **Setup**: *"vas a hacer QA testing sobre un React component en `<URL>`"*.
  2. **Proceso de testing**: pasos generales que Claude debe seguir.
  3. **Test cases concretos**: tres tests específicos:
     - Verificar que las opciones de autocompletado aparezcan al teclear `@`.
     - Verificar que `Enter` inserte la mención.
     - Verificar que `Backspace` muestre las opciones **debajo de la mención**, no en la esquina superior izquierda.
  4. **Output esperado**: *"al final, escribe un reporte conciso con los resultados de cada test"*.
- **Resultado del demo:** Tests 1 y 2 pasan ✓. Test 3 **falla** ✗ — exactamente el bug que el profesor quería que detectara. Claude reporta el fallo claramente, dándole al engineer la pista para investigar a mano.
- **Por qué Computer Use existe** (la sutileza pedagógica):
  - Hay tareas que **no se pueden script-ear fácilmente**: QA en UI complejas, aceptación de flujos multi-paso, accessibility audits, llenar formularios en apps que no exponen API, validar dashboards visuales, comparar layouts entre browsers. Selenium/Playwright cubren parte, pero requieren código por test y se rompen con cada cambio de DOM.
  - Computer Use no se basa en selectores de DOM — **basa sus decisiones en lo que ve en la pantalla**, igual que un humano. Es robusto a refactors visuales que romperían un test de Playwright, pero más caro y menos preciso.
- **Mejores prácticas:**
  - **Estructura el prompt como un test plan, no como una conversación**: el prompt del demo es esencialmente un test plan formal: setup + steps + expected outcomes + report format. Aplica los mismos principios del Módulo 04 Clase 02 (vision): checklist numerada > pregunta abierta. *"Haz QA"* da output vago; *"corre estos 3 tests específicos y reporta pass/fail"* da output calificable.
  - **Sandboxea siempre con Docker** (o equivalente): Computer Use **opera teclado y mouse reales** desde el punto de vista del proceso. Si lo corres en tu desktop sin sandbox, un mal click puede borrar archivos, mandar mensajes, ejecutar comandos en ventanas abiertas. Docker container con su propio display virtual = aislamiento físico real, no solo lógico.
  - **No mezcles Computer Use y Claude Code para la misma tarea sin pensarlo**: si la tarea es *modificar código*, Claude Code es más rápido y barato. Si la tarea es *interactuar con una UI ya construida*, Computer Use. Hacer QA con Claude Code (corriendo Playwright) puede ser más barato si tu UI tiene tests automatizables; usar Computer Use solo cuando los tests visuales-humanos sean genuinamente necesarios.
  - **Cada acción cuesta tiempo y tokens**: cada ciclo de Computer Use es screenshot → modelo razona → decide acción → ejecuta → nuevo screenshot. Una sesión de 20 acciones es 20 screenshots en context window. Diseña tareas acotadas (3–10 acciones idealmente) y termínalas con un reporte explícito para no acumular history innecesario.
  - **El reporte conciso al final es crítico**: sin la instrucción explícita *"escribe un reporte conciso al final"*, te quedas con la transcripción cruda de acciones de Claude — útil para debug, malo para ver el resultado. El reporte es tu test report, **escríbelo en el prompt como requisito**.
  - **Espera resultados imperfectos**: en el demo, Claude reportó test 3 como "failed" — eso es la feature funcionando, no un fracaso. El valor no es que Claude arregle el bug, es que **lo encuentre y lo describa** sin que un humano tenga que reproducirlo. Que Computer Use te diga *"test 3 falló porque el popup apareció arriba a la izquierda"* es exactamente el ahorro.
  - **Diseña tests reproducibles**: igual que con cualquier eval (Módulo 02), un test de Computer Use que ejecutas hoy y mañana debería dar el mismo resultado modulo flakes visuales. Si tus tests dependen de timestamps, datos aleatorios o estado entre corridas, vas a tener falsos positivos/negativos. Inicializa la app a un estado conocido antes de cada batch.
  - **Usa Computer Use para regresión visual sobre tu propio producto**: cuando un cliente reporta *"la dropdown se ve raro en Safari mobile"*, en vez de reproducir a mano, le pasas el repro steps a Computer Use y dejas que valide la fix antes de mergear. El costo de una corrida vs. el costo de un round-trip humano-cliente justifica la inversión.
  - **No es un reemplazo de QA humano para producto crítico**: Computer Use es genial para regresiones, smoke tests y exploraciones — no para validar UX nueva donde el juicio "esto se siente raro" es el output deseado. Trátalo como un tester junior incansable, no como un product manager.
  - **Combinación con MCP servers (Clase 04)**: si tu MCP server expone *"abre un ticket de QA en Jira con el reporte"*, Computer Use puede correr el test, generar el report, y abrir el ticket de un solo viaje. Mismo patrón compositional que cierra el endgame del módulo.
  - **El bug del demo es deliberadamente UI-only**: el profesor eligió un bug que **solo se manifiesta visualmente** (popup en la esquina equivocada) — exactamente el tipo de cosas que tests unitarios de JS no atrapan. Esa es la zona donde Computer Use brilla: bugs que requieren ojos, no asserts.

### Clase 08 - `claude_code_08.txt`
- **Tema:** **cómo funciona Computer Use por debajo** — la revelación de que **no es un API nuevo**, es exactamente el mismo tool-use loop del Módulo 03 con un schema especial. Más cómo arrancar usando la reference implementation oficial de Anthropic.
- **Idea clave (la sutileza pedagógica que cierra el módulo):** **Computer Use está implementado *encima* del sistema de tools que ya conoces.** El profesor lo dice explícito: *"computer use itself is actually implemented with this exact same tool system"*. No hay magia oculta. El loop es idéntico al de `getWeather` del Módulo 03 Clase 01:
  1. Mandas un request con un schema especial.
  2. Claude responde con un `tool_use` part (id, name, input).
  3. **Tú** ejecutas la acción en tu entorno.
  4. Mandas el resultado de vuelta como `tool_result`.
  5. Repetir hasta `stop_reason != "tool_use"`.
- **El truco del schema "pequeño → grande":** lo que el profesor llama una característica importante de Computer Use:
  - Tú declaras un schema **pequeño** del lado del cliente (apenas el tipo de tool — algo como `{"type": "computer_20250124", "name": "computer", "display_width_px": ..., "display_height_px": ...}`).
  - Anthropic, **del lado del servidor, lo expande** internamente a un schema gigante que le dice a Claude que el tool `action` acepta argumentos como `mouse_move`, `left_click`, `screenshot`, `right_click`, `key`, `type`, `cursor_position`, etc.
  - Claude solo ve el schema expandido. Tú no tienes que escribir esa lista enorme de acciones — Anthropic la mantiene actualizada y tú solo declaras la versión.
  - Mismo patrón que `str_replace_based_edit_tool` (Módulo 03 Clase 07) y `web_search_20250305` (Módulo 03 Clase 08): **schemas pre-definidos versionados que Claude entiende nativamente**.
- **El "computing environment" lo provees tú:** Claude no toca tu computadora directamente — solo emite acciones. Es **tu código** el que recibe `{"action": "left_click", "coordinate": [400, 300]}` y se encarga de:
  - Mover el cursor del display virtual a (400, 300).
  - Disparar el evento de click.
  - Tomar un screenshot del nuevo estado.
  - Mandarlo de vuelta como `tool_result` con la imagen base64.
- **Cómo ejecutas las acciones reales:** un Docker container que corre:
  - Un display virtual (X11/Xvfb).
  - Un browser u otra app.
  - Un programa que recibe los `tool_use` blocks y los traduce a llamadas reales del sistema (`xdotool`, `pyautogui`, etc.).
  - Devuelve screenshots como bytes.
- **Reference implementation oficial de Anthropic:**
  - Docker container ya armado con todo el plomería: el display, el ejecutor de acciones, el bridge con Claude.
  - Setup mínimo: instala Docker → corre un comando → tienes la misma UI del demo de la Clase 07 (chat a la izquierda, browser a la derecha).
  - **Comando exacto del transcript** (imagen `ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest`):
    ```bash
    export ANTHROPIC_API_KEY="your api key"
    docker run \
        -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
        -v $HOME/.anthropic:/home/computeruse/.anthropic \
        -p 5900:5900 \
        -p 8501:8501 \
        -p 6080:6080 \
        -p 8080:8080 \
        -it ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest
    ```
  - **Anatomía del comando** (vale la pena entender qué hace cada flag, no solo copy-pegar):
    - `export ANTHROPIC_API_KEY="..."` → tu API key se exporta como env var del shell. **No la hardcodees** en el comando.
    - `-e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY` → pasa la env var del host **al container**. Sin esto, el container no puede llamar a la API.
    - `-v $HOME/.anthropic:/home/computeruse/.anthropic` → **bind mount**: comparte el directorio `~/.anthropic` del host con el container. Persiste settings/cache entre runs (no tienes que re-loguearte cada vez que reinicias).
    - `-p 5900:5900` → VNC server (acceso directo al display virtual con un cliente VNC).
    - `-p 8501:8501` → Streamlit UI (el chat con Claude del lado izquierdo de la demo).
    - `-p 6080:6080` → noVNC (cliente VNC en el browser — abrir `http://localhost:6080` te da el desktop sin instalar app extra).
    - `-p 8080:8080` → la UI combinada (chat + desktop en una sola página, lo más usual).
    - `-it` → modo interactivo con TTY → ves los logs en vivo y puedes hacer `Ctrl+C` para parar.
    - `ghcr.io/anthropics/...:computer-use-demo-latest` → imagen oficial de Anthropic en GitHub Container Registry, tag `latest`.
  - Una vez corriendo, abrir `http://localhost:8080` en el browser → ahí está la UI completa (chat + browser virtual).
  - Link en docs de Anthropic — checa antes de escribir tu propio executor.
- **Mejores prácticas:**
  - **Usa la reference implementation antes de armar la tuya**: ahorrarte semanas de plomería de display virtual y action executor. Empiezas productivo en 10 minutos. Cuando ya entiendes el flujo y necesitas customizar (otra arquitectura de container, otra app además de browser, integración con tus secrets), entonces forkeas.
  - **El loop de Módulo 03 sigue siendo el ground truth**: si Computer Use se comporta raro, la primera hipótesis no debería ser *"es un bug en Computer Use"*, debería ser *"se rompió el contrato de tool_use ↔ tool_result"*. Logea los `tool_use` blocks que llegan y los `tool_result` que mandas — el debug es idéntico al de Módulo 03 Clase 02.
  - **`is_error: true` también aplica aquí**: si la acción falla (la app crasheó, el coordinate está fuera de pantalla, el browser se congeló), devuelve `tool_result` con `is_error: true` y un mensaje. Claude puede decidir reintentar, tomar otro screenshot, o reportar el fallo. El mismo patrón de recovery del Módulo 03 Clase 02.
  - **El schema versioned (`computer_20250124` y similares) cambia con el tiempo**: revisa la versión que estás declarando contra la última en docs. Versiones nuevas agregan acciones (scroll, drag, doble-click); versiones viejas funcionan pero pierden capacidades.
  - **Cada screenshot es una imagen en context window** (Módulo 04 Clase 02 aplica): los screenshots son grandes en tokens. Sesiones largas con muchos screenshots inflan el context rápido — limita la profundidad de la tarea o trunca screenshots viejos cuando el modelo ya no los necesite.
  - **Mismo principio de prompt caching (Módulo 04 Clase 05)**: el system prompt + el schema expandido + las instrucciones iniciales son prefijo estable → cachéalo. Solo los screenshots cambian de turno a turno.
  - **El "small schema → big schema" es el patrón general de Anthropic**: text editor, web search, code execution, computer use — todos son casos del mismo patrón. Cuando Anthropic anuncia un tool nuevo, la pregunta no es *"¿cómo lo uso?"*, sino *"¿cuál es el `type` que declaro y qué versión?"*. Lee el changelog de tools como leerías un changelog de cualquier API.
  - **No mezcles Computer Use con tools custom propios sin pensarlo**: técnicamente puedes tener `computer` + `get_user_preferences` + `read_database` en la misma request. Funciona, pero el modelo a veces se confunde de cuál tool usar para qué. Empieza con solo `computer` y agrega tools propios cuando entiendas el flujo.
  - **El insight pedagógico del módulo cierra aquí**: Claude Code (Clases 02–06) y Computer Use (Clases 07–08) son *exactamente la misma cosa* — agentes construidos con el tool loop del Módulo 03. La diferencia es solo qué tools les das (filesystem+shell vs mouse+keyboard+screenshot). Una vez que ves esto, construir tu propio agente especializado es decidir: *¿qué entorno controla? → ¿qué tools necesita? → schema → executor → loop*. Todo lo demás del módulo son optimizaciones sobre esa base.

---

## Takeaways Centrales del Curso
- **Trata prompts, tools y contexto como un solo sistema.** Un buen prompt con chunks malos falla silenciosamente; un gran chunk sin system prompt también.
- **Para output confiable, prefiere tools.** Tools > prefill+stop > parsing de texto libre. Cae al siguiente nivel solo cuando el anterior es imposible.
- **Evalúa antes de optimizar.** Temperature, extended thinking, caching, RAG, fine-grained streaming — todos son potentes, todos son desperdicio sin una eval que te diga si ayudaron.
- **MCP y RAG expanden el contexto de formas distintas.** MCP le da a Claude **capacidades** (tools, resources, prompts) que un sistema externo implementa. RAG le da a Claude **conocimiento** (chunks de tu data) seleccionados por query. Componen — un tool MCP puede hacer un lookup RAG.
- **API stateless, tú stateful.** Claude no tiene memoria entre requests. Cada `messages`, `system`, `tools`, bloque `thinking` debe re-enviarse. Persistir ese estado correctamente es trabajo del developer.
