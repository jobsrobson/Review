# Guia Rápido - Como Distribuir o Review App

## ✅ Passos Completados

1. ✅ flatpak-builder instalado
2. ✅ Repositório Flathub adicionado
3. ⏳ GNOME Platform/SDK 48 sendo baixado (aguarde finalizar)

## 📦 Próximos Passos

### Depois que o download terminar:

#### 1. Construir o Flatpak
```bash
cd /home/jobsr/Documents/GitHub/Review
flatpak-builder --user --install --force-clean build-dir com.github.jobsr.Review.json
```

#### 2. Testar o App
```bash
flatpak run com.github.jobsr.Review
```

#### 3. Gerar arquivo .flatpak para distribuição
```bash
# Criar repositório
flatpak-builder --repo=repo --force-clean build-dir com.github.jobsr.Review.json

# Criar bundle (arquivo único para distribuir)
flatpak build-bundle repo review.flatpak com.github.jobsr.Review
```

Agora você terá um arquivo `review.flatpak` que pode distribuir!

---

## 🎯 Alternativa Mais Simples: Pacote .deb

Se preferir criar um .deb (mais simples, mas só funciona em Debian/Ubuntu):

```bash
cd /home/jobsr/Documents/GitHub/Review

# Instalar ferramentas
sudo apt install debhelper dh-python devscripts

# Construir
dpkg-buildpackage -us -uc -b

# O arquivo .deb estará em:
cd ..
ls review_1.0.0-1_all.deb
```

---

## 📤 Como Distribuir

### GitHub Releases (Recomendado)
1. Vá para https://github.com/jobsr/Review/releases
2. Clique em "Create a new release"
3. Faça upload do arquivo `review.flatpak` ou `review_1.0.0-1_all.deb`
4. Adicione notas de lançamento

### Flathub (Loja Oficial)
1. Fork: https://github.com/flathub/flathub
2. Adicione seu manifesto
3. Crie Pull Request
4. Documentação: https://docs.flathub.org/

---

## ⚠️ Antes de Publicar

- [ ] Adicionar seu email em `debian/control` e `debian/changelog`
- [ ] Tirar screenshots e adicionar ao `com.github.jobsr.Review.metainfo.xml`
- [ ] Criar arquivo LICENSE (GPL-3.0)
- [ ] Testar em sistema limpo
- [ ] Atualizar README.md com instruções de instalação

---

## 🆘 Problemas Comuns

**Erro: "No remote refs found"**
```bash
sudo flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
```

**Erro: "command not found: flatpak-builder"**
```bash
sudo apt install flatpak flatpak-builder
```

**Erro ao construir .deb**
```bash
sudo apt install debhelper dh-python python3-all devscripts
```
