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

## Takeaways Centrales del Curso
- **Trata prompts, tools y contexto como un solo sistema.** Un buen prompt con chunks malos falla silenciosamente; un gran chunk sin system prompt también.
- **Para output confiable, prefiere tools.** Tools > prefill+stop > parsing de texto libre. Cae al siguiente nivel solo cuando el anterior es imposible.
- **Evalúa antes de optimizar.** Temperature, extended thinking, caching, RAG, fine-grained streaming — todos son potentes, todos son desperdicio sin una eval que te diga si ayudaron.
- **MCP y RAG expanden el contexto de formas distintas.** MCP le da a Claude **capacidades** (tools, resources, prompts) que un sistema externo implementa. RAG le da a Claude **conocimiento** (chunks de tu data) seleccionados por query. Componen — un tool MCP puede hacer un lookup RAG.
- **API stateless, tú stateful.** Claude no tiene memoria entre requests. Cada `messages`, `system`, `tools`, bloque `thinking` debe re-enviarse. Persistir ese estado correctamente es trabajo del developer.
