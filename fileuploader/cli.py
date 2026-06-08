import os
from typing import Optional

import typer

from .core import FileUploaderCore
from .formatting import format_output
from .models import ProviderError


app = typer.Typer(help="Unified file uploader for supported hosting providers.")


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
    _print_result([service.to_dict() for service in result], json_output)


@app.command()
def upload(
    path: str = typer.Argument(..., help="File path to upload."),
    service: str = typer.Option(..., "--service", "-s", help="Provider name."),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="Provider API key."),
    api_key_env: Optional[str] = typer.Option(None, "--api-key-env", help="Environment variable that contains the API key."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
    plaintext: bool = typer.Option(False, "--plaintext", help="Print plaintext output."),
    copy: bool = typer.Option(False, "--copy", help="Copy output to clipboard."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
):
    """Upload a file with a provider."""
    try:
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
        typer.echo("Clipboard copy is available in the GoFile legacy command and GUI.")


@app.command()
def download(
    service: str = typer.Option(..., "--service", "-s", help="Provider name."),
    url: Optional[str] = typer.Option(None, "--url", help="Direct download URL."),
    server: Optional[str] = typer.Option(None, "--server", help="Provider server."),
    file_id: Optional[str] = typer.Option(None, "--file-id", help="Provider file id."),
    filename: Optional[str] = typer.Option(None, "--filename", help="Provider filename."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
):
    """Download or fetch download metadata."""
    try:
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
    service: str = typer.Option(..., "--service", "-s", help="Provider name."),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="Provider API key."),
    api_key_env: Optional[str] = typer.Option(None, "--api-key-env", help="Environment variable that contains the API key."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
):
    """Fetch provider file metadata."""
    try:
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
