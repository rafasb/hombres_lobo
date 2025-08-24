<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Instucciones generales:
- Utiliza los principios de desarrollo SOLID.
- Ejecuta las instrucciones paso a paso.
- Antes de realizar cualquier cambio, analiza el contexto y las dependencias.
- Revisa los cambios realizados para avitar errores o inconsistencias.
- Ejecuta los tests si los hay.
- Propon mejoras seguientes.

# Instrucciones para las comunicaciones frontend-backend:

El principal objetivo es simplificar el proceso de comunicación, así como los mensajes e interacciones, manteniendo la funcionalidad de la aplicación.

Dado que existe una API con endpoints para la gestión de toda la información del juego, y que el flujo de la partida se gestiona en el backend, el frontend enviará la información mediante llamadas a la API, para actualizar la información de la base de datos del backend y activar los cambios de flujo de la partida, si es el caso.

Para permitir la interactividad entre los miembros de cada partida, será el backend el responsable de enviar mensajes a través del websocket a todos los miembros de una misma partida, cuando alguno de los datos asociados a los miembros de la partida o asociados a la partida hayan sido modificados.

El frontend, al recibir los mensajes del backend con las actualizaciones de los datos de la partida y sus participantes, almacenará esta información en local (usando Pinia).

Las modificaciones en los datos de pínia se realizarán mediante los stores siguientes Auth, (ya existente), User (para los datos de usuario: id, username, estado: connected, in_game, disconnected), Player (para la información del usuario relacionada con el juego, como el rol, vivo/muerto, etc).

Las modificaciones de datos en Pinia permitirán que los datos mostrados en los componentes VUE sean reactivos, actualizandose cuando se modifiquen en el store.

## Instrucciones para Copilot en el Proyecto Hombres Lobo

- Se trata de una aplicación web SPA (Single Page Application), que debe estar orientada a móviles, salvo vistas especialmente anchas como la de administración. Asegura la característica SPA y respetar el diseño responsivo.

- El backend reside en el directorio `backend/` y el frontend en `frontend/`. 

- En el directorio superior al directorio `Docs/`, encontrarás el directorio que contiene información sobre el proyecto, su estructura y detalles de implementación.
- Dispones de la documentación del backend en el fichero `./openapi.json`. Consulta el fichero cuando necesites información sobre las rutas y los datos que maneja el backend.


- El proyecto utiliza **Bootstrap 5** como framework de UI. Al crear nuevas vistas o funcionalidades, usa las clases de Bootstrap para styling y componentes. Evita crear CSS personalizado a menos que sea estrictamente necesario para funcionalidades específicas no cubiertas por Bootstrap.

- Estructura de componentes actualizada: separa la vista pura con el template en el directorio `src/views` (usando clases Bootstrap), la lógica de negocio reutilizable en un fichero separado en el directorio `src/composables`, el wrapper simplificado que une ambos en `src/components/`. Los estilos CSS personalizados deben ser mínimos y solo cuando Bootstrap no cubra la funcionalidad.

- **Convenciones de Bootstrap:** Utiliza el sistema de grid de Bootstrap, las clases de utilidad, componentes como cards, buttons, forms, modals, etc. Mantén la consistencia visual usando las variables CSS personalizadas definidas en `src/style.css`.

- **Diseño móvil:** Asegúrate de usar las clases responsive de Bootstrap (col-*, d-*, etc.) y mantener el contenedor `.mobile-container` para simular el aspecto de aplicación móvil en desktop.
- Recuerda utilizar Pinia para la gestión del estado de la aplicación y Vue Router para la navegación entre vistas.

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
