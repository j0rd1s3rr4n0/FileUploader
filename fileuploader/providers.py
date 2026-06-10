import base64
import hashlib
import json
import os
import time
import uuid
from pathlib import Path

import requests

from .models import ProviderError, ProviderInfo, UploadResult


class BaseProvider:
    info = ProviderInfo(name="base", display_name="Base")

    def __init__(self, http_client=None):
        self.http = http_client or requests

    def upload(self, filepath, **options):
        raise ProviderError(self.info.name, "Upload is not supported by this provider")

    def download(self, **options):
        raise ProviderError(self.info.name, "Download is not supported by this provider")

    def info_file(self, file_id, **options):
        raise ProviderError(self.info.name, "File info is not supported by this provider")

    def _ensure_file(self, filepath):
        path = Path(filepath)
        if not path.is_file():
            raise ProviderError(self.info.name, f"File not found: {filepath}", code="file_not_found")
        return path

    def _api_key(self, options, default_env_name, label="API key"):
        api_key = options.get("api_key") or os.environ.get(options.get("api_key_env") or default_env_name)
        if not api_key:
            raise ProviderError(self.info.name, f"Provide a {label}", code="api_key_required")
        return api_key

    def _post_file(self, url, filepath, file_field="file", **kwargs):
        path = self._ensure_file(filepath)
        try:
            with path.open("rb") as file_handle:
                response = self.http.post(url, files={file_field: (path.name, file_handle)}, **kwargs)
        except requests.RequestException as exc:
            raise ProviderError(self.info.name, str(exc), code="network_error") from exc
        return self._json_response(response)

    def _post_file_text(self, url, filepath, file_field="file", **kwargs):
        path = self._ensure_file(filepath)
        try:
            with path.open("rb") as file_handle:
                response = self.http.post(url, files={file_field: (path.name, file_handle)}, **kwargs)
        except requests.RequestException as exc:
            raise ProviderError(self.info.name, str(exc), code="network_error") from exc
        return self._text_response(response)

    def _put_file_text(self, url, filepath, **kwargs):
        path = self._ensure_file(filepath)
        try:
            with path.open("rb") as file_handle:
                response = self.http.put(url, data=file_handle, **kwargs)
        except requests.RequestException as exc:
            raise ProviderError(self.info.name, str(exc), code="network_error") from exc
        return self._text_response(response)

    def _json_response(self, response):
        try:
            payload = response.json()
        except ValueError as exc:
            raise ProviderError(self.info.name, "Provider returned invalid JSON", code="invalid_json") from exc
        if getattr(response, "status_code", 200) >= 400:
            message = payload.get("message") or payload.get("error", {}).get("message") or response.text
            raise ProviderError(self.info.name, message, code="http_error")
        return payload

    def _text_response(self, response):
        text = getattr(response, "text", "").strip()
        if getattr(response, "status_code", 200) >= 400:
            raise ProviderError(self.info.name, text or "Provider returned an HTTP error", code="http_error")
        if not text:
            raise ProviderError(self.info.name, "Provider returned an empty response", code="empty_response")
        return text


class GoFileProvider(BaseProvider):
    info = ProviderInfo(
        name="gofile",
        display_name="GoFile",
        supports_download=True,
        supports_info=False,
    )

    def upload(self, filepath, **options):
        payload = self._post_file("https://upload.gofile.io/uploadfile", filepath)
        if payload.get("status") not in ("ok", True):
            raise ProviderError(self.info.name, str(payload), code="upload_failed")
        data = payload.get("data", {})
        return UploadResult(
            provider=self.info.name,
            status=True,
            url=data.get("downloadPage"),
            file_id=data.get("fileId") or data.get("id") or data.get("code") or data.get("parentFolderCode"),
            metadata=data,
            raw=payload,
        )

    def download(self, **options):
        url = options.get("url")
        if not url:
            server = options.get("server")
            file_id = options.get("file_id")
            filename = options.get("filename")
            if not all([server, file_id, filename]):
                raise ProviderError(self.info.name, "Provide url or server, file_id, and filename")
            url = f"https://{server}.gofile.io/download/{file_id}/{filename}"
        try:
            response = self.http.get(url)
        except requests.RequestException as exc:
            raise ProviderError(self.info.name, str(exc), code="network_error") from exc
        return self._json_response(response)


class AnonFilesNewProvider(BaseProvider):
    info = ProviderInfo(
        name="anonfilesnew",
        display_name="AnonFilesNew",
        supports_info=True,
        requires_api_key=True,
    )

    def upload(self, filepath, **options):
        api_key = options.get("api_key") or os.environ.get(options.get("api_key_env") or "ANONFILESNEW_API_KEY")
        url = "https://api.anonfilesnew.com/upload"
        if api_key:
            url = f"{url}?key={api_key}"
        payload = self._post_file(url, filepath)
        if not payload.get("status"):
            error = payload.get("error", {})
            raise ProviderError(self.info.name, error.get("message", "Upload failed"), code=error.get("type"))
        file_data = payload.get("data", {}).get("file", {})
        url_data = file_data.get("url", {})
        metadata = file_data.get("metadata", {})
        return UploadResult(
            provider=self.info.name,
            status=True,
            url=url_data.get("full"),
            short_url=url_data.get("short"),
            file_id=metadata.get("id"),
            metadata=metadata,
            raw=payload,
        )

    def info_file(self, file_id, **options):
        try:
            response = self.http.get(f"https://api.anonfilesnew.com/v3/file/{file_id}/info")
        except requests.RequestException as exc:
            raise ProviderError(self.info.name, str(exc), code="network_error") from exc
        return self._json_response(response)


class JsonBinProvider(BaseProvider):
    info = ProviderInfo(
        name="jsonbin",
        display_name="JSONBin",
        supports_download=False,
        supports_info=False,
        requires_api_key=True,
    )

    def upload(self, filepath, **options):
        path = self._ensure_file(filepath)
        api_key = options.get("api_key") or os.environ.get(options.get("api_key_env") or "JSONBIN_API_KEYS")
        if api_key and "," in api_key:
            api_key = api_key.split(",", 1)[0].strip()
        if not api_key:
            raise ProviderError(self.info.name, "Provide a JSONBin API key", code="api_key_required")

        data = path.read_bytes()
        record = {
            "upload_id": str(uuid.uuid4()),
            "original_filename": path.name,
            "file_size": len(data),
            "file_sha256": hashlib.sha256(data).hexdigest(),
            "uploaded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "content_encoding": "base64",
            "content": base64.b64encode(data).decode("ascii"),
        }
        headers = {
            "Content-Type": "application/json",
            "X-Master-Key": api_key,
            "X-Bin-Private": "true",
            "X-Bin-Name": path.name[:128],
        }
        try:
            response = self.http.post("https://api.jsonbin.io/v3/b", headers=headers, json=record, timeout=60)
        except requests.RequestException as exc:
            raise ProviderError(self.info.name, str(exc), code="network_error") from exc
        payload = self._json_response(response)
        metadata = payload.get("metadata", {})
        return UploadResult(
            provider=self.info.name,
            status=True,
            url=metadata.get("id"),
            file_id=metadata.get("id"),
            metadata=metadata,
            raw=payload,
        )


class ZeroXZeroProvider(BaseProvider):
    info = ProviderInfo(
        name="0x0",
        display_name="0x0.st",
        supports_info=False,
    )

    def upload(self, filepath, **options):
        url = self._post_file_text("https://0x0.st", filepath)
        return UploadResult(provider=self.info.name, status=True, url=url, raw={"response": url})


class MoonPushProvider(BaseProvider):
    info = ProviderInfo(
        name="moonpush",
        display_name="MoonPush",
        supports_info=True,
    )

    def upload(self, filepath, **options):
        payload = self._post_file("https://www.moonpush.com/api/upload", filepath)
        url = payload.get("shareUrl") or payload.get("share_url") or payload.get("url")
        download_url = payload.get("downloadUrl") or payload.get("download_url")
        file_id = payload.get("id") or payload.get("pipeId") or payload.get("fileId")
        if not url and not download_url:
            raise ProviderError(self.info.name, "Upload response did not include a URL", code="missing_url")
        return UploadResult(
            provider=self.info.name,
            status=True,
            url=url or download_url,
            short_url=download_url if url and download_url != url else None,
            file_id=file_id,
            metadata=payload,
            raw=payload,
        )

    def info_file(self, file_id, **options):
        try:
            response = self.http.get(f"https://www.moonpush.com/api/share/{file_id}")
        except requests.RequestException as exc:
            raise ProviderError(self.info.name, str(exc), code="network_error") from exc
        return self._json_response(response)


class TempShProvider(BaseProvider):
    info = ProviderInfo(
        name="tempsh",
        display_name="Temp.sh",
        supports_info=False,
    )

    def upload(self, filepath, **options):
        url = self._post_file_text("https://temp.sh/upload", filepath)
        return UploadResult(provider=self.info.name, status=True, url=url, raw={"response": url})


class TmpFileLinkProvider(BaseProvider):
    info = ProviderInfo(
        name="tmpfilelink",
        display_name="tmpfile.link",
        supports_info=False,
    )

    def upload(self, filepath, **options):
        payload = self._post_file("https://tmpfile.link/api/upload", filepath)
        url = payload.get("downloadLink") or payload.get("download_link") or payload.get("url")
        if not url:
            raise ProviderError(self.info.name, "Upload response did not include a download link", code="missing_url")
        return UploadResult(
            provider=self.info.name,
            status=True,
            url=url,
            short_url=payload.get("downloadLinkEncoded"),
            file_id=payload.get("fileId") or payload.get("id"),
            metadata=payload,
            raw=payload,
        )


class BlipbinProvider(BaseProvider):
    info = ProviderInfo(
        name="blipbin",
        display_name="blipbin",
        supports_info=False,
    )

    def upload(self, filepath, **options):
        path = self._ensure_file(filepath)
        try:
            with path.open("rb") as file_handle:
                response = self.http.post("https://blipbin.com/upload", files={"file": (path.name, file_handle)})
        except requests.RequestException as exc:
            raise ProviderError(self.info.name, str(exc), code="network_error") from exc
        url = self._text_response(response)
        token = getattr(response, "headers", {}).get("X-Token")
        metadata = {"delete_token": token} if token else {}
        return UploadResult(provider=self.info.name, status=True, url=url, metadata=metadata, raw={"response": url})


class EasySendProvider(BaseProvider):
    info = ProviderInfo(
        name="easysend",
        display_name="EasySend",
        supports_info=False,
    )

    def upload(self, filepath, **options):
        payload = self._post_file("https://easysend.co/api/v1/upload", filepath, file_field="files[]")
        url = payload.get("share_url") or payload.get("shareUrl")
        short_code = payload.get("short_code") or payload.get("shortCode")
        if not url and short_code:
            url = f"https://easysend.co/{short_code}"
        elif url and url.startswith("/"):
            url = f"https://easysend.co{url}"
        if not url:
            raise ProviderError(self.info.name, "Upload response did not include a share URL", code="missing_url")
        return UploadResult(
            provider=self.info.name,
            status=True,
            url=url,
            file_id=short_code,
            metadata=payload,
            raw=payload,
        )


class DropFileDevProvider(BaseProvider):
    info = ProviderInfo(
        name="dropfiledev",
        display_name="dropfile.dev",
        supports_info=False,
    )

    def upload(self, filepath, **options):
        path = self._ensure_file(filepath)
        url = self._put_file_text(f"https://dropfile.dev/{path.name}", path)
        return UploadResult(provider=self.info.name, status=True, url=url, raw={"response": url})


class CuploadProvider(BaseProvider):
    info = ProviderInfo(
        name="cupload",
        display_name="cupload.io",
        supports_info=False,
    )

    def upload(self, filepath, **options):
        path = self._ensure_file(filepath)
        url = self._put_file_text(f"https://cupload.io/{path.name}", path)
        return UploadResult(provider=self.info.name, status=True, url=url, raw={"response": url})


class QurlProvider(BaseProvider):
    info = ProviderInfo(
        name="qurl",
        display_name="qurl.sh",
        supports_info=False,
    )

    def upload(self, filepath, **options):
        path = self._ensure_file(filepath)
        url = self._put_file_text(f"https://qurl.sh/{path.name}", path)
        return UploadResult(provider=self.info.name, status=True, url=url, raw={"response": url})


class FileIoProvider(BaseProvider):
    info = ProviderInfo(
        name="fileio",
        display_name="file.io",
        supports_info=False,
    )

    def upload(self, filepath, **options):
        payload = self._post_file("https://file.io", filepath)
        if payload.get("success") is False:
            raise ProviderError(self.info.name, payload.get("message", "Upload failed"), code=payload.get("error"))
        url = payload.get("link") or payload.get("url")
        if not url:
            raise ProviderError(self.info.name, "Upload response did not include a link", code="missing_url")
        return UploadResult(
            provider=self.info.name,
            status=True,
            url=url,
            file_id=payload.get("key") or payload.get("id"),
            metadata=payload,
            raw=payload,
        )


class UguuProvider(BaseProvider):
    info = ProviderInfo(
        name="uguu",
        display_name="Uguu",
        supports_info=False,
    )

    def upload(self, filepath, **options):
        payload = self._post_file("https://uguu.se/upload.php", filepath, file_field="files[]")
        if payload.get("success") is False:
            raise ProviderError(self.info.name, payload.get("description", "Upload failed"), code=payload.get("errorcode"))
        files = payload.get("files") or []
        file_data = files[0] if files else payload
        url = file_data.get("url")
        if not url:
            raise ProviderError(self.info.name, "Upload response did not include a URL", code="missing_url")
        return UploadResult(
            provider=self.info.name,
            status=True,
            url=url,
            file_id=file_data.get("hash"),
            metadata=file_data,
            raw=payload,
        )


class CatboxProvider(BaseProvider):
    info = ProviderInfo(
        name="catbox",
        display_name="Catbox",
        supports_info=False,
    )

    def upload(self, filepath, **options):
        path = self._ensure_file(filepath)
        try:
            with path.open("rb") as file_handle:
                response = self.http.post(
                    "https://catbox.moe/user/api.php",
                    data={"reqtype": "fileupload"},
                    files={"fileToUpload": (path.name, file_handle)},
                )
        except requests.RequestException as exc:
            raise ProviderError(self.info.name, str(exc), code="network_error") from exc
        url = self._text_response(response)
        return UploadResult(provider=self.info.name, status=True, url=url, raw={"response": url})


class LitterboxProvider(BaseProvider):
    info = ProviderInfo(
        name="litterbox",
        display_name="Litterbox",
        supports_info=False,
    )

    def upload(self, filepath, **options):
        path = self._ensure_file(filepath)
        ttl = options.get("ttl") or options.get("time") or "1h"
        try:
            with path.open("rb") as file_handle:
                response = self.http.post(
                    "https://litterbox.catbox.moe/resources/internals/api.php",
                    data={"reqtype": "fileupload", "time": ttl},
                    files={"fileToUpload": (path.name, file_handle)},
                )
        except requests.RequestException as exc:
            raise ProviderError(self.info.name, str(exc), code="network_error") from exc
        url = self._text_response(response)
        return UploadResult(provider=self.info.name, status=True, url=url, metadata={"ttl": ttl}, raw={"response": url})


class TransferShProvider(BaseProvider):
    info = ProviderInfo(
        name="transfersh",
        display_name="transfer.sh",
        supports_info=False,
    )

    def upload(self, filepath, **options):
        path = self._ensure_file(filepath)
        url = self._put_file_text(f"https://transfer.sh/{path.name}", path)
        return UploadResult(provider=self.info.name, status=True, url=url, raw={"response": url})


class FourSharedProvider(BaseProvider):
    info = ProviderInfo(
        name="4shared",
        display_name="4shared",
        supports_download=False,
        supports_info=True,
        requires_api_key=True,
    )

    def _oauth_params(self, options):
        oauth_params = self._api_key(options, "FOURSHARED_OAUTH_PARAMS", "4shared OAuth query parameters")
        return oauth_params.lstrip("?")

    def upload(self, filepath, **options):
        path = self._ensure_file(filepath)
        oauth_params = self._oauth_params(options)
        folder_id = options.get("folder_id") or "0"
        params = {"folderId": folder_id, "fileName": path.name}
        url = f"https://upload.4shared.com/v1_2/files?{oauth_params}"
        try:
            with path.open("rb") as file_handle:
                response = self.http.post(
                    url,
                    params=params,
                    headers={"Content-Type": "application/octet-stream"},
                    data=file_handle,
                )
        except requests.RequestException as exc:
            raise ProviderError(self.info.name, str(exc), code="network_error") from exc
        payload = self._json_response(response)
        return UploadResult(
            provider=self.info.name,
            status=True,
            url=payload.get("downloadPage") or payload.get("url"),
            file_id=payload.get("id"),
            metadata=payload,
            raw=payload,
        )

    def info_file(self, file_id, **options):
        oauth_params = self._oauth_params(options)
        try:
            response = self.http.get(f"https://api.4shared.com/v1_2/files/{file_id}?{oauth_params}")
        except requests.RequestException as exc:
            raise ProviderError(self.info.name, str(exc), code="network_error") from exc
        return self._json_response(response)


class BoxProvider(BaseProvider):
    info = ProviderInfo(
        name="box",
        display_name="Box",
        supports_download=False,
        supports_info=True,
        requires_api_key=True,
    )

    def upload(self, filepath, **options):
        path = self._ensure_file(filepath)
        access_token = self._api_key(options, "BOX_ACCESS_TOKEN", "Box OAuth access token")
        folder_id = options.get("folder_id") or "0"
        attributes = {"name": path.name, "parent": {"id": str(folder_id)}}
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            with path.open("rb") as file_handle:
                response = self.http.post(
                    "https://upload.box.com/api/2.0/files/content",
                    headers=headers,
                    files=[
                        ("attributes", (None, json.dumps(attributes), "application/json")),
                        ("file", (path.name, file_handle, "application/octet-stream")),
                    ],
                )
        except requests.RequestException as exc:
            raise ProviderError(self.info.name, str(exc), code="network_error") from exc
        payload = self._json_response(response)
        entries = payload.get("entries") or []
        file_data = entries[0] if entries else payload
        file_id = file_data.get("id")
        url = file_data.get("shared_link", {}).get("url") or file_data.get("url")
        return UploadResult(
            provider=self.info.name,
            status=True,
            url=url,
            file_id=file_id,
            metadata=file_data,
            raw=payload,
        )

    def info_file(self, file_id, **options):
        access_token = self._api_key(options, "BOX_ACCESS_TOKEN", "Box OAuth access token")
        try:
            response = self.http.get(
                f"https://api.box.com/2.0/files/{file_id}",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        except requests.RequestException as exc:
            raise ProviderError(self.info.name, str(exc), code="network_error") from exc
        return self._json_response(response)


class DropboxProvider(BaseProvider):
    info = ProviderInfo(
        name="dropbox",
        display_name="Dropbox",
        supports_download=False,
        supports_info=True,
        requires_api_key=True,
    )

    def upload(self, filepath, **options):
        path = self._ensure_file(filepath)
        access_token = self._api_key(options, "DROPBOX_ACCESS_TOKEN", "Dropbox OAuth access token")
        dropbox_path = options.get("dropbox_path") or f"/{path.name}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/octet-stream",
            "Dropbox-API-Arg": json.dumps({"path": dropbox_path, "mode": "add", "autorename": True, "mute": False}),
        }
        try:
            with path.open("rb") as file_handle:
                response = self.http.post("https://content.dropboxapi.com/2/files/upload", headers=headers, data=file_handle)
        except requests.RequestException as exc:
            raise ProviderError(self.info.name, str(exc), code="network_error") from exc
        payload = self._json_response(response)
        return UploadResult(
            provider=self.info.name,
            status=True,
            url=payload.get("path_display"),
            file_id=payload.get("id"),
            metadata=payload,
            raw=payload,
        )

    def info_file(self, file_id, **options):
        access_token = self._api_key(options, "DROPBOX_ACCESS_TOKEN", "Dropbox OAuth access token")
        try:
            response = self.http.post(
                "https://api.dropboxapi.com/2/files/get_metadata",
                headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
                json={"path": file_id},
            )
        except requests.RequestException as exc:
            raise ProviderError(self.info.name, str(exc), code="network_error") from exc
        return self._json_response(response)


class MediaFireProvider(BaseProvider):
    info = ProviderInfo(
        name="mediafire",
        display_name="MediaFire",
        supports_download=False,
        supports_info=False,
        requires_api_key=True,
    )

    def upload(self, filepath, **options):
        path = self._ensure_file(filepath)
        session_token = self._api_key(options, "MEDIAFIRE_SESSION_TOKEN", "MediaFire session token")
        try:
            with path.open("rb") as file_handle:
                response = self.http.post(
                    "https://www.mediafire.com/api/1.5/upload/simple.php",
                    params={"session_token": session_token, "response_format": "json"},
                    headers={"x-filename": path.name, "x-filesize": str(path.stat().st_size)},
                    data=file_handle,
                )
        except requests.RequestException as exc:
            raise ProviderError(self.info.name, str(exc), code="network_error") from exc
        payload = self._json_response(response)
        response_data = payload.get("response", payload)
        upload_data = response_data.get("doupload", response_data.get("upload", response_data))
        file_id = upload_data.get("quickkey") or upload_data.get("key") or upload_data.get("upload_key")
        url = upload_data.get("normal_download") or upload_data.get("link") or upload_data.get("url")
        return UploadResult(
            provider=self.info.name,
            status=True,
            url=url,
            file_id=file_id,
            metadata=upload_data,
            raw=payload,
        )


class MegaProvider(BaseProvider):
    info = ProviderInfo(
        name="mega",
        display_name="MEGA",
        active=False,
        supports_upload=False,
        supports_download=False,
        supports_info=False,
        requires_api_key=True,
    )

    def upload(self, filepath, **options):
        raise ProviderError(
            self.info.name,
            "MEGA uploads require MEGAcmd or an SDK-backed implementation; this provider is listed but disabled.",
            code="provider_disabled",
        )


class AnonFilesProvider(AnonFilesNewProvider):
    info = ProviderInfo(
        name="anonfiles",
        display_name="AnonFiles",
        supports_info=False,
        deprecated=True,
    )

    def upload(self, filepath, **options):
        payload = self._post_file("https://api.anonfiles.com/upload", filepath)
        if not payload.get("status"):
            error = payload.get("error", {})
            raise ProviderError(self.info.name, error.get("message", "Upload failed"), code=error.get("type"))
        file_data = payload.get("data", {}).get("file", {})
        url_data = file_data.get("url", {})
        metadata = file_data.get("metadata", {})
        return UploadResult(
            provider=self.info.name,
            status=True,
            url=url_data.get("full"),
            short_url=url_data.get("short"),
            file_id=metadata.get("id"),
            metadata=metadata,
            raw=payload,
        )


class BayFilesProvider(AnonFilesProvider):
    info = ProviderInfo(
        name="bayfiles",
        display_name="BayFiles",
        supports_info=False,
        deprecated=True,
    )

    def upload(self, filepath, **options):
        payload = self._post_file("https://api.bayfiles.com/upload", filepath)
        if not payload.get("status"):
            error = payload.get("error", {})
            raise ProviderError(self.info.name, error.get("message", "Upload failed"), code=error.get("type"))
        file_data = payload.get("data", {}).get("file", {})
        url_data = file_data.get("url", {})
        metadata = file_data.get("metadata", {})
        return UploadResult(
            provider=self.info.name,
            status=True,
            url=url_data.get("full"),
            short_url=url_data.get("short"),
            file_id=metadata.get("id"),
            metadata=metadata,
            raw=payload,
        )
