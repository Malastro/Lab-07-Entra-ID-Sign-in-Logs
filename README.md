# Lab-07-Entra-ID-Sign-in-Logs

## 1. Descripción del proyecto

Este laboratorio está inspirado en el capítulo 6 de la primera temporada de *La que se avecina*: **«Un voyeur, una inspección y una tarjeta de crédito»**.

Tras extraviar su cartera en Mirador de Montepinar, Antonio Recio convoca una junta para interrogar a los vecinos y descubrir quién está utilizando su tarjeta de crédito. Javi le advierte que no puede acusar a nadie sin pruebas, pero pronto descubre que Lola ha encontrado la cartera y ha realizado una compra con la tarjeta de su vecino. Berta recomienda cancelar la tarjeta, aunque Antonio se niega porque está obsesionado con desenmascarar al responsable. La situación se complica cuando otros vecinos, conocedores del incidente, también empiezan a utilizarla.

Trasladando esta situación al entorno digital de Mirador de Montepinar S.L., la tarjeta de crédito representa las credenciales de una identidad corporativa. Antonio ha perdido el control de su cuenta y comienzan a producirse distintos intentos de acceso que requieren una investigación.

Nuestra misión será descubrir qué ha sucedido utilizando los registros de inicio de sesión (*Sign-in Logs*) de Microsoft Entra ID. A través de Microsoft Graph PowerShell y herramientas de análisis, investigaremos las autenticaciones, identificaremos comportamientos anómalos y recopilaremos evidencias para reconstruir el incidente.

Al igual que Javi insiste en no acusar a ningún vecino sin pruebas, nuestro objetivo será diferenciar los hechos registrados de las simples sospechas y elaborar un diagnóstico fundamentado en evidencias técnicas.

### Objetivos técnicos

- Localizar y consultar los registros de inicio de sesión de Microsoft Entra ID.
- Interpretar los resultados de autenticación y los códigos de error disponibles.
- Diferenciar los posibles fallos de credenciales, autenticación multifactor y Acceso Condicional.
- Examinar los detalles de los intentos de inicio de sesión para formular y comprobar hipótesis.
- Correlacionar las evidencias disponibles con la identidad, la aplicación, el dispositivo y el contexto del acceso.
- Identificar patrones de autenticación fallida y posibles comportamientos sospechosos.
- Recuperar y exportar registros mediante Microsoft Graph PowerShell.
- Automatizar el filtrado y análisis de eventos utilizando PowerShell.
- Documentar el incidente, las evidencias recopiladas y las posibles acciones correctivas.
- Comprender las limitaciones de los registros disponibles según los permisos, las licencias y la configuración del tenant.

## 2. Estructura del proyecto

Antonio Recio quiere saber quién está utilizando su tarjeta y qué ha ocurrido realmente en Mirador de Montepinar. Para investigar el incidente, el laboratorio se organiza en cinco bloques: datos, scripts, consultas, informes y evidencias.

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

1. Se generan distintos eventos de autenticación en Microsoft Entra ID.
2. Se consultan los Sign-in Logs y se recuperan los registros mediante Microsoft Graph PowerShell.
3. Se procesan los eventos mediante scripts PowerShell y, opcionalmente, consultas KQL.
4. Se documentan los hallazgos y se generan los informes correspondientes.
5. Se recopilan las evidencias para reconstruir el incidente y proponer medidas correctivas.

Así, Antonio podrá dejar de sospechar de todos los vecinos por igual y descubrir qué ha ocurrido realmente con su identidad. Porque en Montepinar se puede acusar a cualquiera, pero en IAM hacen falta evidencias.

## 3. Fases de implementación

### Paso 1. Preparación de la identidad y validación de una autenticación correcta (T01)

El primer paso consiste en preparar la identidad de Antonio Recio y comprobar que puede autenticarse correctamente en Microsoft Entra ID. Esta primera prueba servirá como referencia para comparar los siguientes escenarios de autenticación.

#### 1.1. Preparación y sincronización de la identidad

Se comprueba que la cuenta de Antonio Recio existe en Active Directory, dentro de la siguiente estructura:

```text
OU=Usuarios
└── OU=Montepinar
    └── Antonio Recio
```

Como no se disponía de la contraseña original, se realiza un restablecimiento desde Active Directory Users and Computers.

Posteriormente, se solicita la sincronización del hash de la contraseña mediante Microsoft Entra Connect y PowerShell:

```powershell
Import-Module ADSync

Invoke-ADSyncCSObjectPasswordHashSync `
    -ConnectorName "montepinar.local" `
    -DistinguishedName "CN=Antonio Recio,OU=Usuarios,OU=Montepinar,DC=montepinar,DC=local"
```

La operación finaliza correctamente y permite utilizar la nueva contraseña para autenticarse en Microsoft Entra ID.

#### 1.2. Generación del evento de autenticación

Para generar el primer evento, se inicia sesión con la cuenta de Antonio Recio en Microsoft My Account:

https://myaccount.microsoft.com/

Una vez completada la autenticación, se accede al centro de administración de Microsoft Entra y se consultan los registros desde:

`Entra ID > Monitoring & health > Sign-in logs > User sign-ins (interactive)`

Tras localizar los eventos correspondientes a Antonio, se identifican tres registros:

| Aplicación | Recurso | Resultado |
|---|---|---|
| My Profile | Microsoft Graph | Success |
| My Profile | Microsoft Graph | Success |
| My Sign-ins | Microsoft Graph | Success |

Los tres eventos muestran un resultado satisfactorio y corresponden a operaciones realizadas sobre Microsoft Graph.

#### 1.3. Análisis de los detalles de autenticación

Se selecciona uno de los eventos de My Profile para examinar sus detalles.

En el apartado Authentication Details se obtiene la siguiente información:

| Campo | Resultado |
|---|---|
| Authentication method | Previously satisfied |
| Succeeded | Yes |
| Result detail | MFA requirement satisfied by claim in the token |

El requisito de autenticación multifactor aparece satisfecho mediante una claim incluida en el token. Esto indica que Microsoft Entra ha reconocido una evidencia MFA previamente satisfecha, sin que el registro demuestre que se haya realizado un nuevo desafío MFA durante este evento.

#### 1.4. Comprobación de Acceso Condicional

En el apartado Conditional Access se identifica la siguiente política:

| Campo | Resultado |
|---|---|
| Policy | CA-Montepinar-MFA |
| Grant control | MFA |
| Result | Completed successfully |

La política de Acceso Condicional se ha evaluado correctamente y el requisito de autenticación multifactor se ha satisfecho, permitiendo continuar con el acceso.

#### 1.5. Resultado de la prueba

La prueba T01 finaliza satisfactoriamente. Antonio Recio consigue autenticarse en Microsoft Entra ID y se generan registros que permiten analizar el acceso desde distintas perspectivas.

Esta primera comprobación establece una referencia de comportamiento normal para las siguientes pruebas del laboratorio, en las que se investigarán errores de autenticación y posibles usos no autorizados de la identidad.
