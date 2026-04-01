# ⚜️ Intendencia Scout - Menú GSBV

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)

Una aplicación web interactiva diseñada para facilitar la logística de cocina en grupos scouts. Olvida las hojas de cálculo infinitas; planifica tu campamento, calcula raciones según la edad y genera tu lista de la compra en segundos.

[![Abrir en Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://menugsbv.streamlit.app/)

---

## ✨ Características Principales

* **📅 Calendario Inteligente**: Genera bloques automáticos por día (Desayuno, Almuerzo, Comida, Merienda y Cena).
* **👥 Gestión de Censo**: Cálculo basado en **Raciones Equivalentes** según la rama (Castores, Lobatos, Rangers, Pioneros y Monitores).
* **🛒 Cesta de la Compra Global**: Sumatorio automático de todos los ingredientes de todos los días, convertido a unidades lógicas (kg, litros, unidades).
* **📄 Exportación PDF**: Genera un informe profesional con el **Planning de Cocina** y la **Lista de la Compra**.
* **📂 Sistema de Plantillas**: Carga menús predefinidos desde Google Sheets para no empezar de cero cada año.
* **🎨 Estilo Scout**: Interfaz personalizada con divisores azules y temática scout.

---

## 🛠️ Instalación y Uso Local

Si deseas ejecutar el proyecto en tu máquina local para desarrollo:

1. **Clonar el repositorio**
   ```bash
   git clone [https://github.com/tu-usuario/MenuGSBV.git](https://github.com/tu-usuario/MenuGSBV.git)
   cd MenuGSBV
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la App**
   ```bash
   streamlit run streamlit_app.py
   ```

---

## 📊 Configuración de la Base de Datos

La aplicación utiliza un **Google Sheet** como base de datos dinámica. Para que funcione, tu documento debe tener las siguientes pestañas:

### 1️⃣ Pestaña: `Ingredientes` (gid=0)
Esta es tu "despensa". Define qué lleva cada plato.
| Plato | Ingrediente | Gramos_Persona | Unidad | Categoria |
| :--- | :--- | :--- | :--- | :--- |
| Macarrones | Pasta | 100 | g | Comida |
| Lentejas | Lenteja seca | 80 | g | Comida |

### 2️⃣ Pestaña: `Plantillas` (Opcional)
Para guardar menús de campamentos históricos.
| Nombre_Plantilla | Dia_Relativo | Momento | Plato |
| :--- | :--- | :--- | :--- |
| Verano 2024 | 1 | Comida | Macarrones |

> **⚠️ IMPORTANTE:** El Google Sheet debe estar compartido como **"Cualquiera con el enlace puede leer"**.

---

## 📦 Dependencias Técnicas

El proyecto se apoya en las siguientes librerías:
- **Streamlit**: Para la interfaz de usuario.
- **Pandas**: Para la lógica de datos y sumatorios.
- **FPDF**: Para la creación de los documentos PDF descargables.

---

## 🤝 Contribuciones

Si tienes ideas para mejorar los cálculos de raciones o añadir nuevas funciones, ¡siéntete libre de abrir un *Pull Request* o una *Issue*!

**Buena Caza y Largas Lunas.** ⚜️  
*Desarrollado para facilitar la vida a los equipos de intendencia.*
