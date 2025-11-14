#!/usr/bin/env python3
"""
Markdown Pro - Professional Markdown Editor for macOS
Features: Multi-tab editing, live preview, syntax highlighting
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from datetime import datetime
import re

# Settings file for persistent last folder
SETTINGS_FILE = os.path.expanduser("~/.markdown_editor_pro.json")

def load_settings():
    """Load settings from file"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_settings(settings):
    """Save settings to file"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)
    except:
        pass

def markdown_to_html(markdown_text):
    """Convert markdown to HTML for preview"""
    html = markdown_text

    # Headers
    html = re.sub(r'^######\s+(.+)$', r'<h6>\1</h6>', html, flags=re.MULTILINE)
    html = re.sub(r'^#####\s+(.+)$', r'<h5>\1</h5>', html, flags=re.MULTILINE)
    html = re.sub(r'^####\s+(.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'^###\s+(.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^##\s+(.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^#\s+(.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # Bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'__(.+?)__', r'<strong>\1</strong>', html)

    # Italic
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    html = re.sub(r'_(.+?)_', r'<em>\1</em>', html)

    # Code inline
    html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)

    # Code blocks
    html = re.sub(r'```(.+?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)

    # Links
    html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)

    # Images
    html = re.sub(r'!\[(.+?)\]\((.+?)\)', r'<img src="\2" alt="\1" style="max-width: 100%;">', html)

    # Lists (unordered)
    html = re.sub(r'^\*\s+(.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'^\-\s+(.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)

    # Lists (ordered)
    html = re.sub(r'^\d+\.\s+(.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)

    # Wrap consecutive <li> tags in <ul>
    html = re.sub(r'(<li>.*?</li>(\n<li>.*?</li>)*)', r'<ul>\1</ul>', html, flags=re.DOTALL)

    # Blockquotes
    html = re.sub(r'^>\s+(.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)

    # Line breaks
    html = html.replace('\n\n', '<br><br>')

    # Wrap in basic HTML with styles
    full_html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
                line-height: 1.6;
                padding: 20px;
                background-color: #1e1e1e;
                color: #d4d4d4;
            }}
            h1, h2, h3, h4, h5, h6 {{
                margin-top: 24px;
                margin-bottom: 16px;
                font-weight: 600;
                line-height: 1.25;
                color: #89b4fa;
            }}
            h1 {{ font-size: 2em; border-bottom: 1px solid #404040; padding-bottom: 10px; }}
            h2 {{ font-size: 1.5em; border-bottom: 1px solid #404040; padding-bottom: 8px; }}
            h3 {{ font-size: 1.25em; }}
            code {{
                background-color: #2b2b2b;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
                font-size: 0.9em;
                color: #f38ba8;
            }}
            pre {{
                background-color: #2b2b2b;
                padding: 16px;
                border-radius: 6px;
                overflow-x: auto;
            }}
            pre code {{
                background-color: transparent;
                padding: 0;
                color: #d4d4d4;
            }}
            blockquote {{
                border-left: 4px solid #89b4fa;
                padding-left: 16px;
                margin-left: 0;
                color: #a6adc8;
            }}
            a {{
                color: #89b4fa;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            ul, ol {{
                padding-left: 2em;
            }}
            li {{
                margin: 4px 0;
            }}
            strong {{
                color: #fab387;
            }}
            em {{
                color: #94e2d5;
            }}
            img {{
                max-width: 100%;
                height: auto;
            }}
        </style>
    </head>
    <body>
        {html}
    </body>
    </html>
    """

    return full_html


class MarkdownTab:
    """Individual Markdown editing tab"""

    def __init__(self, parent, tab_id, on_content_changed=None):
        self.parent = parent
        self.tab_id = tab_id
        self.on_content_changed = on_content_changed
        self.file_path = None
        self.modified = False

        # Create main container
        self.container = tk.Frame(parent, bg='#2b2b2b')

        # File info bar
        info_bar = tk.Frame(self.container, bg='#2b2b2b')
        info_bar.pack(fill='x', padx=5, pady=(5, 2))

        self.file_label = tk.Label(info_bar, text="Untitled", bg='#2b2b2b',
                                   fg='#808080', font=('Arial', 9))
        self.file_label.pack(side='left')

        self.position_label = tk.Label(info_bar, text="Line 1, Col 1",
                                       bg='#2b2b2b', fg='#808080', font=('Arial', 9))
        self.position_label.pack(side='right')

        # Text editor with frame
        editor_frame = tk.Frame(self.container, bg='#2b2b2b', bd=1)
        editor_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.text = tk.Text(editor_frame,
                           bg='#1e1e1e',
                           fg='#d4d4d4',
                           insertbackground='white',
                           font=('Menlo', 13),
                           wrap='word',
                           bd=0,
                           highlightthickness=0)

        # Scrollbars
        vsb = ttk.Scrollbar(editor_frame, orient="vertical", command=self.text.yview)
        hsb = ttk.Scrollbar(editor_frame, orient="horizontal", command=self.text.xview)

        self.text.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        editor_frame.grid_rowconfigure(0, weight=1)
        editor_frame.grid_columnconfigure(0, weight=1)

        self.text.config(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Bind events
        self.text.bind('<KeyRelease>', self.update_position)
        self.text.bind('<ButtonRelease>', self.update_position)
        self.text.bind('<<Modified>>', self.on_text_modified)
        self.text.bind("<Command-s>", lambda e: self.on_save_request())

        # Setup syntax highlighting
        self.setup_syntax_highlighting()

    def setup_syntax_highlighting(self):
        """Setup Markdown syntax highlighting"""
        # Configure tags
        self.text.tag_config('h1', foreground='#89b4fa', font=('Menlo', 18, 'bold'))
        self.text.tag_config('h2', foreground='#89b4fa', font=('Menlo', 16, 'bold'))
        self.text.tag_config('h3', foreground='#89b4fa', font=('Menlo', 14, 'bold'))
        self.text.tag_config('h4', foreground='#89b4fa', font=('Menlo', 13, 'bold'))
        self.text.tag_config('h5', foreground='#89b4fa', font=('Menlo', 13, 'bold'))
        self.text.tag_config('h6', foreground='#89b4fa', font=('Menlo', 13, 'bold'))
        self.text.tag_config('bold', foreground='#fab387', font=('Menlo', 13, 'bold'))
        self.text.tag_config('italic', foreground='#94e2d5', font=('Menlo', 13, 'italic'))
        self.text.tag_config('code', foreground='#f38ba8', background='#2b2b2b')
        self.text.tag_config('link', foreground='#89b4fa', underline=True)
        self.text.tag_config('list', foreground='#f9e2af')
        self.text.tag_config('blockquote', foreground='#a6adc8')

        self.text.bind('<KeyRelease>', self.highlight_syntax)

    def highlight_syntax(self, event=None):
        """Apply Markdown syntax highlighting"""
        content = self.text.get('1.0', tk.END)

        # Remove all tags
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'bold', 'italic', 'code', 'link', 'list', 'blockquote']:
            self.text.tag_remove(tag, '1.0', tk.END)

        # Highlight headers
        for line_num, line in enumerate(content.split('\n'), 1):
            if line.startswith('# '):
                self.text.tag_add('h1', f'{line_num}.0', f'{line_num}.end')
            elif line.startswith('## '):
                self.text.tag_add('h2', f'{line_num}.0', f'{line_num}.end')
            elif line.startswith('### '):
                self.text.tag_add('h3', f'{line_num}.0', f'{line_num}.end')
            elif line.startswith('#### '):
                self.text.tag_add('h4', f'{line_num}.0', f'{line_num}.end')
            elif line.startswith('##### '):
                self.text.tag_add('h5', f'{line_num}.0', f'{line_num}.end')
            elif line.startswith('###### '):
                self.text.tag_add('h6', f'{line_num}.0', f'{line_num}.end')
            elif line.startswith('> '):
                self.text.tag_add('blockquote', f'{line_num}.0', f'{line_num}.end')
            elif re.match(r'^[\*\-]\s+', line) or re.match(r'^\d+\.\s+', line):
                self.text.tag_add('list', f'{line_num}.0', f'{line_num}.end')

        # Highlight bold **text**
        for match in re.finditer(r'\*\*(.+?)\*\*', content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text.tag_add('bold', start, end)

        # Highlight bold __text__
        for match in re.finditer(r'__(.+?)__', content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text.tag_add('bold', start, end)

        # Highlight italic *text*
        for match in re.finditer(r'\*(.+?)\*', content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            # Only if not part of **
            if not content[max(0, match.start()-1):match.start()] == '*':
                self.text.tag_add('italic', start, end)

        # Highlight italic _text_
        for match in re.finditer(r'_(.+?)_', content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            # Only if not part of __
            if not content[max(0, match.start()-1):match.start()] == '_':
                self.text.tag_add('italic', start, end)

        # Highlight inline code `code`
        for match in re.finditer(r'`(.+?)`', content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text.tag_add('code', start, end)

        # Highlight links [text](url)
        for match in re.finditer(r'\[(.+?)\]\((.+?)\)', content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text.tag_add('link', start, end)

        # Trigger preview update
        if self.on_content_changed:
            self.on_content_changed(self.tab_id)

    def update_position(self, event=None):
        """Update cursor position display"""
        position = self.text.index(tk.INSERT)
        line, col = position.split('.')
        self.position_label.config(text=f"Line {line}, Col {int(col)+1}")

    def on_text_modified(self, event=None):
        """Called when text is modified"""
        if self.text.edit_modified():
            self.modified = True
            if self.on_content_changed:
                self.on_content_changed(self.tab_id)
            self.text.edit_modified(False)

    def on_save_request(self):
        """Called when save is requested"""
        pass

    def get_content(self):
        """Get the markdown text content"""
        return self.text.get("1.0", tk.END).strip()

    def set_content(self, content):
        """Set the markdown text content"""
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", content)
        self.highlight_syntax()
        self.modified = False

    def set_file_path(self, path):
        """Set the file path for this tab"""
        self.file_path = path
        if path:
            filename = os.path.basename(path)
            self.file_label.config(text=filename, fg='#50fa7b')
        else:
            self.file_label.config(text="Untitled", fg='#808080')

    def insert_bold(self):
        """Insert bold markdown syntax"""
        try:
            selection = self.text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text.insert(tk.INSERT, f"**{selection}**")
        except:
            self.text.insert(tk.INSERT, "****")
            current_pos = self.text.index(tk.INSERT)
            line, col = current_pos.split('.')
            self.text.mark_set(tk.INSERT, f"{line}.{int(col)-2}")

    def insert_italic(self):
        """Insert italic markdown syntax"""
        try:
            selection = self.text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text.insert(tk.INSERT, f"*{selection}*")
        except:
            self.text.insert(tk.INSERT, "**")
            current_pos = self.text.index(tk.INSERT)
            line, col = current_pos.split('.')
            self.text.mark_set(tk.INSERT, f"{line}.{int(col)-1}")

    def insert_code(self):
        """Insert code markdown syntax"""
        try:
            selection = self.text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text.insert(tk.INSERT, f"`{selection}`")
        except:
            self.text.insert(tk.INSERT, "``")
            current_pos = self.text.index(tk.INSERT)
            line, col = current_pos.split('.')
            self.text.mark_set(tk.INSERT, f"{line}.{int(col)-1}")

    def insert_link(self):
        """Insert link markdown syntax"""
        try:
            selection = self.text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text.insert(tk.INSERT, f"[{selection}](url)")
        except:
            self.text.insert(tk.INSERT, "[text](url)")


class PreviewPanel:
    """HTML preview panel for markdown"""

    def __init__(self, parent):
        self.parent = parent
        self.container = tk.Frame(parent, bg='#2b2b2b')

        # Header
        header = tk.Frame(self.container, bg='#2b2b2b')
        header.pack(fill='x', padx=5, pady=(5, 2))

        tk.Label(header, text="Preview", bg='#2b2b2b', fg='white',
                font=('Arial', 10, 'bold')).pack(side='left')

        # Preview text widget (simpler HTML rendering)
        preview_frame = tk.Frame(self.container, bg='#404040', bd=1)
        preview_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.preview = tk.Text(preview_frame,
                              bg='#1e1e1e',
                              fg='#d4d4d4',
                              font=('Arial', 12),
                              wrap='word',
                              bd=0,
                              highlightthickness=0,
                              state='disabled')

        # Scrollbar
        vsb = ttk.Scrollbar(preview_frame, orient="vertical", command=self.preview.yview)

        self.preview.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')

        preview_frame.grid_rowconfigure(0, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)

        self.preview.config(yscrollcommand=vsb.set)

        # Configure tags for styled preview
        self.preview.tag_config('h1', foreground='#89b4fa', font=('Arial', 24, 'bold'))
        self.preview.tag_config('h2', foreground='#89b4fa', font=('Arial', 20, 'bold'))
        self.preview.tag_config('h3', foreground='#89b4fa', font=('Arial', 16, 'bold'))
        self.preview.tag_config('h4', foreground='#89b4fa', font=('Arial', 14, 'bold'))
        self.preview.tag_config('bold', foreground='#fab387', font=('Arial', 12, 'bold'))
        self.preview.tag_config('italic', foreground='#94e2d5', font=('Arial', 12, 'italic'))
        self.preview.tag_config('code', foreground='#f38ba8', background='#2b2b2b', font=('Menlo', 11))
        self.preview.tag_config('link', foreground='#89b4fa', underline=True)
        self.preview.tag_config('blockquote', foreground='#a6adc8', lmargin1=20, lmargin2=20)

    def update_preview(self, markdown_text):
        """Update preview with markdown content"""
        self.preview.config(state='normal')
        self.preview.delete('1.0', tk.END)

        if not markdown_text:
            self.preview.config(state='disabled')
            return

        # Simple rendering - just apply basic formatting
        lines = markdown_text.split('\n')
        for line in lines:
            if line.startswith('# '):
                self.preview.insert(tk.END, line[2:] + '\n', 'h1')
            elif line.startswith('## '):
                self.preview.insert(tk.END, line[3:] + '\n', 'h2')
            elif line.startswith('### '):
                self.preview.insert(tk.END, line[4:] + '\n', 'h3')
            elif line.startswith('#### '):
                self.preview.insert(tk.END, line[5:] + '\n', 'h4')
            elif line.startswith('> '):
                self.preview.insert(tk.END, line[2:] + '\n', 'blockquote')
            else:
                # Process inline formatting
                self._render_line(line)
                self.preview.insert(tk.END, '\n')

        self.preview.config(state='disabled')

    def _render_line(self, line):
        """Render a line with inline formatting"""
        if not line:
            return

        # Simple approach: process the line character by character
        pos = 0
        while pos < len(line):
            # Check for bold **
            if line[pos:pos+2] == '**':
                end = line.find('**', pos+2)
                if end != -1:
                    self.preview.insert(tk.END, line[pos+2:end], 'bold')
                    pos = end + 2
                    continue

            # Check for italic *
            if line[pos] == '*' and (pos == 0 or line[pos-1] != '*'):
                end = line.find('*', pos+1)
                if end != -1 and (end == len(line)-1 or line[end+1] != '*'):
                    self.preview.insert(tk.END, line[pos+1:end], 'italic')
                    pos = end + 1
                    continue

            # Check for code `
            if line[pos] == '`':
                end = line.find('`', pos+1)
                if end != -1:
                    self.preview.insert(tk.END, line[pos+1:end], 'code')
                    pos = end + 1
                    continue

            # Check for links [text](url)
            if line[pos] == '[':
                text_end = line.find(']', pos)
                if text_end != -1 and text_end+1 < len(line) and line[text_end+1] == '(':
                    url_end = line.find(')', text_end+2)
                    if url_end != -1:
                        self.preview.insert(tk.END, line[pos+1:text_end], 'link')
                        pos = url_end + 1
                        continue

            # Regular character
            self.preview.insert(tk.END, line[pos])
            pos += 1


class MarkdownEditorPro:
    """Main Markdown Editor Application"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Markdown Pro")

        # Start with a default size
        self.root.geometry("1200x700")

        # Maximize window
        self.root.after(100, self.maximize_window)

        # Variables
        self.tabs = {}
        self.tab_counter = 0
        self.preview_visible = True

        # Load settings
        self.settings = load_settings()
        self.last_folder = self.settings.get('last_folder', os.path.expanduser("~"))

        # Create UI
        self.create_widgets()

        # Bind shortcuts
        self.root.bind("<Command-o>", lambda e: self.open_file())
        self.root.bind("<Command-s>", lambda e: self.save_file())
        self.root.bind("<Command-n>", lambda e: self.create_new_tab())
        self.root.bind("<Command-t>", lambda e: self.create_new_tab())
        self.root.bind("<Command-b>", lambda e: self.insert_bold())
        self.root.bind("<Command-i>", lambda e: self.insert_italic())
        self.root.bind("<Command-k>", lambda e: self.insert_link())

    def maximize_window(self):
        """Maximize window to fill screen"""
        if sys.platform == 'darwin':
            try:
                self.root.state('zoomed')
            except:
                pass
        else:
            self.root.state('zoomed')

        self.root.configure(bg='#2b2b2b')

    def create_widgets(self):
        """Create the main UI"""

        # Top toolbar
        toolbar = tk.Frame(self.root, bg='#3c3c3c', height=40)
        toolbar.pack(fill='x', padx=0, pady=0)

        def create_button(parent, text, command, side='left'):
            btn = tk.Label(parent, text=text, bg='#404040', fg='white',
                          padx=12, pady=6, cursor='hand2', relief='raised', bd=1)
            btn.pack(side=side, padx=2, pady=5)
            btn.bind("<Button-1>", lambda e: command())

            def on_enter(e):
                btn.config(bg='#505050')
            def on_leave(e):
                btn.config(bg='#404040')

            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            return btn

        # Left side buttons
        create_button(toolbar, "+ NEW", self.create_new_tab)
        create_button(toolbar, "OPEN", self.open_file)
        create_button(toolbar, "SAVE", self.save_file)
        create_button(toolbar, "BOLD", self.insert_bold)
        create_button(toolbar, "ITALIC", self.insert_italic)
        create_button(toolbar, "CODE", self.insert_code)
        create_button(toolbar, "LINK", self.insert_link)

        # Toggle preview button
        self.preview_toggle_btn = create_button(toolbar, "PREVIEW ▼", self.toggle_preview)

        # Status label
        self.status_label = tk.Label(toolbar, text="", bg='#3c3c3c',
                                    fg='#808080', font=('Arial', 10))
        self.status_label.pack(side='right', padx=10)

        # Main container with paned window
        self.main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL,
                                         sashwidth=8, sashrelief=tk.RAISED,
                                         bg='#404040', borderwidth=0)
        self.main_paned.pack(fill='both', expand=True, padx=5, pady=5)

        # Left panel - Editor tabs
        left_panel = tk.Frame(self.root, bg='#2b2b2b')

        # Create notebook for tabs
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Custom.TNotebook',
                       background='#2b2b2b',
                       borderwidth=0)
        style.configure('Custom.TNotebook.Tab',
                       background='#404040',
                       foreground='#d4d4d4',
                       padding=[15, 8],
                       font=('Arial', 10))
        style.map('Custom.TNotebook.Tab',
                 background=[('selected', '#2b2b2b'), ('!selected', '#404040')],
                 foreground=[('selected', '#89b4fa'), ('!selected', '#d4d4d4')])

        self.notebook = ttk.Notebook(left_panel, style='Custom.TNotebook')
        self.notebook.pack(fill='both', expand=True)

        # Bind tab change event
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
        self.notebook.bind('<Button-3>', self.on_tab_right_click)

        # Right panel - Preview
        self.preview_panel = PreviewPanel(self.root)

        # Add panels to paned window
        self.main_paned.add(left_panel, minsize=400)
        self.main_paned.add(self.preview_panel.container, minsize=300)

        # Set initial sash position (35% editor, 65% preview)
        self.root.update_idletasks()
        total_width = self.main_paned.winfo_width()
        self.main_paned.sash_place(0, int(total_width * 0.35), 1)

        # Create first tab
        self.create_new_tab()

    def toggle_preview(self):
        """Toggle preview panel visibility"""
        if self.preview_visible:
            self.main_paned.forget(self.preview_panel.container)
            self.preview_toggle_btn.config(text="PREVIEW ▶")
            self.preview_visible = False
        else:
            self.main_paned.add(self.preview_panel.container)
            total_width = self.main_paned.winfo_width()
            self.main_paned.sash_place(0, int(total_width * 0.35), 1)
            self.preview_toggle_btn.config(text="PREVIEW ▼")
            self.preview_visible = True
            self.update_preview()

    def create_new_tab(self):
        """Create a new editing tab"""
        self.tab_counter += 1
        tab_id = self.tab_counter
        tab_name = f"Untitled {tab_id}"

        tab = MarkdownTab(self.notebook, tab_id, on_content_changed=self.on_tab_modified)

        self.tabs[tab_id] = {
            'tab': tab,
            'name': tab_name
        }

        self.notebook.add(tab.container, text=tab_name)
        self.notebook.select(tab.container)
        tab.text.focus_set()

    def get_current_tab(self):
        """Get the currently active tab"""
        current = self.notebook.select()
        if not current:
            return None

        for tab_id, tab_data in self.tabs.items():
            if str(tab_data['tab'].container) == current:
                return tab_data['tab']
        return None

    def on_tab_modified(self, tab_id):
        """Called when a tab is modified"""
        if tab_id in self.tabs:
            tab_data = self.tabs[tab_id]
            tab = tab_data['tab']
            name = tab_data['name']
            if tab.modified and not name.startswith('*'):
                self.notebook.tab(tab.container, text=f"*{name}")

        # Update preview
        self.update_preview()

    def on_tab_changed(self, event=None):
        """Called when tab changes"""
        self.update_preview()

    def update_preview(self):
        """Update preview panel"""
        if not self.preview_visible:
            return

        current_tab = self.get_current_tab()
        if current_tab:
            content = current_tab.get_content()
            self.preview_panel.update_preview(content)

    def on_tab_right_click(self, event):
        """Handle right-click on tab"""
        clicked_tab = self.notebook.tk.call(self.notebook._w, "identify", "tab", event.x, event.y)
        if clicked_tab == "":
            return

        tab_index = int(clicked_tab)
        tab_id = None
        for tid, tdata in self.tabs.items():
            if self.notebook.index(tdata['tab'].container) == tab_index:
                tab_id = tid
                break

        if not tab_id:
            return

        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Rename", command=lambda: self.rename_tab(tab_id))
        if len(self.tabs) > 1:
            menu.add_separator()
            menu.add_command(label="Close", command=lambda: self.close_tab(tab_id))
        menu.post(event.x_root, event.y_root)

    def rename_tab(self, tab_id):
        """Rename a tab"""
        pass

    def close_tab(self, tab_id):
        """Close a tab"""
        if tab_id not in self.tabs:
            return

        tab_data = self.tabs[tab_id]
        tab = tab_data['tab']

        if tab.modified:
            response = messagebox.askyesno(
                "Close Tab",
                f"Close '{tab_data['name']}'?\n\nUnsaved changes will be lost."
            )
            if not response:
                return

        self.notebook.forget(tab.container)
        tab.container.destroy()
        del self.tabs[tab_id]

    def open_file(self):
        """Open a markdown file"""
        filename = filedialog.askopenfilename(
            title="Open Markdown File",
            initialdir=self.last_folder,
            filetypes=[
                ("Markdown files", "*.md"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )

        if filename:
            # Save the folder for next time
            self.last_folder = os.path.dirname(filename)
            self.settings['last_folder'] = self.last_folder
            save_settings(self.settings)

            try:
                with open(filename, 'r') as f:
                    content = f.read()

                # Create new tab or use current empty tab
                current_tab = self.get_current_tab()
                if current_tab and not current_tab.get_content() and not current_tab.file_path:
                    tab = current_tab
                else:
                    self.create_new_tab()
                    tab = self.get_current_tab()

                # Load content
                tab.set_content(content)
                tab.set_file_path(filename)
                tab.modified = False

                # Update tab name
                for tab_id, tab_data in self.tabs.items():
                    if tab_data['tab'] == tab:
                        tab_data['name'] = os.path.basename(filename)
                        self.notebook.tab(tab.container, text=os.path.basename(filename))
                        break

                # Update preview
                self.update_preview()

                self.status_label.config(text=f"Opened: {os.path.basename(filename)}", fg='#50fa7b')
                self.root.after(3000, lambda: self.status_label.config(text=""))

            except Exception as e:
                messagebox.showerror("Error", f"Error opening file:\n{str(e)}")

    def save_file(self):
        """Save current markdown file"""
        current_tab = self.get_current_tab()
        if not current_tab:
            return

        # If no file path, do save as
        if not current_tab.file_path:
            self.save_file_as()
            return

        try:
            content = current_tab.get_content()

            with open(current_tab.file_path, 'w') as f:
                f.write(content)

            # Save the folder for next time
            self.last_folder = os.path.dirname(current_tab.file_path)
            self.settings['last_folder'] = self.last_folder
            save_settings(self.settings)

            current_tab.modified = False

            # Update tab name (remove *)
            for tab_id, tab_data in self.tabs.items():
                if tab_data['tab'] == current_tab:
                    self.notebook.tab(current_tab.container, text=tab_data['name'])
                    break

            self.status_label.config(text="Saved", fg='#50fa7b')
            self.root.after(2000, lambda: self.status_label.config(text=""))

        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def save_file_as(self):
        """Save as new file"""
        current_tab = self.get_current_tab()
        if not current_tab:
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".md",
            initialdir=self.last_folder,
            filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*.*")]
        )

        if filename:
            current_tab.set_file_path(filename)

            # Update tab name
            for tab_id, tab_data in self.tabs.items():
                if tab_data['tab'] == current_tab:
                    tab_data['name'] = os.path.basename(filename)
                    break

            self.save_file()

    def insert_bold(self):
        """Insert bold markdown"""
        current_tab = self.get_current_tab()
        if current_tab:
            current_tab.insert_bold()

    def insert_italic(self):
        """Insert italic markdown"""
        current_tab = self.get_current_tab()
        if current_tab:
            current_tab.insert_italic()

    def insert_code(self):
        """Insert code markdown"""
        current_tab = self.get_current_tab()
        if current_tab:
            current_tab.insert_code()

    def insert_link(self):
        """Insert link markdown"""
        current_tab = self.get_current_tab()
        if current_tab:
            current_tab.insert_link()

    def run(self):
        """Start the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        """Handle window closing"""
        # Check for unsaved changes
        unsaved = []
        for tab_id, tab_data in self.tabs.items():
            if tab_data['tab'].modified:
                unsaved.append(tab_data['name'])

        if unsaved:
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                f"Save changes before closing?\n\nUnsaved tabs: {', '.join(unsaved)}"
            )
            if response is None:  # Cancel
                return
            elif response:  # Yes - save all
                for tab_id, tab_data in self.tabs.items():
                    if tab_data['tab'].modified:
                        # Would need to implement save all
                        pass

        self.root.destroy()


def main():
    app = MarkdownEditorPro()
    app.run()


if __name__ == "__main__":
    main()
