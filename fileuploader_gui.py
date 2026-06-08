import tkinter as tk
from dataclasses import dataclass
from tkinter import filedialog, messagebox, ttk

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


class FileUploaderGui:
    def __init__(self, root, core=None):
        self.root = root
        self.core = core or FileUploaderCore()
        self.root.title("FileUploader")
        self.root.geometry("760x560")
        self.services = self.core.services(include_deprecated=True)
        self.service_names = [service.name for service in self.services]
        self._build_widgets()

    def _build_widgets(self):
        container = ttk.Frame(self.root, padding=12)
        container.pack(fill="both", expand=True)

        controls = ttk.Frame(container)
        controls.pack(fill="x")

        ttk.Label(controls, text="Service").grid(row=0, column=0, sticky="w")
        self.service_var = tk.StringVar(value=self.service_names[0] if self.service_names else "")
        ttk.Combobox(controls, textvariable=self.service_var, values=self.service_names, state="readonly").grid(row=0, column=1, sticky="ew", padx=6)

        ttk.Label(controls, text="Action").grid(row=0, column=2, sticky="w")
        self.action_var = tk.StringVar(value="upload")
        ttk.Combobox(controls, textvariable=self.action_var, values=["upload", "download", "info"], state="readonly").grid(row=0, column=3, sticky="ew", padx=6)

        ttk.Label(controls, text="File").grid(row=1, column=0, sticky="w", pady=6)
        self.path_var = tk.StringVar()
        ttk.Entry(controls, textvariable=self.path_var).grid(row=1, column=1, columnspan=2, sticky="ew", padx=6)
        ttk.Button(controls, text="Browse", command=self._browse_file).grid(row=1, column=3, sticky="ew", padx=6)

        ttk.Label(controls, text="URL").grid(row=2, column=0, sticky="w", pady=6)
        self.url_var = tk.StringVar()
        ttk.Entry(controls, textvariable=self.url_var).grid(row=2, column=1, columnspan=3, sticky="ew", padx=6)

        ttk.Label(controls, text="File ID").grid(row=3, column=0, sticky="w", pady=6)
        self.file_id_var = tk.StringVar()
        ttk.Entry(controls, textvariable=self.file_id_var).grid(row=3, column=1, columnspan=3, sticky="ew", padx=6)

        ttk.Label(controls, text="API Key").grid(row=4, column=0, sticky="w", pady=6)
        self.api_key_var = tk.StringVar()
        ttk.Entry(controls, textvariable=self.api_key_var, show="*").grid(row=4, column=1, sticky="ew", padx=6)

        ttk.Label(controls, text="API Key Env").grid(row=4, column=2, sticky="w", pady=6)
        self.api_key_env_var = tk.StringVar()
        ttk.Entry(controls, textvariable=self.api_key_env_var).grid(row=4, column=3, sticky="ew", padx=6)

        self.json_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(controls, text="JSON output", variable=self.json_var).grid(row=5, column=1, sticky="w", padx=6)
        ttk.Button(controls, text="Run", command=self._run_action).grid(row=5, column=2, sticky="ew", padx=6, pady=8)
        ttk.Button(controls, text="Copy result", command=self._copy_result).grid(row=5, column=3, sticky="ew", padx=6, pady=8)

        controls.columnconfigure(1, weight=1)
        controls.columnconfigure(3, weight=1)

        self.output = tk.Text(container, wrap="word", height=18)
        self.output.pack(fill="both", expand=True, pady=(10, 0))

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
