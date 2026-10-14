# Modelo SketchUp – Etapa 1 (verificación de metrados)

## Opción A (recomendada): SketchUp de escritorio 2017 o superior
1. Abre un modelo nuevo con la plantilla en **metros**.
2. Abre **Ventana > Consola Ruby**.
3. Escribe (con tu ruta): `load 'C:/Users/TU_USUARIO/Downloads/etapa1_sketchup.rb'`.
4. El modelo se arma solo y, al terminar, sale el **REPORTE DE METRADOS** medido sobre el modelo.

Cada partida queda en su propia **etiqueta (capa)**, por ejemplo `04.02 Vigas de equilibrio VE`, `04.09c Acero columnas` o `02.01 Excavacion zapatas`. Así puedes prender y apagar partidas.
- **Volumen:** selecciona un elemento y mira *Información de entidad*.
- **Acero:** cada grupo de acero guarda sus kg, metros y número de barras por diámetro en *Ventana > Atributos de componente*.

## Opción B: sin Ruby (SketchUp web o versiones sin consola)
Usa **Archivo > Importar** con `etapa1_modelo.dae`. Trae los mismos sólidos agrupados por partida, pero sin el acero ni el reporte.

## Convenciones
- Origen: x = 0 en el lindero A, y = 0 en el frente de la vivienda (eje 1), z = 0 en el NTN ±0.00. El cerco queda en y negativa.
- VE de −1.00 a −0.30 sobre tecnopor (E-10). VC de −1.50 a −1.10, modelada solo fuera de zapata (lo de adentro es concreto de zapata).
- Excavación: pozos con 0.10 de sobreancho (no en las caras de lindero) y zanjas solo entre pozos.
- **Cerco:** las columnas CA, la ZC y el cimiento corrido son referenciales porque falta el plano E-09. La VA del cerco no está modelada.
