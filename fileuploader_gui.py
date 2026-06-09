import tkinter as tk
from dataclasses import dataclass
from tkinter import filedialog, font, messagebox, ttk

from fileuploader import FileUploaderCore
from fileuploader.formatting import format_output
from fileuploader.models import ProviderError


@dataclass
class GuiState:
    service: str = "gofile"
    action: str = "upload"
    path: str = ""
    url: str = ""
    file_id: str = ""
    api_key: str = ""
    api_key_env: str = ""
    json_output: bool = False


def default_state() -> GuiState:
    return GuiState()


def build_options(state: GuiState) -> dict:
    return {
        "api_key": state.api_key or None,
        "api_key_env": state.api_key_env or None,
        "url": state.url or None,
    }


def active_services(services):
    return [service for service in services if not service.deprecated]


def deprecated_services(services):
    return [service for service in services if service.deprecated]


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


def required_fields_for_state(state: GuiState, service) -> set[str]:
    fields = set()
    if state.action == "upload":
        fields.add("path")
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
        self.root.geometry("920x680")
        self.services = self.core.services(include_deprecated=True)
        self.active_service_names = service_names(active_services(self.services))
        self.service_lookup = {service.name: service for service in self.services}
        self._build_widgets()

    def _build_widgets(self):
        container = ttk.Frame(self.root, padding=12)
        container.pack(fill="both", expand=True)

        ttk.Label(
            container,
            text="Choose a provider, action, and the required fields. Results appear below and can be copied.",
        ).pack(fill="x", pady=(0, 10))

        controls = ttk.Frame(container)
        controls.pack(fill="x")

        ttk.Label(controls, text="Active service").grid(row=0, column=0, sticky="w")
        self.service_var = tk.StringVar(value=default_service_name(self.services))
        self.service_combo = ttk.Combobox(controls, textvariable=self.service_var, values=self.active_service_names, state="readonly")
        self.service_combo.grid(row=0, column=1, sticky="ew", padx=6)
        self.service_combo.bind("<<ComboboxSelected>>", lambda _event: self._sync_service_fields())

        ttk.Label(controls, text="Action").grid(row=0, column=2, sticky="w")
        self.action_var = tk.StringVar(value="upload")
        self.action_combo = ttk.Combobox(controls, textvariable=self.action_var, values=["upload"], state="readonly")
        self.action_combo.grid(row=0, column=3, sticky="ew", padx=6)
        self.action_combo.bind("<<ComboboxSelected>>", lambda _event: self._sync_visible_fields())

        self.path_label = ttk.Label(controls, text="File")
        self.path_label.grid(row=1, column=0, sticky="w", pady=6)
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(controls, textvariable=self.path_var)
        self.path_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=6)
        self.browse_button = ttk.Button(controls, text="Browse", command=self._browse_file)
        self.browse_button.grid(row=1, column=3, sticky="ew", padx=6)

        self.url_label = ttk.Label(controls, text="Download URL")
        self.url_label.grid(row=2, column=0, sticky="w", pady=6)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(controls, textvariable=self.url_var)
        self.url_entry.grid(row=2, column=1, columnspan=3, sticky="ew", padx=6)

        self.file_id_label = ttk.Label(controls, text="File ID")
        self.file_id_label.grid(row=3, column=0, sticky="w", pady=6)
        self.file_id_var = tk.StringVar()
        self.file_id_entry = ttk.Entry(controls, textvariable=self.file_id_var)
        self.file_id_entry.grid(row=3, column=1, columnspan=3, sticky="ew", padx=6)

        self.api_key_label = ttk.Label(controls, text="API Key")
        self.api_key_label.grid(row=4, column=0, sticky="w", pady=6)
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(controls, textvariable=self.api_key_var, show="*")
        self.api_key_entry.grid(row=4, column=1, sticky="ew", padx=6)

        self.api_key_env_label = ttk.Label(controls, text="API Key Env")
        self.api_key_env_label.grid(row=4, column=2, sticky="w", pady=6)
        self.api_key_env_var = tk.StringVar()
        self.api_key_env_entry = ttk.Entry(controls, textvariable=self.api_key_env_var)
        self.api_key_env_entry.grid(row=4, column=3, sticky="ew", padx=6)

        self.json_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(controls, text="JSON output", variable=self.json_var).grid(row=5, column=1, sticky="w", padx=6)
        ttk.Button(controls, text="Run action", command=self._run_action).grid(row=5, column=2, sticky="ew", padx=6, pady=8)
        ttk.Button(controls, text="Copy result", command=self._copy_result).grid(row=5, column=3, sticky="ew", padx=6, pady=8)

        self.hint_var = tk.StringVar(value="Upload: choose a file. Download: enter URL. Info: enter file id.")
        ttk.Label(controls, textvariable=self.hint_var).grid(row=6, column=0, columnspan=4, sticky="w", pady=(2, 0))

        controls.columnconfigure(1, weight=1)
        controls.columnconfigure(3, weight=1)

        self.deprecated_text = tk.Text(container, height=3, wrap="none", borderwidth=0)
        self.deprecated_text.pack(fill="x", pady=(10, 0))
        strike_font = font.Font(self.deprecated_text, self.deprecated_text.cget("font"))
        strike_font.configure(overstrike=True)
        self.deprecated_text.tag_configure("deprecated", foreground="#777777", font=strike_font)
        self._render_deprecated_services()
        self.deprecated_text.configure(state="disabled")

        self.output = tk.Text(container, wrap="word", height=18)
        self.output.pack(fill="both", expand=True, pady=(10, 0))
        self._sync_service_fields()

    def _render_deprecated_services(self):
        deprecated = deprecated_services(self.services)
        if not deprecated:
            self.deprecated_text.insert("end", "No deprecated services.")
            return
        self.deprecated_text.insert("end", "Deprecated services disabled: ")
        for index, service in enumerate(deprecated):
            if index:
                self.deprecated_text.insert("end", ", ")
            self.deprecated_text.insert("end", service.name, "deprecated")

    def _current_service(self):
        return self.service_lookup[self.service_var.get()]

    def _sync_service_fields(self):
        service = self._current_service()
        actions = actions_for_service(service)
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
        self.hint_var.set(self._hint_text(state, service, fields))

    def _hint_text(self, state, service, fields):
        if service.deprecated:
            return f"{service.display_name} is deprecated and disabled."
        if not fields:
            return f"{service.display_name}: no extra fields required."
        labels = {
            "path": "choose a file",
            "url": "enter a download URL",
            "file_id": "enter a file id",
            "api_key": "enter an API key or API key environment variable",
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
        except ProviderError as exc:
            self._set_output(format_output({"ok": False, "error": exc.to_dict()}, json_output=state.json_output))
        except Exception as exc:
            messagebox.showerror("FileUploader", str(exc))

    def _copy_result(self):
        text = self.output.get("1.0", tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()


def main():
    root = tk.Tk()
    FileUploaderGui(root)
    root.mainloop()


if __name__ == "__main__":
    main()
