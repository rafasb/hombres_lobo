<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Instrucciones para Copilot en el Proyecto Hombres Lobo
- Se trata de una aplicación web SPA (Single Page Application), que debe estar orientada a móviles.
- El backend está desarrollado en Python con FastAPI. 
- El backend también incluye un sistema de autenticación y autorización, que se gestiona a través de un token JWT (JSON Web Token).
- El backend, además, incluye un sistema de notificaciones en tiempo real utilizando WebSockets.
- El backend reside en el directorio `../backend/` y el frontend en `../frontend/`. El primero es el directorio de trabajo principal.
- Manten los ficheros con el tamaño mínimo, separando las funcionalidades en componentes pequeños y reutilizable.
- Sigue las buenas prácticas de desarrollo de software, incluyendo la separación de preocupaciones y la reutilización de componentes.
- Siempre que introduzcas cambios en un fichero, analiza las dependencias y consecuencias para determinar si es necesario actualizar o refactorizar los otros ficheros relacionados.
- En el directorio `../doc/`, encontrarás información sobre el proyecto, su estructura y detalles de implementación.
- Sugiere siempre el siguiente paso a seguir, pero que sea de un alcance razonable, no un paso completo del proyecto. No te embarques en pasos con demasiadas tareas sin preguntar antes.

## 📊 Proyecto Hombres Lobo

# Descripción del juego

## Roles y Funciones en la App (El Narrador Digital)

El número de roles se ajustará automáticamente según el total de jugadores. La app te recomendará el número óptimo de Hombres Lobo para una partida equilibrada (generalmente, al menos un Hombre Lobo por cada 3-4 Aldeanos).

### Roles de los Aldeanos (Bando del Pueblo)

- **Aldeano/a:** No tiene habilidades especiales. Tu objetivo es usar tu lógica y persuasión en el chat de grupo para identificar a los Hombres Lobo y convencer al pueblo de lincharlos.
- **Vidente:** Cada "noche", la app te permitirá seleccionar a un jugador para conocer su verdadera identidad (Aldeano, Hombre Lobo o un rol especial). La información que recibas de El Narrador Digital es crucial, pero ¡decide con astucia cuándo y cómo revelarla en el chat de día sin ser descubierto por los Hombres Lobo!
- **Alguacil:** Elegido por votación popular al inicio de la partida. Tu voto cuenta doble y la app te consultará en caso de empate durante un linchamiento. Si mueres, la app te pedirá que elijas a tu sucesor antes de tu eliminación.
- **Cazador/a:** Si eres eliminado (por linchamiento o por los Hombres Lobo), la app te preguntará a quién deseas llevarte contigo. Ese jugador también será eliminado de la partida.
- **Bruja:** Tienes dos pociones de un solo uso que la app te permitirá activar: una de curación para salvar a la víctima de los Hombres Lobo y una de veneno para eliminar a cualquier jugador durante la "noche". Puedes usar ambas en la misma noche o en noches separadas.
- **El Niño Salvaje:** Comienzas como un Aldeano. En la primera "noche", la app te pedirá que escojas a un jugador como tu modelo a seguir. Si tu modelo muere, la app te informará que te has convertido en un Hombre Lobo, y notificará a los demás Hombres Lobo en su siguiente turno nocturno. Si tu modelo es el último Hombre Lobo eliminado, ¡ganas con los Aldeanos!
- **Cupido:** En la primera "noche", la app te permitirá elegir a dos jugadores para que se "enamoren". La app les les avisará en secreto informándoles de su conexión.
  - **Condición de Enamorados:** Si uno de los enamorados muere (por cualquier causa), la app anunciará que el otro muere inmediatamente de pena.
  - **Condición de Victoria:** Si los dos enamorados son de bandos opuestos (ej. un Aldeano y un Hombre Lobo), su condición de victoria cambia: ganan si solo ellos dos quedan vivos al final, independientemente de sus roles originales. Si son del mismo bando, su objetivo de victoria sigue siendo el de su bando.

### Roles de los Hombres Lobo (Manada de los Hombres Lobo)

- **Hombre Lobo:** Cada "noche", la app te permitirá, junto con los otros Hombres Lobo (cuyas identidades te serán reveladas por la app), seleccionar a un Aldeano para devorar. Durante el "día", debes actuar como un Aldeano inocente en alas interacciones con los demás meimbros de la partida, engañar y desviar sospechas para evitar ser linchado. Ganan si acaban con todos los Aldeanos.

---

## Preparación y Reparto de Roles con la App

El Narrador Digital (la app) se encargará de todo el proceso:

1. **Creación de Partida:** Un jugador crea la partida en la app y comparte un código con los demás.
2. **Unión de Jugadores:** Los demás jugadores se unen a la partida usando el código.
3. **Asignación de Roles:** Una vez que todos están en la partida, la app asigna roles de forma aleatoria y secreta. Cada jugador recibirá un aviso de forma privada en la app con su rol, su objetivo y cualquier habilidad especial. Los Hombres Lobo serán notificados de la identidad de sus compañeros en la primera fase de "noche" a través de un aviso privado en la app. Se asigna un hombre lobo cada 3 ciudadanos. 

---

## Rondas del Juego

### 1. Fase de Noche (Interacciones Secretas con la App)

Todos los Aldeanos están "durmiendo" virtualmente. La app permitirá que cada jugador, en secreto, pueda comunicar su voto y sus interacciones específicas asociadas al rol asignado. No hay un orden visible.

Durante esta fase, la app te permitirá:

- **Voto de Linchamiento:** Todos los jugadores, si son Aldeanos, podrán votar en secreto por un jugador para lincharlo.
- **Cupido (Solo Primera Noche):** La app te pedirá que elijas a dos jugadores para enamorar. Una vez elegidos, la app notificará a los enamorados en su próxima interacción secreta para informarles de su conexión.
- **El Niño Salvaje (Solo Primera Noche):** La app te pedirá que elijas a tu jugador modelo. Te advertirá de tu transformación si tu modelo muere.
- **Vidente:** La app te preguntará qué jugador deseas investigar. Una vez elegido, la app te revelará el rol de esa persona de forma privada.
- **Bruja:** La app te informará si alguien fue atacado por los Hombres Lobo y te preguntará si deseas usar tu poción de curación. Luego, te preguntará si deseas usar tu poción de veneno y sobre quién.
- **Hombres Lobo (Se omite en la primera ronda):** La app permitirá una votación solo para los Hombres Lobo, donde deberán llegar a un consenso sobre a qué jugador devorar. Si no hay consenso en el tiempo establecido, la app registrará que no hubo devorado. La app también les comunicará si el Niño Salvaje se ha convertido en Hombre Lobo y cuál es el nuevo miembro de la manada.

Estas interacciones dentro de la app permiten a los roles de apoyo, como la Vidente, compartir información crucial sin ser directamente expuestos en el debate general. El Narrador Digital es el único que conoce la información completa de todos los roles.

### 2. Fase de Despertar (Anuncio de Víctimas por la App)

Una vez que todas las acciones nocturnas han sido procesadas por El Narrador Digital, la app anunciará los resultados en el chat general de la partida:

- **Linchamiento:** La app mostrará el resultado de los votos y anunciará al jugador con más votos que será linchado. En caso de empate, la app consultará al Alguacil para que decida. La app revelará el rol del jugador linchado y lo eliminará de la partida.
- **Ataque de los Hombres Lobo:** La app anunciará quién ha sido devorado y revelará su rol. Los roles de los salvados por la Bruja no se revelan.
- **Muerte de Enamorados:** Si uno de los enamorados ha muerto, la app anunciará que el otro enamorado también ha fallecido de pena en ese momento, y revelará su rol.
- **Cazador:** Si el Cazador ha sido eliminado, la app le enviará una notificación privada para que elija a quién llevarse consigo. Una vez elegido, la app anunciará la muerte de ambos.
- **Transformación del Niño Salvaje:** Si el modelo del Niño Salvaje murió, la app le avisará de forma privada para informarle que se ha convertido en Hombre Lobo (esto se comunicará a los Hombres Lobo en su próxima fase de noche).

### 3. Fase de Día (Debate en el Chat)

Esta es la fase de interacción y deducción abierta, con componentes secretos manejados por la app. La duración de esta fase será configurable por el anfitrión de la partida.

- **El debate:** Todos los jugadores pueden comunicarse libremente. La app establecerá una limitación temporal para esta fase. Se recomendará a los jugadores pueden iniciar conversaciones privadas (entre 2-3 jugadores, etc.). Esto permite compartir información (verdadera o falsa), formar alianzas, hacer acusaciones o defenderse sin la supervisión directa de la app (más allá de las reglas del juego).
- **Votación de Linchamiento:** Al final de la fase de día, la app abrirá una votación pública para linchar a un jugador. Esta fase también estará limitada temporalmente.

El objetivo durante el día es identificar a los Hombres Lobo y decidir a quién linchar. Los Hombres Lobo deben sembrar la duda y desviar las acusaciones.

---

## Fin de la Partida

La app declarará el fin del juego cuando se cumpla una de las siguientes condiciones:

- **Los Hombres Lobo ganan:** Si todos los Aldeanos han sido devorados.
- **Los Aldeanos ganan:** Si todos los Hombres Lobo han sido linchados (y los enamorados no son la única pareja viva de bandos opuestos).
- **Los Enamorados ganan:** Si los dos enamorados son los únicos jugadores que quedan vivos, y sus roles originales eran de bandos opuestos.

---

## Resumen de la Partida con la App

- **Explicación del Juego:** La app proporcionará una guía completa de las reglas y roles.
- **Reparto de Roles en Secreto:** El Narrador Digital asigna y comunica los roles de forma privada.
- **RONDAS:**
  - **Fase de Noche:** Interacciones secretas con la app (acciones de roles especiales).
  - **Fase de Despertar:** El Narrador Digital anuncia las víctimas y eventos de la noche en el chat general.
  - **Fase de Día:** Debate en el chat general y chats privados, seguido de una votación de linchamiento.
- **Fin de la Partida:** La app declara el ganador según las condiciones de victoria.

## 📦 Stack Tecnológico del Backend

### Framework y Servidor
- **FastAPI**: Framework web moderno y rápido para construir APIs con Python
- **Uvicorn**: Servidor ASGI de alto rendimiento para Python
- **CORS**: Soporte para Cross-Origin Resource Sharing integrado

### Modelos y Validación
- **Pydantic**: Validación de datos y serialización
- **Email-validator**: Validación de direcciones de correo electrónico

### Autenticación y Seguridad
- **PassLib[bcrypt]**: Gestión de hashing de contraseñas con soporte para bcrypt
- **Python-jose**: Implementación de JWT (JSON Web Tokens) para autenticación
- **Python-multipart**: Soporte para formularios y subida de archivos

### Persistencia de Datos
- Sistema de almacenamiento basado en archivos JSON
- Estructura modular de datos en directorio `db_json/`

### Testing
- **Pytest**: Framework de testing
- **HTTPX**: Cliente HTTP para pruebas de integración

### Configuración
- **Python-dotenv**: Gestión de variables de entorno
- Configuración modular en directorio `core/`

### Arquitectura y Estructura
- Organización modular del código:
  - `api/`: Rutas y endpoints de la API
  - `core/`: Configuración central y dependencias
  - `models/`: Definición de modelos de datos
  - `services/`: Lógica de negocio
  - `websocket/`: Gestión de conexiones WebSocket y eventos en tiempo real

### Características Principales
- API RESTful
- Documentación OpenAPI/Swagger automática
- WebSockets para comunicación en tiempo real
- Sistema de roles y permisos
- Gestión de estado del juego
- Sistemas de votación y acciones de jugadores