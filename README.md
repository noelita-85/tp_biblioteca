\#  Sistema de Gestión de Biblioteca (Django CLI)\
\
Un sistema de gestión de biblioteca basado en consola (CLI) desarrollado con \*\*Django\*\* y \*\*Python 3.13\*\*, aplicando una arquitectura en 3 capas (\*3-Tier Architecture\*) y principios de Programación Orientada a Objetos (POO).\
\
\---\
\
\##  Características Principales\
\
\- \*\*Gestión de Libros\*\*: Registro de ejemplares con categorización (\`CategoriaLibro\`), control de stock disponible y filtrado.\
\- \*\*Gestión de Socios\*\*: Control de estados de socios (\`SocioEstado\`) y validaciones de negocio.\
\- \*\*Búsqueda Flexible\*\*: Búsqueda avanzada de libros por título o autor utilizando consultas dinámicas con objetos \`Q\` de Django ORM.\
\- \*\*Sistema de Reservas\*\*: Flujo interactivo de reserva de libros con validación de disponibilidad y actualización automática de stock.\
\- \*\*Manejo de Errores Robustos\*\*: Captura centralizada de \`ValidationError\` y excepciones de integridad de datos (\`IntegrityError\`).\
\- \*\*Optimización de Consultas\*\*: Uso de \`select_related\` para la prevención del problema de rendimiento de N+1 queries.\
\
\---\
\
\##  Arquitectura del Sistema\
\
El proyecto sigue un patrón estructurado en 3 capas bien delimitadas:\
\
1\. \*\*Capa de Modelos (\`models.py\`)\*\*: Define la estructura de datos (\`Socio\`, \`Libro\`, \`Reserva\`) y los enumeradores (\`TextChoices\`).\
2\. \*\*Capa de Servicios (\`services.py\`)\*\*: Encapsula toda la lógica de negocio (validaciones, creación de registros, transacciones).\
3\. \*\*Capa de Presentación / CLI (\`management/commands/biblioteca.py\`)\*\*: Interfaz de comandos interactiva basada en \`BaseCommand\` para la interacción con el usuario.\
\
\---\
\
\##  Requisitos Previos\
\
\- Python 3.10 o superior.\
\- Django 4.2+ / 5.0+.\
\
\---\
\
\##  Instalación y Configuración\
\
1\. \*\*Clonar el repositorio\*\*:\
&#x20;  \`\`\`bash\
&#x20;  git clone [https\://github.com/TU_USUARIO/tp_biblioteca.git]\(https\://github.com/TU_USUARIO/tp_biblioteca.git)\
&#x20;  cd tp_biblioteca