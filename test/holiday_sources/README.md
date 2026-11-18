# Holiday source files

These files are the published documents that `test/test_holiday_golds.py` reads. The test compares each date in them with the date the engine resolves.

## Spanish regional holidays

Each page is the text of a resolution of the Dirección General de Trabajo that lists the regional holidays of one year. The test reads the table of each page.

| File | Year | Source |
|---|---|---|
| `es_boe_BOE-A-2022-16755.html` | 2023 | <https://www.boe.es/buscar/doc.php?id=BOE-A-2022-16755> |
| `es_boe_BOE-A-2023-22014.html` | 2024 | <https://www.boe.es/buscar/doc.php?id=BOE-A-2023-22014> |
| `es_boe_BOE-A-2024-21316.html` | 2025 | <https://www.boe.es/buscar/doc.php?id=BOE-A-2024-21316> |
| `es_boe_BOE-A-2025-21667.html` | 2026 | <https://www.boe.es/buscar/doc.php?id=BOE-A-2025-21667> |

Fuente de los datos: Agencia Estatal Boletín Oficial del Estado (https://www.boe.es).

The text of a legal provision is free of copyright (Real Decreto Legislativo 1/1996, article 13). The BOE legal notice allows reuse with this source line. The pages keep the BOE identifier and the date of the resolution.

## Portuguese municipal holidays

| File | Content |
|---|---|
| `feriados.tsv` | Fixed municipal holidays: date, holiday, municipalities. |
| `feriados_moveis.tsv` | Movable municipal holidays: rule, holiday, municipalities. |
| `municipios_portugal.csv` | Municipality name and the code of its subdivision. |

The tables come from the public gist <https://gist.github.com/JarbasAl/00ac648935e964a795e9b9fe4585c2a5>, written by the owner of this repository. They ship under the licence of this repository.
