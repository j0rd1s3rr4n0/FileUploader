import tkinter as tk
from dataclasses import dataclass
from tkinter import filedialog, font, messagebox, ttk

from fileuploader import FileUploaderCore
from fileuploader.branding import compact_credit
from fileuploader.formatting import format_output
from fileuploader.models import ProviderError


PALETTE = {
    "bg": "#eef2f7",
    "surface": "#ffffff",
    "surface_alt": "#f8fafc",
    "ink": "#111827",
    "muted": "#64748b",
    "line": "#d9e2ef",
    "brand": "#0f766e",
    "brand_hover": "#115e59",
    "brand_soft": "#ccfbf1",
    "danger": "#b91c1c",
    "warning": "#b45309",
    "success": "#047857",
    "disabled": "#6b7280",
}


@dataclass
class GuiState:
    service: str = "gofile"
    action: str = "upload"
    path: str = ""
    url: str = ""
    file_id: str = ""
    api_key: str = ""
    api_key_env: str = ""
    password: str = ""
    ttl: str = ""
    max_downloads: str = ""
    notify_jid: str = ""
    json_output: bool = False


def default_state() -> GuiState:
    return GuiState()


def build_options(state: GuiState) -> dict:
    return {
        "api_key": state.api_key or None,
        "api_key_env": state.api_key_env or None,
        "url": state.url or None,
        "password": state.password or None,
        "ttl": state.ttl or None,
        "max_downloads": state.max_downloads or None,
        "notify_jid": state.notify_jid or None,
    }


def active_services(services):
    return [service for service in services if service.active and not service.deprecated]


def deprecated_services(services):
    return [service for service in services if service.deprecated or not service.active]


def service_names(services):
    return [service.name for service in services]


def default_service_name(services):
    names = service_names(active_services(services))
    if "gofile" in names:
        return "gofile"
    return names[0] if names else ""


def service_by_name(services, name):
    for service in services:
        if service.name == name:
            return service
    raise ProviderError(name, f"Unknown provider: {name}", code="unknown_provider")


def actions_for_service(service):
    actions = []
    if service.supports_upload:
        actions.append("upload")
    if service.supports_download:
        actions.append("download")
    if service.supports_info:
        actions.append("info")
    return actions


def provider_status(service) -> str:
    if not service.active:
        return "disabled"
    if service.deprecated:
        return "deprecated"
    return "active"


def provider_summary(service) -> str:
    capabilities = []
    if service.supports_upload:
        capabilities.append("upload")
    if service.supports_download:
        capabilities.append("download")
    if service.supports_info:
        capabilities.append("info")
    credential = "token required" if service.requires_api_key else "no account needed"
    return f"{service.display_name} | {', '.join(capabilities) or 'listed only'} | {credential}"


def required_fields_for_state(state: GuiState, service) -> set[str]:
    fields = set()
    if state.action == "upload":
        fields.add("path")
        if service.name == "exploitsend":
            fields.update({"password", "ttl", "max_downloads", "notify_jid"})
    elif state.action == "download":
        fields.add("url")
    elif state.action == "info":
        fields.add("file_id")
    if service.requires_api_key:
        fields.add("api_key")
    return fields


def validate_state(state: GuiState, service=None) -> None:
    if service and state.action not in actions_for_service(service):
        raise ProviderError(state.service, f"{service.display_name} does not support {state.action}.", code="unsupported_action")
    if state.action == "upload" and not state.path:
        raise ProviderError(state.service, "Choose a file before uploading.", code="path_required")
    if state.action == "download" and not state.url:
        raise ProviderError(state.service, "Enter a download URL before downloading.", code="url_required")
    if state.action == "info" and not state.file_id:
        raise ProviderError(state.service, "Enter a file id before requesting info.", code="file_id_required")
    if service and service.requires_api_key and not (state.api_key or state.api_key_env):
        raise ProviderError(state.service, "Enter an API key or API key environment variable.", code="api_key_required")


class FileUploaderGui:
    def __init__(self, root, core=None):
        self.root = root
        self.core = core or FileUploaderCore()
        self.root.title("FileUploader")
        self.root.geometry("1080x760")
        self.root.minsize(920, 640)
        self.root.configure(bg=PALETTE["bg"])
        self.services = self.core.services(include_deprecated=True)
        self.active_service_names = service_names(active_services(self.services))
        self.service_lookup = {service.name: service for service in self.services}
        self._configure_style()
        self._build_widgets()

    def _configure_style(self):
        self.style = ttk.Style(self.root)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
        self.style.configure("TFrame", background=PALETTE["bg"])
        self.style.configure("Surface.TFrame", background=PALETTE["surface"])
        self.style.configure("TLabel", background=PALETTE["surface"], foreground=PALETTE["ink"], font=("Segoe UI", 10))
        self.style.configure("Page.TLabel", background=PALETTE["bg"], foreground=PALETTE["ink"], font=("Segoe UI", 10))
        self.style.configure("Heading.TLabel", background=PALETTE["surface"], foreground=PALETTE["ink"], font=("Segoe UI Semibold", 13))
        self.style.configure("Hint.TLabel", background=PALETTE["surface"], foreground=PALETTE["muted"], font=("Segoe UI", 9))
        self.style.configure("Status.TLabel", background=PALETTE["brand_soft"], foreground=PALETTE["brand"], font=("Segoe UI Semibold", 9), padding=(8, 4))
        self.style.configure("TButton", font=("Segoe UI", 10), padding=(10, 7))
        self.style.configure("Accent.TButton", background=PALETTE["brand"], foreground="#ffffff", font=("Segoe UI Semibold", 10), padding=(12, 8))
        self.style.map("Accent.TButton", background=[("active", PALETTE["brand_hover"])], foreground=[("active", "#ffffff")])
        self.style.configure("TCombobox", padding=6, fieldbackground=PALETTE["surface_alt"], background=PALETTE["surface_alt"])
        self.style.configure("TEntry", padding=7, fieldbackground=PALETTE["surface_alt"])
        self.style.configure("TCheckbutton", background=PALETTE["surface"], foreground=PALETTE["ink"], font=("Segoe UI", 10))

    def _build_widgets(self):
        container = ttk.Frame(self.root, padding=18)
        container.pack(fill="both", expand=True)

        header = tk.Frame(container, background=PALETTE["ink"], padx=20, pady=16, highlightthickness=0)
        header.pack(fill="x", pady=(0, 14))
        title_row = tk.Frame(header, background=PALETTE["ink"])
        title_row.pack(fill="x")
        mark = tk.Canvas(title_row, width=38, height=38, bg=PALETTE["ink"], highlightthickness=0)
        mark.pack(side="left", padx=(0, 12))
        mark.create_oval(3, 3, 35, 35, fill=PALETTE["brand"], outline="")
        mark.create_line(19, 10, 19, 25, fill="#ffffff", width=3)
        mark.create_line(12, 17, 19, 10, 26, 17, fill="#ffffff", width=3)
        mark.create_rectangle(11, 25, 27, 29, fill="#ffffff", outline="")
        title_stack = tk.Frame(title_row, background=PALETTE["ink"])
        title_stack.pack(side="left", fill="x", expand=True)
        tk.Label(title_stack, text="FileUploader", background=PALETTE["ink"], foreground="#ffffff", font=("Segoe UI Semibold", 24)).pack(anchor="w")
        tk.Label(
            title_stack,
            text="Unified uploads for temporary links, cloud accounts, scripts, and desktop workflows",
            background=PALETTE["ink"],
            foreground="#cbd5e1",
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(1, 0))
        tk.Label(header, text=compact_credit(), background=PALETTE["ink"], foreground="#99f6e4", font=("Segoe UI", 9)).pack(anchor="w", pady=(8, 0))

        main = ttk.Frame(container)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=0, minsize=380)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        controls = tk.Frame(main, background=PALETTE["surface"], padx=18, pady=16, highlightbackground=PALETTE["line"], highlightthickness=1)
        controls.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        ttk.Label(controls, text="Upload setup", style="Heading.TLabel").grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 12))

        ttk.Label(controls, text="Provider").grid(row=1, column=0, sticky="w", pady=(0, 5))
        self.service_var = tk.StringVar(value=default_service_name(self.services))
        self.service_combo = ttk.Combobox(controls, textvariable=self.service_var, values=self.active_service_names, state="readonly")
        self.service_combo.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(0, 10))
        self.service_combo.bind("<<ComboboxSelected>>", lambda _event: self._sync_service_fields())

        self.provider_meta_var = tk.StringVar(value="")
        self.provider_status_var = tk.StringVar(value="")
        ttk.Label(controls, textvariable=self.provider_meta_var, style="Hint.TLabel").grid(row=3, column=0, columnspan=3, sticky="w", pady=(0, 8))
        ttk.Label(controls, textvariable=self.provider_status_var, style="Status.TLabel").grid(row=3, column=3, sticky="e", pady=(0, 8))

        ttk.Label(controls, text="Action").grid(row=4, column=0, sticky="w", pady=(2, 5))
        self.action_var = tk.StringVar(value="upload")
        self.action_combo = ttk.Combobox(controls, textvariable=self.action_var, values=["upload"], state="readonly")
        self.action_combo.grid(row=5, column=0, columnspan=4, sticky="ew", pady=(0, 10))
        self.action_combo.bind("<<ComboboxSelected>>", lambda _event: self._sync_visible_fields())

        self.path_label = ttk.Label(controls, text="File")
        self.path_label.grid(row=6, column=0, sticky="w", pady=(2, 5))
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(controls, textvariable=self.path_var)
        self.path_entry.grid(row=7, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        self.browse_button = ttk.Button(controls, text="Browse", command=self._browse_file)
        self.browse_button.grid(row=7, column=3, sticky="ew", padx=(8, 0), pady=(0, 10))

        self.url_label = ttk.Label(controls, text="Download URL")
        self.url_label.grid(row=8, column=0, sticky="w", pady=(2, 5))
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(controls, textvariable=self.url_var)
        self.url_entry.grid(row=9, column=0, columnspan=4, sticky="ew", pady=(0, 10))

        self.file_id_label = ttk.Label(controls, text="File ID")
        self.file_id_label.grid(row=10, column=0, sticky="w", pady=(2, 5))
        self.file_id_var = tk.StringVar()
        self.file_id_entry = ttk.Entry(controls, textvariable=self.file_id_var)
        self.file_id_entry.grid(row=11, column=0, columnspan=4, sticky="ew", pady=(0, 10))

        self.api_key_label = ttk.Label(controls, text="API key / access token")
        self.api_key_label.grid(row=12, column=0, sticky="w", pady=(2, 5))
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(controls, textvariable=self.api_key_var, show="*")
        self.api_key_entry.grid(row=13, column=0, columnspan=4, sticky="ew", pady=(0, 10))

        self.api_key_env_label = ttk.Label(controls, text="Environment variable")
        self.api_key_env_label.grid(row=14, column=0, sticky="w", pady=(2, 5))
        self.api_key_env_var = tk.StringVar()
        self.api_key_env_entry = ttk.Entry(controls, textvariable=self.api_key_env_var)
        self.api_key_env_entry.grid(row=15, column=0, columnspan=4, sticky="ew", pady=(0, 10))

        self.password_label = ttk.Label(controls, text="Password (optional)")
        self.password_label.grid(row=16, column=0, sticky="w", pady=(2, 5))
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(controls, textvariable=self.password_var, show="*")
        self.password_entry.grid(row=17, column=0, columnspan=4, sticky="ew", pady=(0, 10))

        self.ttl_label = ttk.Label(controls, text="Retention seconds")
        self.ttl_label.grid(row=18, column=0, sticky="w", pady=(2, 5))
        self.ttl_var = tk.StringVar(value="2592000")
        self.ttl_entry = ttk.Entry(controls, textvariable=self.ttl_var)
        self.ttl_entry.grid(row=19, column=0, columnspan=2, sticky="ew", pady=(0, 10), padx=(0, 6))

        self.max_downloads_label = ttk.Label(controls, text="Max downloads")
        self.max_downloads_label.grid(row=18, column=2, sticky="w", pady=(2, 5), padx=(6, 0))
        self.max_downloads_var = tk.StringVar(value="1")
        self.max_downloads_entry = ttk.Entry(controls, textvariable=self.max_downloads_var)
        self.max_downloads_entry.grid(row=19, column=2, columnspan=2, sticky="ew", pady=(0, 10), padx=(6, 0))

        self.notify_jid_label = ttk.Label(controls, text="Notify JID (optional)")
        self.notify_jid_label.grid(row=20, column=0, sticky="w", pady=(2, 5))
        self.notify_jid_var = tk.StringVar()
        self.notify_jid_entry = ttk.Entry(controls, textvariable=self.notify_jid_var)
        self.notify_jid_entry.grid(row=21, column=0, columnspan=4, sticky="ew", pady=(0, 10))

        self.json_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(controls, text="JSON output", variable=self.json_var).grid(row=22, column=0, columnspan=2, sticky="w", pady=(0, 12))
        ttk.Button(controls, text="Run", command=self._run_action, style="Accent.TButton").grid(row=23, column=0, columnspan=2, sticky="ew", pady=(0, 10), padx=(0, 6))
        ttk.Button(controls, text="Copy", command=self._copy_result).grid(row=23, column=2, columnspan=2, sticky="ew", pady=(0, 10), padx=(6, 0))

        self.hint_var = tk.StringVar(value="Upload: choose a file. Download: enter URL. Info: enter file id.")
        ttk.Label(controls, textvariable=self.hint_var, style="Hint.TLabel", wraplength=330).grid(row=24, column=0, columnspan=4, sticky="ew", pady=(2, 0))

        for column in range(4):
            controls.columnconfigure(column, weight=1)

        self.deprecated_text = tk.Text(container, height=3, wrap="none", borderwidth=0)
        self.deprecated_text.pack(fill="x", pady=(12, 0))
        self.deprecated_text.configure(background=PALETTE["bg"], foreground=PALETTE["muted"], font=("Segoe UI", 9))
        strike_font = font.Font(self.deprecated_text, self.deprecated_text.cget("font"))
        strike_font.configure(overstrike=True)
        self.deprecated_text.tag_configure("deprecated", foreground=PALETTE["disabled"], font=strike_font)
        self._render_deprecated_services()
        self.deprecated_text.configure(state="disabled")

        output_panel = tk.Frame(main, background=PALETTE["surface"], padx=18, pady=16, highlightbackground=PALETTE["line"], highlightthickness=1)
        output_panel.grid(row=0, column=1, sticky="nsew")
        output_panel.rowconfigure(2, weight=1)
        output_panel.columnconfigure(0, weight=1)

        ttk.Label(output_panel, text="Result", style="Heading.TLabel").grid(row=0, column=0, sticky="w")
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(output_panel, textvariable=self.status_var, style="Hint.TLabel").grid(row=1, column=0, sticky="w", pady=(2, 12))
        self.output = tk.Text(output_panel, wrap="word", height=18, borderwidth=1, relief="solid")
        self.output.configure(
            background=PALETTE["surface_alt"],
            foreground=PALETTE["ink"],
            insertbackground=PALETTE["ink"],
            font=("Cascadia Mono", 10),
            padx=12,
            pady=10,
            relief="flat",
            borderwidth=0,
        )
        self.output.grid(row=2, column=0, sticky="nsew")
        self._sync_service_fields()

    def _render_deprecated_services(self):
        deprecated = deprecated_services(self.services)
        if not deprecated:
            self.deprecated_text.insert("end", "No deprecated services.")
            return
        self.deprecated_text.insert("end", "Disabled services: ")
        for index, service in enumerate(deprecated):
            if index:
                self.deprecated_text.insert("end", ", ")
            self.deprecated_text.insert("end", service.name, "deprecated")

    def _current_service(self):
        return self.service_lookup[self.service_var.get()]

    def _sync_service_fields(self):
        service = self._current_service()
        actions = actions_for_service(service)
        self.provider_meta_var.set(provider_summary(service))
        self.provider_status_var.set(provider_status(service).upper())
        self.action_combo.configure(values=actions)
        if self.action_var.get() not in actions:
            self.action_var.set(actions[0] if actions else "")
        self._sync_visible_fields()

    def _grid_or_hide(self, widgets, visible):
        for widget in widgets:
            if visible:
                widget.grid()
            else:
                widget.grid_remove()

    def _sync_visible_fields(self):
        service = self._current_service()
        state = self._state()
        fields = required_fields_for_state(state, service)
        self._grid_or_hide([self.path_label, self.path_entry, self.browse_button], "path" in fields)
        self._grid_or_hide([self.url_label, self.url_entry], "url" in fields)
        self._grid_or_hide([self.file_id_label, self.file_id_entry], "file_id" in fields)
        self._grid_or_hide([self.api_key_label, self.api_key_entry, self.api_key_env_label, self.api_key_env_entry], "api_key" in fields)
        self._grid_or_hide([self.password_label, self.password_entry], "password" in fields)
        self._grid_or_hide([self.ttl_label, self.ttl_entry], "ttl" in fields)
        self._grid_or_hide([self.max_downloads_label, self.max_downloads_entry], "max_downloads" in fields)
        self._grid_or_hide([self.notify_jid_label, self.notify_jid_entry], "notify_jid" in fields)
        self.hint_var.set(self._hint_text(state, service, fields))

    def _hint_text(self, state, service, fields):
        if service.deprecated:
            return f"{service.display_name} is deprecated and disabled."
        if not service.active:
            return f"{service.display_name} is disabled."
        if not fields:
            return f"{service.display_name}: no extra fields required."
        labels = {
            "path": "choose a file",
            "url": "enter a download URL",
            "file_id": "enter a file id",
            "api_key": "enter an API key or API key environment variable",
            "password": "optionally set a password",
            "ttl": "set retention seconds",
            "max_downloads": "set max downloads",
            "notify_jid": "optionally set a notification JID",
        }
        return f"{service.display_name} {state.action}: " + "; ".join(labels[field] for field in sorted(fields))

    def _state(self) -> GuiState:
        return GuiState(
            service=self.service_var.get(),
            action=self.action_var.get(),
            path=self.path_var.get(),
            url=self.url_var.get(),
            file_id=self.file_id_var.get(),
            api_key=self.api_key_var.get(),
            api_key_env=self.api_key_env_var.get(),
            password=self.password_var.get(),
            ttl=self.ttl_var.get(),
            max_downloads=self.max_downloads_var.get(),
            notify_jid=self.notify_jid_var.get(),
            json_output=self.json_var.get(),
        )

    def _browse_file(self):
        filename = filedialog.askopenfilename(title="Select file")
        if filename:
            self.path_var.set(filename)

    def _set_output(self, text):
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, text)

    def _run_action(self):
        state = self._state()
        try:
            self.status_var.set(f"Running {state.action} with {state.service}...")
            service = self._current_service()
            validate_state(state, service)
            if state.action == "upload":
                result = self.core.upload(state.service, state.path, **build_options(state))
            elif state.action == "download":
                result = self.core.download(state.service, **build_options(state))
            elif state.action == "info":
                result = self.core.info(state.service, state.file_id, **build_options(state))
            else:
                raise ProviderError(state.service, f"Unknown action: {state.action}")
            if hasattr(result, "to_dict"):
                result = result.to_dict()
            self._set_output(format_output(result, json_output=state.json_output))
            self.status_var.set(f"Completed {state.action} with {service.display_name}.")
        except ProviderError as exc:
            self._set_output(format_output({"ok": False, "error": exc.to_dict()}, json_output=state.json_output))
            self.status_var.set(f"{exc.provider}: {exc.message}")
        except Exception as exc:
            self.status_var.set("Unexpected error.")
            messagebox.showerror("FileUploader", str(exc))

    def _copy_result(self):
        text = self.output.get("1.0", tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        self.status_var.set("Result copied.")


def main():
    root = tk.Tk()
    FileUploaderGui(root)
    root.mainloop()


if __name__ == "__main__":
    main()
