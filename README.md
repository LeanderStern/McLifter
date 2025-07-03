## Overview

McLifter is designed to help Minecraft server administrators and players manage their mod collections by automatically updating mods to compatible versions. It currently only focuses on Fabric mods and integrates with the Modrinth mod repository.

## Features

- **Easy Setup**: No API key required just install the packages and run `main.py` or download the executable
- **Automatic Mod Updates**: Automatically finds and downloads compatible mod versions for new Minecraft releases
- **Fabric Mod Support**: Specialized handling of Fabric mods with `fabric.mod.json` metadata
- **Backup System**: Creates backups of your existing mods before making changes
- **Optional Force Updates**: Modifies the mod to support the provided version and tracks which mods have been force-updated to prevent issues
- **Hash Verification**: Verifies downloaded files using hashes
- **Interactive Fallbacks**: Prompts for manual input when mod IDs are invalid

## Installation Pip

```bash
git clone https://github.com/LeanderStern/McLifter.git
cd McLifter
pip install -r requirements.txt
```

## Installation Conda

```bash
git clone https://github.com/LeanderStern/McLifter.git
cd McLifter
conda env create -f environment.yml
```

## Core Components

### API Service
- **Modrinth Integration**: Fetches mod information and download links from Modrinth
- **Version Selection**: Automatically selects the most stable version based on release type and semantic versioning
- **Retry Logic**: Built-in retry mechanisms for network reliability

### File Manager
- **Fabric File Manager**: Handles Fabric mod metadata and file operations
- **Backup Management**: Creates and restores backups of mod folders
- **Metadata Modification**: Updates mod to provided version and flags as force-updated

### Type Safety
- **Pydantic Models**: Strong typing with validation for all data structures
- **Custom Constraints**: Specialized types for Base62 strings, semantic versions, file paths, and JAR files

## Workflow

1. Scanning your existing mod folders (client and/or server)
2. Reading mod metadata from `fabric.mod.json` files
3. Querying Modrinth for compatible versions
4. Creating backups of current mods
5. Downloading and installing updated versions
6. Optional force update if there is no matching version available

## Configuration

McLifter supports:
- Client-side mod management
- Server-side mod management (optional)
- Minecraft version targeting

## Backup System

McLifter automatically creates backups before making changes:
- Client mods backed up to dedicated backup directory
- Server mods backed up separately (if server update is enabled)
- Full restoration capability if updates cause issues or an exception occures

## Error Handling

- Hash verification for downloaded files
- Comprehensive validation of mod metadata
- Graceful handling of missing dependencies

## Requirements

- Python 3.7+
- Internet connection for Modrinth API access
- Fabric mod environment

## Contributing

This project uses type hints and Pydantic for data validation. Please ensure all contributions maintain the existing code quality standards.
