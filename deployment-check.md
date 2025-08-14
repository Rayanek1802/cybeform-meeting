# Checklist de vérification du déploiement

## ✅ Tests à effectuer

### 1. Accessibilité
- [ ] L'URL Render charge correctement
- [ ] Pas d'erreurs 404 ou 500
- [ ] Temps de chargement acceptable (<5s)

### 2. Interface utilisateur
- [ ] Page d'accueil s'affiche correctement
- [ ] Navigation fonctionne
- [ ] Formulaires sont interactifs
- [ ] Styles CSS appliqués correctement

### 3. Fonctionnalités métier
- [ ] Création de réunion fonctionne
- [ ] Rejoindre une réunion fonctionne
- [ ] Chat en temps réel opérationnel
- [ ] Partage d'écran disponible

### 4. Performance
- [ ] Application responsive sur mobile
- [ ] Pas d'erreurs console
- [ ] WebRTC fonctionne correctement

### 5. Monitoring
- [ ] Logs Render sans erreurs critiques
- [ ] Métriques de performance acceptables
- [ ] Uptime stable

## 🔧 En cas de problème

### Erreurs communes et solutions :
1. **Build failed** : Vérifier les dépendances et la configuration Docker
2. **404 sur les routes** : Configurer le fallback pour SPA
3. **WebRTC ne fonctionne pas** : Vérifier les certificats HTTPS
4. **Lenteur** : Optimiser le bundle ou upgrader l'instance

### Commandes de debug :
```bash
# Vérifier les logs en local
docker logs <container-id>

# Tester la connectivité
curl -I https://votre-app.onrender.com

# Vérifier les headers de sécurité
curl -I https://votre-app.onrender.com | grep -i security
```