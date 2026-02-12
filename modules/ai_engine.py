def procesar_lote_industrial(df):
    resultados = []
    # Usamos un contenedor vacío para actualizar el texto de estado sin romper la barra
    status_text = st.empty()
    progreso = st.progress(0)
    
    col_desc = next((c for c in ['DESCRIPCION CORTA', 'Descripción', 'Especificación'] if c in df.columns), df.columns[0])
    col_url = next((c for c in ['URL', 'Enlace', 'Link', 'URL (Opcional pero recomendada)'] if c in df.columns), None)

    total = len(df)
    for index, row in df.iterrows():
        # Actualización segura del progreso
        valor_progreso = (index + 1) / total
        progreso.progress(valor_progreso)
        
        nombre_prod = str(row[col_desc])[:30] if pd.notna(row[col_desc]) else "Sin nombre"
        status_text.text(f"Analizando {index + 1} de {total}: {nombre_prod}...")
        
        if pd.notna(row[col_desc]):
            url_val = row[col_url] if col_url else None
            datos = ejecutar_analisis_ia(row[col_desc], url_val)
            if datos:
                resultados.append({
                    "Descripción Original": row[col_desc],
                    "Producto Competidor": datos.get('comp', 'N/A'),
                    "Tienda (Venta)": datos.get('tienda', 'N/A'),
                    "Importador/Marca": datos.get('imp', 'N/A'),
                    "Precio": datos.get('precio', 0),
                    "Moneda": datos.get('moneda', 'N/A'),
                    "Presentación": datos.get('um', 'N/A'),
                    "Link Hallazgo": datos.get('link', 'N/A'),
                    "Análisis vs Würth": datos.get('vs', 'N/A')
                })
    
    status_text.empty() # Limpiar texto al finalizar
    return resultados
