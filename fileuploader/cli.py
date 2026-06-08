import os
from typing import Optional

import typer

from .clipboard import copy_text
from .core import FileUploaderCore
from .formatting import format_output, service_rows
from .models import ProviderError
from .validation import require_value


app = typer.Typer(
    help="Upload files with GoFile, AnonFilesNew, JSONBin, AnonFiles, or BayFiles.",
    no_args_is_help=True,
)


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


@app.command()
def services(
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
    include_deprecated: bool = typer.Option(True, "--include-deprecated/--active-only", help="Include deprecated providers."),
):
    """List available providers."""
    result = FileUploaderCore().services(include_deprecated=include_deprecated)
    services_data = [service.to_dict() for service in result]
    typer.echo(format_output(services_data, json_output=True) if json_output else service_rows(services_data))


@app.command()
def upload(
    path: str = typer.Argument(..., help="File path to upload, for example ./document.pdf."),
    service: str = typer.Option(..., "--service", "-s", help="Provider name. Run `services` to list choices."),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="Provider API key. Prefer --api-key-env for repeat use."),
    api_key_env: Optional[str] = typer.Option(None, "--api-key-env", help="Environment variable that contains the API key."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
    plaintext: bool = typer.Option(False, "--plaintext", help="Print plaintext output."),
    copy: bool = typer.Option(False, "--copy", help="Copy output to clipboard."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
):
    """Upload a file with a provider."""
    try:
        require_value(service, path, "Provide a file path to upload.", "path_required")
        result = FileUploaderCore().upload(
            service,
            path,
            api_key=_resolve_api_key(api_key, api_key_env),
            api_key_env=api_key_env,
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
    service: str = typer.Option(..., "--service", "-s", help="Provider name. GoFile supports download metadata."),
    url: Optional[str] = typer.Option(None, "--url", help="Direct download URL."),
    server: Optional[str] = typer.Option(None, "--server", help="Provider server."),
    file_id: Optional[str] = typer.Option(None, "--file-id", help="Provider file id."),
    filename: Optional[str] = typer.Option(None, "--filename", help="Provider filename."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
):
    """Download or fetch download metadata."""
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
    file_id: str = typer.Argument(..., help="Provider file id."),
    service: str = typer.Option(..., "--service", "-s", help="Provider name. AnonFilesNew supports info."),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="Provider API key."),
    api_key_env: Optional[str] = typer.Option(None, "--api-key-env", help="Environment variable that contains the API key."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
):
    """Fetch provider file metadata."""
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
