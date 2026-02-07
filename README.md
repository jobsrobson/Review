# Review - Spaced Repetition Study Manager

A modern GNOME application for managing your study schedule using the spaced repetition technique.

## Features

- **Spaced Repetition Scheduling**: Automatic review scheduling at 7, 15, and 30-day intervals
- **Study Timer**: Built-in timer with session tracking and expandable fullscreen mode
- **Calendar Views**: Monthly and weekly calendar views to visualize your study schedule
- **Topic Organization**: Organize topics by areas and tags with custom colors
- **Statistics**: Track total study time for each topic
- **Backup & Restore**: Export and import your study data with optional password encryption
- **Beautiful Interface**: Modern GNOME/Libadwaita design with dark mode support

See [CHANGELOG.md](CHANGELOG.md) for full version history.

## Installation

### From Flatpak (Recommended)

```bash
# Build and install locally
flatpak-builder --user --install --force-clean build-dir com.github.jobsr.Review.json
```

### From Source

```bash
# Install dependencies
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adwaita-1 python3-cryptography

# Run directly
python3 main.py
```

## Building

### Flatpak

```bash
# Install flatpak-builder
sudo apt install flatpak-builder

# Add Flathub repository
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

# Install GNOME SDK
flatpak install flathub org.gnome.Platform//47 org.gnome.Sdk//47

# Build
flatpak-builder --user --install --force-clean build-dir com.github.jobsr.Review.json

# Run
flatpak run com.github.jobsr.Review
```

### Debian Package

See `debian/` directory for packaging files.

## Usage

1. **Add Topics**: Click the "+" button to add study topics
2. **Start Studying**: Click on a topic to start the timer
3. **Track Progress**: View your schedule in the calendar views
4. **Manage**: Organize topics with areas and tags

## License

GPL-3.0-or-later

## Author

Robson Ricardo
