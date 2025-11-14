# Markdown Pro

A professional Markdown editor for macOS, built with Python and Tkinter.

## Features

- Multi-tab editing
- Live preview panel
- Syntax highlighting for Markdown
- File operations (New, Open, Save)
- Quick formatting buttons (Bold, Italic, Code, Link)
- Keyboard shortcuts
- Dark theme interface
- Custom blue icon

## Installation

### Option 1: Run directly
```bash
python3 markdown_editor_pro.py
```

### Option 2: Use as macOS app
1. Copy `Markdown Pro.app` to your `/Applications` folder
2. Double-click to launch
3. You can now keep it in your Dock permanently by right-clicking the Dock icon and selecting "Options > Keep in Dock"

## Keyboard Shortcuts

- `⌘N` - New tab
- `⌘O` - Open file
- `⌘S` - Save file
- `⌘T` - New tab
- `⌘B` - Insert bold formatting
- `⌘I` - Insert italic formatting
- `⌘K` - Insert link

## File Format Support

- `.md` - Markdown files
- `.markdown` - Markdown files
- `.txt` - Text files

## Requirements

- Python 3
- tkinter (included with Python on macOS)
- PIL/Pillow (for icon creation only)

## Icon

The app uses a custom blue icon created from `blue1.png`. The icon has been converted to macOS `.icns` format for proper display in the Dock and Finder.

## Project Structure

```
markdown-pro/
├── markdown_editor_pro.py      # Main application
├── create_markdown_icon.py     # Icon generator script
├── blue1.png                   # Source icon image
├── MarkdownPro.icns           # macOS app icon
├── MarkdownPro.iconset/       # Icon sizes for .icns
├── Markdown Pro.app/          # macOS application bundle
│   └── Contents/
│       ├── Info.plist         # App metadata
│       ├── MacOS/
│       │   └── markdown_pro   # Launcher script
│       └── Resources/
│           └── MarkdownPro.icns
└── README.md                   # This file
```

## How to Add to Dock Permanently

1. Open Finder and navigate to `/Users/hm/markdown-pro/`
2. Drag `Markdown Pro.app` to your Applications folder
3. Open Applications folder and double-click `Markdown Pro.app` to launch
4. Right-click the app icon in the Dock
5. Select "Options > Keep in Dock"
6. The app will now stay in your Dock even after closing

## Comparison to JSON Pro

This editor is based on the structure of JSON Pro but adapted for Markdown:

| Feature | JSON Pro | Markdown Pro |
|---------|----------|--------------|
| File Types | .json | .md, .markdown, .txt |
| Left Panel | JSON Tree View | (can add table of contents) |
| Right Panel | Editor | Editor + Preview |
| Formatting | Format/Minify/Validate | Bold/Italic/Code/Link |
| Syntax Highlighting | JSON | Markdown |

## Future Enhancements

- Export to HTML/PDF
- Table of contents panel
- Find/Replace functionality
- Markdown tables support
- Image preview
- Custom themes
- Spell check
