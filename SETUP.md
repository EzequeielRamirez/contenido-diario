# Puesta en marcha (una sola vez)

Sistema: 3 reels por día, solos, desde la nube (GitHub Actions). Horarios Argentina: 12:30 · 18:30 · 21:30.
Estructura de cada video: gancho → intro → cuerpo 1 → bucle → cuerpo 2 → bucle → cuerpo 3 → "enlace en la bio".
Guiones en `src/bank_*.py` (22–23 por franja, rotan solos). Voz es-AR-ElenaNeural. Clips de Pexels.

1. **Pexels** (gratis): https://www.pexels.com/api/ → copiá la API key.
2. **Meta** (Instagram + Facebook): la cuenta de Instagram tiene que ser *profesional* y estar vinculada a la página.
   Necesitás `FB_PAGE_ID`, `IG_USER_ID` y un token de página de larga duración con permisos
   `pages_show_list, pages_read_engagement, pages_manage_posts, instagram_basic, instagram_content_publish`.
3. Corré `./setup.sh` y pegá cada valor (no se muestran en pantalla).
4. Probá sin publicar: `gh workflow run "Video diario" -f slot=almuerzo -f dry_run=true` y bajá el video de *Artifacts*.
5. Desde ahí corre solo todos los días.

TikTok: opcional y experimental (las apps sin auditar de TikTok solo pueden subir en privado).
