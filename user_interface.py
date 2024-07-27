import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from tkinter import font as tkfont
import threading
import docx
from PIL import Image, ImageTk

class UserInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Professional Technical Writing Assistant")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Set custom theme
        self.style = ttk.Style()
        self.style.theme_create("modern", parent="alt", settings={
            "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0]}},
            "TNotebook.Tab": {"configure": {"padding": [10, 5], "background": "#f0f0f0"},
                              "map": {"background": [("selected", "#ffffff")],
                                      "expand": [("selected", [1, 1, 1, 0])]}},
            "TFrame": {"configure": {"background": "#ffffff"}},
            "TButton": {"configure": {"padding": [10, 5], "font": ("Roboto", 10)}},
            "TLabel": {"configure": {"font": ("Roboto", 11)}},
            "TEntry": {"configure": {"font": ("Roboto", 11)}},
            "TCombobox": {"configure": {"padding": 5, "font": ("Roboto", 11)}},
        })
        self.style.theme_use("modern")

        # Load and set custom fonts
        self.load_fonts()

        self.create_menu()
        self.create_main_interface()
        self.generated_doc = None

    def load_fonts(self):
        self.title_font = tkfont.Font(family="Roboto", size=18, weight="bold")
        self.header_font = tkfont.Font(family="Roboto", size=14, weight="bold")
        self.body_font = tkfont.Font(family="Roboto", size=11)

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Document", command=self.new_document)
        file_menu.add_command(label="Save", command=self.save_document)
        file_menu.add_command(label="Download", command=self.download_document)
        file_menu.add_command(label="Preview", command=self.preview_document)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_main_interface(self):
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(self.main_frame, text="Professional Technical Writing Assistant", font=self.title_font)
        title_label.pack(pady=(0, 20))

        # Options Frame
        options_frame = ttk.Frame(self.main_frame)
        options_frame.pack(fill=tk.X, pady=(0, 20))

        # Approach
        approach_frame = ttk.Frame(options_frame)
        approach_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Label(approach_frame, text="Approach:", font=self.body_font).pack(anchor=tk.W)
        self.approach_var = tk.StringVar(value="Technical")
        approach_combobox = ttk.Combobox(approach_frame, textvariable=self.approach_var, 
                                         values=["Technical", "Non-Technical", "Conversational", "Formal", "Objective", "Subjective", "Collaborative"])
        approach_combobox.pack(fill=tk.X, pady=(5, 0))

        # Purpose
        purpose_frame = ttk.Frame(options_frame)
        purpose_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Label(purpose_frame, text="Purpose:", font=self.body_font).pack(anchor=tk.W)
        self.purpose_var = tk.StringVar(value="General")
        purpose_combobox = ttk.Combobox(purpose_frame, textvariable=self.purpose_var, 
                                        values=["Instructional", "Informative", "Descriptive", "Persuasive", "Analytical", "Evaluative", "Creative"])
        purpose_combobox.pack(fill=tk.X, pady=(5, 0))

        # Category
        category_frame = ttk.Frame(options_frame)
        category_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(category_frame, text="Category:", font=self.body_font).pack(anchor=tk.W)
        self.category_var = tk.StringVar(value="General")
        category_combobox = ttk.Combobox(category_frame, textvariable=self.category_var, 
                                         values=["User Manual", "Technical Specification", "Report", "Analysis", "Whitepaper", "Instructional Video Script", "API Documentation", "Technical Blog Post", "Case Study"])
        category_combobox.pack(fill=tk.X, pady=(5, 0))

        # Content
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        ttk.Label(content_frame, text="Content:", font=self.body_font).pack(anchor=tk.W)
        self.content_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, font=self.body_font)
        self.content_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # Buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 20))

        generate_btn = ttk.Button(button_frame, text="Generate Document", command=self.generate_document)
        generate_btn.pack(side=tk.LEFT, padx=(0, 10))

        preview_btn = ttk.Button(button_frame, text="Preview", command=self.preview_document)
        preview_btn.pack(side=tk.LEFT, padx=(0, 10))

        download_btn = ttk.Button(button_frame, text="Download", command=self.download_document)
        download_btn.pack(side=tk.LEFT)

        # Progress bar
        self.progress_bar = ttk.Progressbar(self.main_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X)
        self.progress_bar.pack_forget()

    def set_generate_callback(self, callback):
        self.generate_callback = callback

    def set_save_callback(self, callback):
        self.save_callback = callback

    def validate_input(self, content):
        return content.strip()

    def generate_document(self):
        approach = self.approach_var.get()
        purpose = self.purpose_var.get()
        category = self.category_var.get()
        content = self.content_text.get("1.0", tk.END)

        sanitized_content = self.validate_input(content)

        if len(sanitized_content) < 10:
            self.display_message("Please provide more content for meaningful document generation.")
            return

        self.progress_bar.pack()
        self.progress_bar.start()

        def generate():
            self.generated_doc = self.generate_callback(approach, purpose, category, sanitized_content)
            self.root.after(0, self.generation_complete)

        threading.Thread(target=generate, daemon=True).start()

    def generation_complete(self):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        if self.generated_doc:
            self.display_message("Document generated successfully. You can now save, download, or preview it.")
        else:
            self.display_message("Failed to generate document. Please try again.")

    def preview_document(self):
        if not self.generated_doc:
            self.display_message("Please generate a document first.")
            return

        preview_window = tk.Toplevel(self.root)
        preview_window.title("Document Preview")
        preview_window.geometry("800x600")

        preview_text = scrolledtext.ScrolledText(preview_window, wrap=tk.WORD, font=self.body_font)
        preview_text.pack(expand=True, fill=tk.BOTH)

        content = self.get_doc_text(self.generated_doc)
        preview_text.insert(tk.END, content)
        preview_text.config(state=tk.DISABLED)

    def get_doc_text(self, doc):
        if not doc:
            return ""
        text = []
        for para in doc.paragraphs:
            text.append(para.text)
        return "\n".join(text)

    def save_document(self):
        if not self.generated_doc:
            self.display_message("Please generate a document first.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".docx",
                                                 filetypes=[("Word Document", "*.docx"), ("PDF", "*.pdf")])
        if file_path:
            self.save_callback(self.generated_doc, file_path)

    def download_document(self):
        self.save_document()

    def new_document(self):
        self.generated_doc = None
        self.content_text.delete("1.0", tk.END)
        self.approach_var.set("Technical")
        self.purpose_var.set("Instructional")
        self.category_var.set("User Manual")

    def show_about(self):
        messagebox.showinfo("About", "Professional Technical Writing Assistant\nVersion 1.0\n\nCreated by Your Company")

    def display_message(self, message):
        messagebox.showinfo("Information", message)

    def run(self):
        self.root.mainloop()