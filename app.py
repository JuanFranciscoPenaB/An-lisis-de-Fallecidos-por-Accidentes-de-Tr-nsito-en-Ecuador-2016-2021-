import streamlit as st
import pandas as pd
import plotly.express as px


from ydata_profiling import ProfileReport
from streamlit_ydata_profiling import st_profile_report

# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(
    page_title="Accidentes de Tránsito Ecuador",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# ESTILOS
# =====================================================

st.markdown("""
<style>

.titulo{
    color:#0B5394;
    font-size:38px;
    font-weight:bold;
}

.subtitulo{
    color:gray;
    font-size:18px;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# ENCABEZADO
# =====================================================

col_logo, col_titulo = st.columns([1,4])

with col_logo:
    try:
        st.image("logo_tecazuay.png", width=180)
    except:
        pass

with col_titulo:

    st.markdown("""
    <div class="titulo">
    🚗 Análisis de Fallecidos por Accidentes de Tránsito
    </div>

    <div class="subtitulo">
    Instituto Universitario TEC Azuay - Tecnología Superior en Big Data
    </div>
    """, unsafe_allow_html=True)

st.divider()

# =====================================================
# SIDEBAR
# =====================================================

try:
    st.sidebar.image(
        "logo_tecazuay.png",
        width=220
    )
except:
    pass

st.sidebar.title("Menú")

opcion = st.sidebar.radio(
    "Seleccione una opción",
    [
        "Inicio",
        "Tabla de Datos",
        "Estadísticas",
        "Gráficos",
        "YData Profiling"
    ]
)

# =====================================================
# CARGA DE DATOS DESDE CSV
# =====================================================
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_csv(
            "accidentes.csv",
            sep=";",
            encoding="latin1"
        )

        # Eliminar espacios en nombres de columnas
        df.columns = df.columns.str.strip()

        # Guardar nombres originales (ANTES de renombrar)
        columnas_antes = df.columns.tolist()

        # ==========================================
        # RENOMBRAR COLUMNAS
        # ==========================================
        df.rename(columns={
                "Género de la víctima": "Genero_Victima",
                "Tipo de accidente": "Tipo_Accidente",
                "Fecha de muerte Víctima": "Fecha_Muerte"
        }, inplace=True)

        # Guardar nombres nuevos (DESPUÉS de renombrar)
        columnas_despues = df.columns.tolist()

        # ==========================================
        # TRATAMIENTO DE VALORES NULOS
        # ==========================================

        columnas_numericas = df.select_dtypes(include="number").columns
        df[columnas_numericas] = (
           df[columnas_numericas]
           .fillna(0)
        )

        columnas_texto = df.select_dtypes(include="object").columns
        df[columnas_texto] = (
           df[columnas_texto]
           .fillna("No especificado")
        )

        # ==========================================
        # ELIMINAR DUPLICADOS
        # ==========================================
        duplicados_encontrados = int(df.duplicated().sum())
        df = df.drop_duplicates()

        return df, columnas_antes, columnas_despues, duplicados_encontrados

    except Exception as e:
        st.error(f"Error al cargar CSV: {e}")
        return None, None, None, None

# =====================================================
# CARGA DE DATOS
# =====================================================

df, columnas_antes, columnas_despues, duplicados_eliminados = cargar_datos()

if df is None:

    st.error("""
    No fue posible cargar los datos.

    Verifique:

    • Que el archivo accidentes.csv esté en la misma carpeta del script.
    • Que el separador sea punto y coma (;).
    • Que la codificación sea latin1.
    """)

    st.stop()

if df.empty:

    st.warning(
        "La tabla está vacía."
    )

    st.stop()

# =====================================================
# INICIO
# =====================================================

if opcion == "Inicio":

    st.header("📌 Resumen General")

    col1,col2,col3,col4 = st.columns(4)

    col1.metric(
        "📋 Registros",
        f"{len(df):,}"
    )

    col2.metric(
        "📌 Variables",
        len(df.columns)
    )

    col3.metric(
        "❌ Valores Nulos",
        int(df.isnull().sum().sum())
    )

    col4.metric(
        "🔁 Duplicados Eliminados",
        duplicados_eliminados
    )

    st.divider()

    # ==========================================
    # COMPARACIÓN DE NOMBRES DE COLUMNAS
    # ANTES vs DESPUÉS DEL RENOMBRADO
    # ==========================================

    st.subheader("🔤 Nombres de Columnas: Antes y Después")

    tabla_columnas = pd.DataFrame({
        "Columna Original": columnas_antes,
        "Columna Renombrada": columnas_despues
    })

    # Resaltar solo las filas donde el nombre cambió
    def resaltar_cambios(fila):
        if fila["Columna Original"] != fila["Columna Renombrada"]:
            return ["background-color: #FFD60A; color: #000000; font-weight: 600"] * len(fila)
        return [""] * len(fila)

    st.dataframe(
        tabla_columnas.style.apply(resaltar_cambios, axis=1),
        use_container_width=True
    )

    cambios = (tabla_columnas["Columna Original"] != tabla_columnas["Columna Renombrada"]).sum()

    st.info(f"Se renombraron {cambios} columna(s). Las filas resaltadas en amarillo muestran el cambio.")

# =====================================================
# TABLA
# =====================================================

elif opcion == "Tabla de Datos":

    st.header("Tabla de Datos")

    st.dataframe(
        df,
        use_container_width=True,
        height=600
    )

# =====================================================
# ESTADÍSTICAS
# =====================================================

elif opcion == "Estadísticas":

    st.header("📈 Información Descriptiva del Conjunto de Datos")

    # ==========================================
    # NÚMERO DE REGISTROS
    # ==========================================

    st.subheader("📋 Número de Registros")

    st.success(
        f"Total de registros: {df.shape[0]:,}"
    )

    # ==========================================
    # NÚMERO DE VARIABLES
    # ==========================================

    st.subheader("📌 Número de Variables")

    st.success(
        f"Total de variables: {df.shape[1]}"
    )

    # ==========================================
    # TIPOS DE DATOS
    # ==========================================

    st.subheader("📊 Tipos de Datos")

    tipos = pd.DataFrame(
        df.dtypes,
        columns=["Tipo de Dato"]
    )

    st.dataframe(
        tipos,
        use_container_width=True
    )

    # ==========================================
    # VALORES NULOS
    # ==========================================

    st.subheader("⚠️ Valores Nulos")

    nulos = pd.DataFrame(
        df.isnull().sum(),
        columns=["Cantidad"]
    )

    nulos["Porcentaje (%)"] = (
        nulos["Cantidad"] / len(df)
    ) * 100

    st.dataframe(
        nulos,
        use_container_width=True
    )

    # ==========================================
    # ESTADÍSTICAS DESCRIPTIVAS
    # ==========================================

    st.subheader("📉 Estadísticas Descriptivas")

    st.dataframe(
        df.describe(
            include="all"
        ),
        use_container_width=True
    )

    # ==========================================
    # INFORMACIÓN ADICIONAL
    # ==========================================

    st.subheader("🔍 Primeros 5 Registros")

    st.dataframe(
        df.head(),
        use_container_width=True
    )


    st.subheader("🔎 Últimos 5 Registros")

    st.dataframe(
        df.tail(),
        use_container_width=True
    )

    st.subheader("⚠️ Registros con Valores Nulos")
    registros_nulos=df[df.isnull().any(axis=1)]
    st.write(f"Total de registros con nulos: {len(registros_nulos)}")
    st.dataframe(
        registros_nulos,
        use_container_width=True
    )


    st.subheader("📈 Resumen General")

    col1, col2, col3, col4,col5,col6 = st.columns(6)

    with col1:
        st.metric(
            "Registros",
            f"{df.shape[0]:,}"
        )

    with col2:
        st.metric(
            "Variables",
            df.shape[1]
        )

    with col3:
        st.metric(
            "Nulos",
            int(df.isnull().sum().sum())
        )

    with col4:
        st.metric(
            "Duplicados",
            int(df.duplicated().sum())
        )
    with col5:
        st.metric(
        "📂 Columnas con Nulos",
        (df.isnull().sum() > 0).sum()
    )

    with col6:
        st.metric(
        "💾 Memoria (MB)",
        round(
            df.memory_usage(deep=True).sum() / 1024**2,
            2
        )
    )
    st.divider()

    st.subheader("📌 Detección de Valores Atípicos")

    columnas_numericas = df.select_dtypes(include="number").columns

    if len(columnas_numericas) > 0:

         variable = st.selectbox(
        "Seleccione una variable numérica",
        columnas_numericas
     )

         Q1 = df[variable].quantile(0.25)
         Q3 = df[variable].quantile(0.75)

         IQR = Q3 - Q1

         limite_inferior = Q1 - (1.5 * IQR)
         limite_superior = Q3 + (1.5 * IQR)

         outliers = df[
           (df[variable] < limite_inferior) |
           (df[variable] > limite_superior)
         ]

         c1, c2, c3 = st.columns(3)

         with c1:
           st.metric("Q1", round(Q1, 2))

         with c2:
          st.metric("Q3", round(Q3, 2))

         with c3:
          st.metric(
            "Outliers",
            len(outliers)
        )

         st.dataframe(
          outliers,
          use_container_width=True
         )

    else:
     st.warning(
        "No existen columnas numéricas para analizar."
     )

    st.subheader("📥 Descargar Datos Limpios")

    st.download_button(
      "📥 Descargar CSV",
      df.to_csv(
          index=False,
          sep=";"
      ).encode("utf-8"),
      "accidentes_limpio.csv",
      "text/csv"
    )
# =====================================================
# GRÁFICOS
# =====================================================

elif opcion == "Gráficos":

    st.header("📊 Dashboard de Visualización")

    # ==========================================
    # INDICADORES GENERALES
    # ==========================================

    st.subheader("📈 Indicadores Generales")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Registros",
        f"{df.shape[0]:,}"
    )

    c2.metric(
        "Variables",
        df.shape[1]
    )

    c3.metric(
        "Valores Nulos",
        int(df.isnull().sum().sum())
    )

    c4.metric(
        "Duplicados",
        int(df.duplicated().sum())
    )



    st.divider()

    # ==========================================
    # GRÁFICO 1
    # BARRAS HORIZONTALES
    # TOP 10 PROVINCIAS
    # ==========================================

    if "Provincia" in df.columns:

        st.subheader("🏛 Top 10 Provincias con Más Fallecidos")

        provincia = (
            df["Provincia"]
            .value_counts()
            .head(10)
        )

        fig1 = px.bar(
            x=provincia.values,
            y=provincia.index,
            orientation="h",
            text=provincia.values,
            title="Top 10 Provincias con Más Fallecidos"
        )

        fig1.update_layout(
            xaxis_title="Cantidad de Fallecidos",
            yaxis_title="Provincia",
            height=500
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

    # ==========================================
    # GRÁFICO 2
    # DONA / PIE CHART
    # TIPO DE ACCIDENTE
    # ==========================================

    if "Tipo_Accidente" in df.columns:

        st.subheader("🚗 Distribución por Tipo de Accidente")

        accidentes = (
            df["Tipo_Accidente"]
            .value_counts()
            .head(10)
        )

        fig2 = px.pie(
            names=accidentes.index,
            values=accidentes.values,
            hole=0.5,
            title="Distribución por Tipo de Accidente"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    # ==========================================
    # GRÁFICO 3
    # BARRAS VERTICALES
    # GÉNERO DE LA VÍCTIMA
    # ==========================================

    if "Genero_Victima" in df.columns:

        st.subheader("👥 Fallecidos por Género")

        genero = (
            df["Genero_Victima"]
            .value_counts()
        )

        fig3 = px.bar(
            x=genero.index,
            y=genero.values,
            text=genero.values,
            title="Fallecidos por Género"
        )

        fig3.update_layout(
            xaxis_title="Género",
            yaxis_title="Cantidad de Fallecidos",
            height=500
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

    # ==========================================
    # GRÁFICO 4
    # Gráfico de Líneas
    # Evolución de Fallecidos por Accidentes de Tránsito por Año
    # ==========================================

    st.subheader("📈 Evolución de Fallecidos por Accidentes de Tránsito por Año")

    df["Fecha_Muerte"] = pd.to_datetime(
    df["Fecha_Muerte"],
    errors="coerce"
)

    anios = (
    df["Fecha_Muerte"]
    .dt.year
    .value_counts()
    .sort_index()
)

    fig5 = px.line(
    x=anios.index,
    y=anios.values,
    markers=True,
    title="Tendencia Anual de Fallecidos por Accidentes de Tránsito en Ecuador (2016-2021)"
)

    fig5.update_layout(
    xaxis_title="Año",
    yaxis_title="Número de Fallecidos",
    height=500
)

    st.plotly_chart(
    fig5,
    use_container_width=True
)

# =====================================================
# YDATA PROFILING
# =====================================================

elif opcion == "YData Profiling":

    st.header("Perfilamiento")

    if st.button(
        "Generar Reporte"
    ):

        profile = ProfileReport(
            df,
            title="Reporte Accidentes",
            explorative=True
        )

        st_profile_report(
            profile
        )

    if st.button(
        "Descargar HTML"
    ):

        profile = ProfileReport(
            df,
            title="Reporte Accidentes",
            explorative=True
        )

        html = profile.to_html()

        st.download_button(
            "Guardar Reporte",
            html,
            file_name="reporte_accidentes.html",
            mime="text/html"
        )

# =====================================================
# FOOTER
# =====================================================

st.divider()

st.markdown("""
### Instituto Universitario TEC Azuay

**Carrera:** Tecnología Superior en Big Data

**Autor:** Juan Francisco Peña B.

**Tecnologías:**
Python · Streamlit · CSV · Plotly · YData Profiling
""")