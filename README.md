# Lab-07-Entra-ID-Sign-in-Logs

## 1. Descripción del proyecto

Después de los últimos incidentes de identidad y control de accesos en Mirador de Montepinar S.L., Antonio Recio ha llegado a una conclusión: no basta con poner puertas, asignar llaves y desconfiar de los vecinos. También hay que averiguar quién intenta entrar, qué ocurre cuando no lo consigue y por qué el sistema permite o bloquea un acceso.

Cuando uno de los vecinos afirma que no puede acceder a una aplicación corporativa, Antonio exige respuestas. ¿Ha escrito mal la contraseña? ¿Ha fallado la autenticación multifactor? ¿Está interviniendo una política de Acceso Condicional? ¿O hay algún problema de configuración de la identidad?

Para evitar que cada incidencia termine en otra discusión interminable en la junta de vecinos, se plantea investigar los registros de inicio de sesión (Sign-in Logs) de Microsoft Entra ID. El objetivo es aprender a interpretar las evidencias disponibles, identificar la causa probable de un fallo de autenticación y documentar un diagnóstico fundamentado en los registros, en lugar de hacer cambios a ciegas.

Este laboratorio continúa el trabajo de los proyectos anteriores de Mirador de Montepinar, pasando de configurar controles de identidad y acceso a investigar qué ocurre cuando un usuario intenta autenticarse y el resultado no es el esperado.

Objetivos técnicos

- Localizar y consultar los registros de inicio de sesión de Microsoft Entra ID.
- Interpretar los resultados de autenticación y los códigos de error disponibles.
- Diferenciar los posibles fallos de credenciales, autenticación multifactor y Acceso Condicional.
- Examinar los detalles de un intento de inicio de sesión para formular y comprobar hipótesis.
- Correlacionar las evidencias disponibles con la identidad, la aplicación y el contexto del acceso.
- Documentar el diagnóstico, las evidencias que lo respaldan y las posibles acciones correctivas.
- Comprender las limitaciones de los registros disponibles según los permisos, las licencias y la configuración del tenant.

## 2. Estructura del proyecto

Antonio Recio quiere saber quién intenta acceder a los sistemas de Montepinar, desde dónde y por qué algunos vecinos no consiguen iniciar sesión. Para investigar estos incidentes, el laboratorio se organiza en cinco bloques: datos, scripts, consultas, informes y evidencias.

### `data/` — Los registros de Montepinar

Almacena muestras anonimizadas de los registros de inicio de sesión (*Sign-in Logs*) obtenidos desde Microsoft Entra ID. Estos datos servirán para realizar pruebas y analizar los eventos sin publicar información sensible del tenant.

### `scripts/` — La investigación de Antonio Recio

Contiene los scripts PowerShell utilizados para conectarse a Microsoft Graph, recuperar los registros de autenticación, filtrar eventos y automatizar su análisis.

### `queries/` — El interrogatorio de Montepinar

Incluye las consultas KQL utilizadas para investigar patrones de autenticación en Azure Log Analytics, como intentos fallidos, resultados de MFA y actividad sospechosa.

### `reports/` — Los informes de la junta

Guarda los resultados del análisis, incluyendo exportaciones CSV e informes en Markdown con los errores detectados, los eventos relevantes y las conclusiones de la investigación.

### `screenshots/` — Las pruebas del delito

Contiene las capturas de pantalla que documentan la configuración del entorno, las consultas realizadas y los resultados obtenidos durante las pruebas.

### Flujo de trabajo

1. Se generan eventos de autenticación en Microsoft Entra ID.
2. Se consultan los Sign-in Logs y se recuperan los registros mediante Microsoft Graph PowerShell.
3. Se procesan los eventos mediante scripts PowerShell y, opcionalmente, consultas KQL.
4. Se documentan los hallazgos y se generan los informes correspondientes.
5. Se recopilan las evidencias para documentar la investigación.

Así, Antonio podrá dejar de sospechar de todos los vecinos por igual y empezar a identificar quién tiene problemas de acceso, quién está introduciendo mal la contraseña y quién merece una investigación más detallada.
