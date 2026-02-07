# Guia de Distribuição - Review App

## Opção 1: Flatpak (Recomendado para GNOME)

### Pré-requisitos
```bash
sudo apt install flatpak flatpak-builder
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
flatpak install flathub org.gnome.Platform//48 org.gnome.Sdk//48
```

### Construir e Instalar Localmente
```bash
cd /home/jobsr/Documents/GitHub/Review
flatpak-builder --user --install --force-clean build-dir com.github.jobsr.Review.json
```

### Executar
```bash
flatpak run com.github.jobsr.Review
```

### Gerar Flatpak para Distribuição
```bash
# Construir
flatpak-builder --repo=repo --force-clean build-dir com.github.jobsr.Review.json

# Criar bundle (arquivo .flatpak)
flatpak build-bundle repo review.flatpak com.github.jobsr.Review

# Agora você pode distribuir o arquivo review.flatpak
```

### Publicar no Flathub
1. Fork do repositório: https://github.com/flathub/flathub
2. Adicione seu manifesto `com.github.jobsr.Review.json`
3. Crie um Pull Request
4. Documentação: https://docs.flathub.org/docs/for-app-authors/submission

---

## Opção 2: Pacote .deb (Debian/Ubuntu)

### Pré-requisitos
```bash
sudo apt install debhelper dh-python python3-all python3-setuptools devscripts
```

### Construir o Pacote
```bash
cd /home/jobsr/Documents/GitHub/Review

# Construir
dpkg-buildpackage -us -uc -b

# O arquivo .deb será criado no diretório pai
cd ..
ls -l review_1.0.0-1_all.deb
```

### Instalar Localmente
```bash
sudo dpkg -i review_1.0.0-1_all.deb
sudo apt-get install -f  # Corrigir dependências se necessário
```

### Distribuir
- Você pode hospedar o arquivo .deb no GitHub Releases
- Ou criar um repositório APT próprio

---

## Opção 3: PyPI (Python Package Index)

### Preparar
```bash
pip install build twine
```

### Construir
```bash
cd /home/jobsr/Documents/GitHub/Review
python3 -m build
```

### Publicar (requer conta no PyPI)
```bash
python3 -m twine upload dist/*
```

### Instalar via pip
```bash
pip install review
```

---

## Opção 4: AppImage

### Pré-requisitos
```bash
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
```

### Criar AppImage
```bash
# Criar estrutura AppDir
mkdir -p Review.AppDir/usr/bin
mkdir -p Review.AppDir/usr/share/applications
mkdir -p Review.AppDir/usr/share/icons/hicolor/scalable/apps

# Copiar arquivos
cp -r review Review.AppDir/usr/bin/
cp main.py Review.AppDir/usr/bin/review
cp com.github.jobsr.Review.desktop Review.AppDir/
cp review/icons/review-app.svg Review.AppDir/usr/share/icons/hicolor/scalable/apps/
cp review/icons/review-app.svg Review.AppDir/review-app.svg

# Criar AppRun
cat > Review.AppDir/AppRun << 'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
export PYTHONPATH="${HERE}/usr/bin:${PYTHONPATH}"
exec python3 "${HERE}/usr/bin/review" "$@"
EOF
chmod +x Review.AppDir/AppRun

# Gerar AppImage
./appimagetool-x86_64.AppImage Review.AppDir Review-1.0.0-x86_64.AppImage
```

---

## Recomendações

### Para Usuários GNOME/Linux Desktop
**Flatpak** é a melhor opção:
- Sandboxing de segurança
- Atualizações automáticas
- Funciona em todas as distribuições
- Fácil de publicar no Flathub

### Para Desenvolvedores Python
**PyPI** é conveniente:
- `pip install review`
- Fácil de atualizar

### Para Distribuições Específicas
**.deb** para Debian/Ubuntu:
- Integração nativa com o sistema
- Gerenciamento de dependências via APT

---

## Checklist Antes de Publicar

- [ ] Atualizar email em `debian/control` e `debian/changelog`
- [ ] Adicionar screenshots ao `com.github.jobsr.Review.metainfo.xml`
- [ ] Criar LICENSE file (GPL-3.0)
- [ ] Testar instalação em sistema limpo
- [ ] Criar GitHub Release com changelog
- [ ] Adicionar badges ao README.md

---

## Recursos Úteis

- Flatpak Docs: https://docs.flatpak.org/
- Flathub Submission: https://docs.flathub.org/docs/for-app-authors/submission
- Debian Packaging: https://www.debian.org/doc/manuals/maint-guide/
- AppImage: https://appimage.org/
- PyPI: https://packaging.python.org/
