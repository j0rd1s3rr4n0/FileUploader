import os
from typing import Optional

import typer

from .branding import banner_text
from .clipboard import copy_text
from .core import FileUploaderCore
from .formatting import format_output, service_rows
from .models import ProviderError
from .validation import require_value


app = typer.Typer(
    help="Upload files with GoFile, AnonFilesNew, JSONBin, AnonFiles, or BayFiles.",
    no_args_is_help=True,
)


def _banner_enabled(ctx: typer.Context, json_output: bool = False) -> bool:
    return not json_output and not (ctx.obj or {}).get("no_banner", False)


def _print_banner(ctx: typer.Context, json_output: bool = False):
    if _banner_enabled(ctx, json_output):
        typer.echo(banner_text())
        typer.echo()


@app.callback()
def app_options(
    ctx: typer.Context,
    no_banner: bool = typer.Option(False, "--no-banner", help="Hide the FileUploader banner and credits."),
):
    ctx.obj = {"no_banner": no_banner}


def _resolve_api_key(api_key: Optional[str], api_key_env: Optional[str]) -> Optional[str]:
    if api_key:
        return api_key
    if api_key_env:
        return os.environ.get(api_key_env)
    return None


def _print_result(result, json_output: bool):
    typer.echo(format_output(result, json_output=json_output))


def _exit_provider_error(error: ProviderError, json_output: bool):
    payload = {"ok": False, "error": error.to_dict()}
    _print_result(payload, json_output)
    raise typer.Exit(code=1)


def _service_names(core: FileUploaderCore) -> list[str]:
    return [service.name for service in core.services(include_deprecated=True)]


def build_guided_upload(core: FileUploaderCore, service: str, path: str, api_key: Optional[str], api_key_env: Optional[str]):
    require_value(service, path, "Provide a file path to upload.", "path_required")
    return core.upload(service, path, api_key=_resolve_api_key(api_key, api_key_env), api_key_env=api_key_env)


def build_guided_download(core: FileUploaderCore, service: str, url: str):
    require_value(service, url, "Provide a download URL.", "url_required")
    return core.download(service, url=url)


def build_guided_info(core: FileUploaderCore, service: str, file_id: str, api_key: Optional[str], api_key_env: Optional[str]):
    require_value(service, file_id, "Provide the provider file id.", "file_id_required")
    return core.info(service, file_id, api_key=_resolve_api_key(api_key, api_key_env), api_key_env=api_key_env)


@app.command()
def services(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
    include_deprecated: bool = typer.Option(True, "--include-deprecated/--active-only", help="Include deprecated providers."),
):
    """List available providers."""
    _print_banner(ctx, json_output)
    result = FileUploaderCore().services(include_deprecated=include_deprecated)
    services_data = [service.to_dict() for service in result]
    typer.echo(format_output(services_data, json_output=True) if json_output else service_rows(services_data))


@app.command()
def guided(ctx: typer.Context):
    """Run a step-by-step upload, download, or info flow."""
    core = FileUploaderCore()
    _print_banner(ctx, json_output=False)
    services_data = [service.to_dict() for service in core.services(include_deprecated=True)]
    typer.echo("Available providers:")
    typer.echo(service_rows(services_data))

    service = typer.prompt("Provider", default=services_data[0]["name"])
    action = typer.prompt("Action", default="upload")
    api_key = None
    api_key_env = None
    json_output = typer.confirm("Print JSON output?", default=False)

    try:
        if action == "upload":
            path = typer.prompt("File path to upload")
            api_key = typer.prompt("API key, leave blank if not needed", default="")
            api_key_env = typer.prompt("API key environment variable, leave blank if not needed", default="")
            result = build_guided_upload(core, service, path, api_key or None, api_key_env or None)
        elif action == "download":
            url = typer.prompt("Download URL")
            result = build_guided_download(core, service, url)
        elif action == "info":
            file_id = typer.prompt("Provider file ID")
            api_key = typer.prompt("API key, leave blank if not needed", default="")
            api_key_env = typer.prompt("API key environment variable, leave blank if not needed", default="")
            result = build_guided_info(core, service, file_id, api_key or None, api_key_env or None)
        else:
            choices = "upload, download, info"
            raise ProviderError(service, f"Unknown action '{action}'. Choose one of: {choices}", code="unknown_action")
    except ProviderError as error:
        _exit_provider_error(error, json_output)
        return

    if hasattr(result, "to_dict"):
        result = result.to_dict()
    _print_result(result, json_output)


@app.command()
def upload(
    ctx: typer.Context,
    path: str = typer.Argument(..., help="File path to upload, for example ./document.pdf."),
    service: str = typer.Option(..., "--service", "-s", help="Provider name. Run `services` to list choices."),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="Provider API key. Prefer --api-key-env for repeat use."),
    api_key_env: Optional[str] = typer.Option(None, "--api-key-env", help="Environment variable that contains the API key."),
    password: Optional[str] = typer.Option(None, "--password", help="Optional provider password when supported."),
    ttl: Optional[str] = typer.Option(None, "--ttl", help="Provider retention in seconds when supported."),
    max_downloads: Optional[str] = typer.Option(None, "--max-downloads", help="Provider download limit when supported."),
    notify_jid: Optional[str] = typer.Option(None, "--notify-jid", help="Optional notification JID when supported."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
    plaintext: bool = typer.Option(False, "--plaintext", help="Print plaintext output."),
    copy: bool = typer.Option(False, "--copy", help="Copy output to clipboard."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
):
    """Upload a file with a provider."""
    _print_banner(ctx, json_output)
    try:
        require_value(service, path, "Provide a file path to upload.", "path_required")
        result = FileUploaderCore().upload(
            service,
            path,
            api_key=_resolve_api_key(api_key, api_key_env),
            api_key_env=api_key_env,
            password=password,
            ttl=ttl,
            max_downloads=max_downloads,
            notify_jid=notify_jid,
            verbose=verbose,
        )
    except ProviderError as error:
        _exit_provider_error(error, json_output)
        return

    output = format_output(result.to_dict(), json_output=json_output and not plaintext)
    typer.echo(output)
    if copy:
        try:
            copy_text(output)
            typer.echo("Copied result to clipboard.")
        except Exception as exc:
            typer.echo(f"Could not copy result to clipboard: {exc}", err=True)


@app.command()
def download(
    ctx: typer.Context,
    service: str = typer.Option(..., "--service", "-s", help="Provider name. GoFile supports download metadata."),
    url: Optional[str] = typer.Option(None, "--url", help="Direct download URL."),
    server: Optional[str] = typer.Option(None, "--server", help="Provider server."),
    file_id: Optional[str] = typer.Option(None, "--file-id", help="Provider file id."),
    filename: Optional[str] = typer.Option(None, "--filename", help="Provider filename."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
):
    """Download or fetch download metadata."""
    _print_banner(ctx, json_output)
    try:
        if not url and not all([server, file_id, filename]):
            raise ProviderError(service, "Provide --url or --server, --file-id, and --filename.", code="download_target_required")
        result = FileUploaderCore().download(
            service,
            url=url,
            server=server,
            file_id=file_id,
            filename=filename,
            verbose=verbose,
        )
    except ProviderError as error:
        _exit_provider_error(error, json_output)
        return
    _print_result(result, json_output)


@app.command()
def info(
    ctx: typer.Context,
    file_id: str = typer.Argument(..., help="Provider file id."),
    service: str = typer.Option(..., "--service", "-s", help="Provider name. AnonFilesNew supports info."),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="Provider API key."),
    api_key_env: Optional[str] = typer.Option(None, "--api-key-env", help="Environment variable that contains the API key."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
):
    """Fetch provider file metadata."""
    _print_banner(ctx, json_output)
    try:
        require_value(service, file_id, "Provide the provider file id.", "file_id_required")
        result = FileUploaderCore().info(
            service,
            file_id,
            api_key=_resolve_api_key(api_key, api_key_env),
            api_key_env=api_key_env,
        )
    except ProviderError as error:
        _exit_provider_error(error, json_output)
        return
    _print_result(result, json_output)


def main():
    app()
