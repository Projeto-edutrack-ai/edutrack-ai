# Design

Registrar edutrack_search_key em cada conexão SQLite, usando unicodedata.normalize(NFKD), casefold e remoção de caracteres combinantes. Normalizar o termo antes de escapar caracteres literais LIKE. Outros dialetos mantêm ILIKE. Não reescrever nomes ou criar colunas novas.

O cabeçalho usa position:sticky/top:0/z-index:40 para seu dropdown não ficar sob transformações das seções GSAP. Modais continuam z-50. A revisão visual real será confirmada pela aluna.

Referências: https://www.sqlite.org/lang_expr.html e https://docs.python.org/3/library/sqlite3.html .
