# EquineLead: Data Analyst Executive Dashboard

## Descripción
Este directorio contiene la aplicación modular interactiva (Dashboard) diseñada por el rol de **Data Analyst**. Sirve como el entregable final ejecutivo que consolida métricas comerciales, validación de datos (Data Engineering), y resultados de modelos predictivos y A/B Tests (Data Science).

## Arquitectura (Estructura Senior)
El proyecto ha sido refactorizado usando los mejores estándares de la industria para aplicaciones Python/Streamlit:
- `app.py`: El punto de entrada principal (Router).
- `pages/`: Módulos que dividen lógicamente el Pitch Ejecutivo, la Validación de Datos, y el Simulador de ROI (Multipágina).
- `components/`: Componentes UI reutilizables (Tarjetas de KPIs, Alertas y Funciones de Matplotlib).
- `utils/`: Módulos con lógica de backend (Data Loaders con tipado fuerte y manejo de excepciones).

## Requisitos de Ejecución Local
Asegurarse de tener instalado `uv` (o `pip`) y ejecutar lo siguiente en la raíz del repositorio (`Data_Science_EquineLead`):

```bash
# 1. Instalar dependencias del Data Analyst
pip install -r Data_Analyst_Project/requirements.txt

# 2. Levantar la aplicación modular
streamlit run Data_Analyst_Project/app.py
```
