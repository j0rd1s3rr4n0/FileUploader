from dataclasses import dataclass

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from fileuploader import FileUploaderCore
from fileuploader.formatting import format_output
from fileuploader.models import ProviderError


@dataclass
class TuiRequest:
    service: str
    action: str
    path: str = ""
    url: str = ""
    file_id: str = ""
    api_key: str = ""
    api_key_env: str = ""
    json_output: bool = False


def service_table(core=None) -> Table:
    core = core or FileUploaderCore()
    table = Table(title="FileUploader Services")
    table.add_column("Name")
    table.add_column("Display")
    table.add_column("Upload")
    table.add_column("Download")
    table.add_column("Info")
    table.add_column("Deprecated")
    for service in core.services(include_deprecated=True):
        table.add_row(
            service.name,
            service.display_name,
            "yes" if service.supports_upload else "no",
            "yes" if service.supports_download else "no",
            "yes" if service.supports_info else "no",
            "yes" if service.deprecated else "no",
        )
    return table


def request_options(request: TuiRequest) -> dict:
    return {
        "api_key": request.api_key or None,
        "api_key_env": request.api_key_env or None,
        "url": request.url or None,
    }


def validate_request(request: TuiRequest) -> None:
    if request.action == "upload" and not request.path:
        raise ProviderError(request.service, "Provide a file path to upload.", code="path_required")
    if request.action == "download" and not request.url:
        raise ProviderError(request.service, "Provide a download URL.", code="url_required")
    if request.action == "info" and not request.file_id:
        raise ProviderError(request.service, "Provide a file id.", code="file_id_required")


class FileUploaderTui:
    def __init__(self, core=None, console=None):
        self.core = core or FileUploaderCore()
        self.console = console or Console()

    def run_once(self, request: TuiRequest):
        try:
            validate_request(request)
            if request.action == "upload":
                result = self.core.upload(request.service, request.path, **request_options(request))
            elif request.action == "download":
                result = self.core.download(request.service, **request_options(request))
            elif request.action == "info":
                result = self.core.info(request.service, request.file_id, **request_options(request))
            else:
                raise ProviderError(request.service, f"Unknown action: {request.action}")
            if hasattr(result, "to_dict"):
                result = result.to_dict()
            return {"ok": True, "result": result}
        except ProviderError as exc:
            return {"ok": False, "error": exc.to_dict()}

    def interactive(self):
        self.console.print(Panel.fit("FileUploader TUI\nPick a provider, choose an action, then fill only the fields requested."))
        self.console.print(service_table(self.core))
        services = [service.name for service in self.core.services(include_deprecated=True)]
        while True:
            service = Prompt.ask("Service", choices=services, default=services[0])
            action = Prompt.ask("Action", choices=["upload", "download", "info"], default="upload")
            path = Prompt.ask("File path to upload", default="") if action == "upload" else ""
            url = Prompt.ask("Download URL", default="") if action == "download" else ""
            file_id = Prompt.ask("Provider file ID", default="") if action == "info" else ""
            api_key = Prompt.ask("API key, leave blank if not needed", password=True, default="")
            api_key_env = Prompt.ask("API key environment variable, leave blank if not needed", default="")
            json_output = Confirm.ask("JSON output?", default=False)

            payload = self.run_once(
                TuiRequest(
                    service=service,
                    action=action,
                    path=path,
                    url=url,
                    file_id=file_id,
                    api_key=api_key,
                    api_key_env=api_key_env,
                    json_output=json_output,
                )
            )
            self.console.print(Panel(format_output(payload, json_output=json_output), title="Result"))
            if not Confirm.ask("Run another action?", default=False):
                break


def main():
    FileUploaderTui().interactive()


if __name__ == "__main__":
    main()
