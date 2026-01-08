# 🔑 Cómo Obtener tus Binance API Keys

## ⚠️ Importante Antes de Empezar

- **Solo lectura**: Para este proyecto (consultar precios), NO necesitas permisos de trading
- **Nunca compartas** tus API keys con nadie
- **No las subas** a repositorios públicos (ya están en `.gitignore`)
- **Usa restricciones**: IP whitelist y permisos mínimos

---

## 📋 Paso a Paso

### 1. Crear una Cuenta en Binance (si no tienes)

1. Ve a [Binance.com](https://www.binance.com)
2. Haz clic en **"Register"** (Registrarse)
3. Completa el registro con email y contraseña
4. Verifica tu email
5. Completa la verificación KYC (Know Your Customer) si es necesario

---

### 2. Acceder a la Sección de API Management

1. **Inicia sesión** en tu cuenta de Binance
2. En la esquina superior derecha, haz clic en tu **icono de perfil**
3. Selecciona **"API Management"** del menú desplegable

   ![API Management Location](https://public.bnbstatic.com/image/cms/article/body/202203/0e8a4b8c4b4e4d3e8b5e8b5e8b5e8b5e.png)

   **Ruta directa**: https://www.binance.com/en/my/settings/api-management

---

### 3. Crear una Nueva API Key

1. En la página de API Management, haz clic en **"Create API"**
2. Elige el tipo:
   - **System generated** (Recomendado para principiantes)
   - API key generada por el sistema

3. Dale un nombre a tu API key:
   ```
   Ejemplo: "Trading Engine - Read Only"
   ```

4. **Verificación de seguridad**:
   - Binance te pedirá verificación 2FA (Google Authenticator, SMS, o Email)
   - Completa la verificación

---

### 4. Configurar Permisos (MUY IMPORTANTE)

Después de crear la API key, verás opciones de permisos. **Para este proyecto solo necesitas**:

✅ **Enable Reading** (Habilitar Lectura)
- Permite consultar datos de mercado
- Ver balances (si quieres monitorear tu cuenta)

❌ **Disable Trading** (Deshabilitar Trading)
- NO marques esta opción
- No es necesario para consultar precios

❌ **Disable Withdrawals** (Deshabilitar Retiros)
- NUNCA habilites esto en producción
- Mantén esto deshabilitado

**Configuración recomendada para este proyecto:**
```
✅ Enable Reading
❌ Enable Spot & Margin Trading
❌ Enable Futures
❌ Enable Withdrawals
```

---

### 5. Restricción de IP (OPCIONAL pero RECOMENDADO)

Para mayor seguridad, restringe el acceso solo desde tu IP:

1. En la sección **"API restrictions"**
2. Selecciona **"Restrict access to trusted IPs only"**
3. Agrega tu IP actual:
   - Para obtener tu IP: https://whatismyipaddress.com/
   - Si usas servidor: agrega la IP del servidor
   - Si usas local: agrega tu IP local

**Ejemplo:**
```
192.168.1.100 (tu IP local)
```

**Nota**: Si tu IP cambia frecuentemente, puedes dejar esto sin restricción para desarrollo, pero **NUNCA en producción**.

---

### 6. Copiar tus API Keys

Después de crear la API key, Binance te mostrará:

1. **API Key** (pública)
   ```
   Ejemplo: mVtxA8RzQk7h3W9pN5vL2mK8jF4dS6aT1bC0eR9yU3xI7oP2qM5
   ```

2. **Secret Key** (privada) - **¡SOLO SE MUESTRA UNA VEZ!**
   ```
   Ejemplo: xY2zW5vU8tS1rQ4pN7mK0jH3gF6dC9bA2eR5yT8iO1uP4qM7
   ```

⚠️ **IMPORTANTE**: 
- La **Secret Key** solo se muestra UNA VEZ
- Cópiala inmediatamente y guárdala en lugar seguro
- Si la pierdes, deberás eliminar la API key y crear una nueva

---

### 7. Agregar las Keys a tu Proyecto

1. Abre el archivo `.env` en tu proyecto:
   ```bash
   nano /home/integral/DevUser/trading_engine/.env
   ```

2. Reemplaza las líneas:
   ```bash
   BINANCE_API_KEY=tu_api_key
   BINANCE_API_SECRET=tu_api_secret
   ```

   Por tus keys reales:
   ```bash
   BINANCE_API_KEY=mVtxA8RzQk7h3W9pN5vL2mK8jF4dS6aT1bC0eR9yU3xI7oP2qM5
   BINANCE_API_SECRET=xY2zW5vU8tS1rQ4pN7mK0jH3gF6dC9bA2eR5yT8iO1uP4qM7
   ```

3. Guarda el archivo

---

## 🔒 Seguridad - Checklist

Antes de usar tus API keys en producción, verifica:

- [ ] ✅ Solo permisos de **lectura** habilitados
- [ ] ✅ Trading y Withdrawals **DESHABILITADOS**
- [ ] ✅ Restricción de IP configurada (si es posible)
- [ ] ✅ API key con nombre descriptivo
- [ ] ✅ 2FA habilitado en tu cuenta de Binance
- [ ] ✅ `.env` en `.gitignore` (no subir a GitHub)
- [ ] ✅ Secret Key guardada en lugar seguro (password manager)

---

## 🚀 Probar tu Configuración

Una vez configuradas las keys, prueba que funcionan:

```bash
# Levantar el proyecto
docker compose up

# En otra terminal, probar endpoint
curl http://localhost/api/signals/latest
```

Si las keys funcionan, deberías ver datos de mercado sin errores.

---

## ❓ Troubleshooting

### Error: "Invalid API-key, IP, or permissions for action"
**Solución**: 
- Verifica que copiaste correctamente ambas keys
- Revisa los permisos (debe tener "Enable Reading")
- Si configuraste restricción de IP, verifica que sea la correcta

### Error: "Signature for this request is not valid"
**Solución**:
- La Secret Key es incorrecta
- Verifica que no tenga espacios al inicio o final
- Recrea la API key si es necesario

### La Secret Key no aparece
**Solución**:
- Solo se muestra una vez al crear
- Elimina la API key actual y crea una nueva

---

## 📚 Recursos Adicionales

- [Binance API Documentation](https://binance-docs.github.io/apidocs/spot/en/)
- [Binance API Management Guide](https://www.binance.com/en/support/faq/how-to-create-api-360002502072)
- [Security Best Practices](https://www.binance.com/en/support/faq/how-to-keep-your-account-secure-360002937492)

---

## 🔄 Rotar tus API Keys (Recomendado cada 3-6 meses)

1. Crea una nueva API key siguiendo los pasos anteriores
2. Actualiza el `.env` con las nuevas keys
3. Reinicia el proyecto: `docker compose restart`
4. Elimina la API key antigua desde Binance

---

## ⚠️ Nota para Producción

**Para este proyecto (solo consultar precios):**
- Las API keys son **opcionales**
- Binance permite consultar precios públicos sin autenticación
- Solo necesitas las keys si quieres:
  - Ver tu balance
  - Ejecutar órdenes en el futuro
  - Acceder a endpoints privados

**Puedes dejarlo como está** (`tu_api_key` / `tu_api_secret`) si solo quieres probar el sistema de alertas sin ejecutar trades reales.
