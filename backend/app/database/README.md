app/database/
├── __init__.py          # Exporta todas las funciones (compatibilidad)
├── session.py          # Configuración BD (engine, SessionLocal, Base)
├── models.py           # Modelos SQLAlchemy (UserDB, GameDB)
├── conversions.py      # Funciones de conversión (separadas pero no usadas)
├── utils.py            # Operaciones CRUD y funciones helper
└── initialization.py   # Inicialización y migración de BD