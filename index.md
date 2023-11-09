<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>FileUploader</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
  <style>
    

  </style>
</head>
<body>
  <h1>FileUploader</h1>

  <p>Automate Anonymous File Uploads and Downloads</p>

  <details open>
    <summary><h2>Overview</h2></summary>
    <p>FileUploader is a Python script that simplifies the process of uploading files to various file-hosting services, including Anonfiles, Bayfiles (Deprecated), and GoFile. This script streamlines the file upload process and provides you with direct download links, making it convenient for sharing files.</p>
    <p><strong>Note: Anonfiles and Bayfiles are Deprecated. Please consider using the GoFile option for a more reliable service.</strong></p>
  </details>

  <details open>
    <summary><h2>Usage</h2></summary>
    <details>
      <summary><h3>FileUploader</h3></summary>
      <details>
        <summary><h4>Windows</h4></summary>
        <h4>Installation</h4>
        <p>You can install by executing <code>fileuploader_setup.exe</code> and follow the steps.</p>
        <h4>Usage</h4>
        <p><strong>Python File</strong></p>
        <pre><code>python3 fileUploader.py</code></pre>
        <p><strong>Exe File</strong></p>
        <pre><code>start fileUploader.exe</code></pre>
        <p><strong>Right Click to File</strong></p>
        <img src="imagen-de-asdasdadas-en-contexto-de-menu-de-archivo" alt="Right Click to File">
      </details>
      <details>
        <summary><h4>Linux</h4></summary>
        <h4>Installation</h4>
        <p>You can install by executing <code>fileuploader_setup.sh</code>.</p>
        <h4>Permissions</h4>
        <p><strong>Python File</strong></p>
        <pre><code>chmod +x fileUploader.py</code></pre>
        <p><strong>Binary File</strong></p>
        <pre><code>chmod +x fileUploader</code></pre>
        <h4>Usage</h4>
        <p><strong>Python File</strong></p>
        <pre><code>python3 fileUploader.py</code></pre>
        <p><strong>Binary File</strong></p>
        <pre><code>./fileUploader</code></pre>
      </details>
    </details>
  </details>

  <details open>
    <summary><h3>GoFile</h3></summary>
    <details>
      <summary><h4>Windows</h4></summary>
      <h4>Installation</h4>
      <p>You can install by executing <code>gofile_setup.exe</code> and follow the steps.</p>
      <details>
        <summary><h4>Usage</h4></summary>
        <p>Run the program from the command line with the following options:</p>
        <h4>Options:</h4>
        <ul>
          <li><code>-v</code>, <code>--verbose</code>: Enable verbose mode to display detailed information during execution.</li>
          <li><code>-d, --download-url &lt;url&gt;</code>: Download a file by providing the URL.</li>
          <li><code>-s, --download &lt;server&gt; &lt;fileId&gt; &lt;fileName&gt;</code>: Download a file by specifying the server, fileId, and fileName.</li>
          <li><code>-u, --upload &lt;filepath&gt;</code>: Upload a file from a local path.</li>
          <li><code>--json</code>: Return data in JSON format.</li>
          <li><code>--xml</code>: Return data in XML format.</li>
          <li><code>--plaintext</code>: Return data in plain text format.</li>
          <li><code>-o, --output &lt;output-file&gt;</code>: Save the processed data to a file with the specified name.</li>
        </ul>
        <h4>Examples:</h4>
        <p>Upload a file:</p>
        <pre><code>python gofile.py -u file.txt</code></pre>
        <p>Download a file by URL:</p>
        <pre><code>python gofile.py -d https://store5.gofile.io/download/fcd000f4-73d1-4966-8c56-20496efd150a/text.txt</code></pre>
        <p>Download a file by server, fileId, and fileName:</p>
        <pre><code>python gofile.py -s store5 fcd000f4-73d1-4966-8c56-20496efd150a file.txt</code></pre>
        <h3>Output Format</h3>
        <p>The program can return data in JSON, XML, or plain text format. If no format is specified, it defaults to plain text format.</p>
        <h4>XML</h4>
        <pre><code><?xml version="1.0" encoding="UTF-8" ?>
<uploadedFile>
  <status>ok</status>
  <data>
    <guestToken>uT0xLP89WVxbjMQVM1iDh5nC5b0ANORa</guestToken>
    <downloadPage>https://gofile.io/d/5Zisuc</downloadPage>
    <c0de>5Zisuc</c0de>
    <parentFolder>10ea022d-a43a-4faf-bcae-2889c7a48e8a</parentFolder>
    <fileId>fcd000f4-73d1-4966-8c56-20496efd150a</fileId>
    <fileName>text.txt</fileName>
    <md5>89da2808465ff4b8a18e192ba873c458</md5>
    <server>store11</server>
  </data>
</uploadedFile></code></pre>
        <h4>JSON</h4>
        <pre><code>{
  "status": "ok",
  "data": {
    "guestToken": "UJlzsi3EdfdUmr5SlimWPKZn7x8ifJM5",
    "downloadPage": "https://gofile.io/d/BPWAu8",
    "code": "BPWAu8",
    "parentFolder": "ab6f7927-5c19-4ab9-a83a-e4ae3db095e2",
    "fileId": "6cc4e899-92bc-4b3a-af13-442254b9c105",
    "fileName": "text.txt",
    "md5": "89da2808465ff4b8a18e192ba873c458",
    "server": "store8"
  }
}</code></pre>
        <h4>PLAINTEXT</h4>
        <pre><code>status          : ok
data :
    guestToken      : OUWgISULaTNl42Tr5tc8UIiI1Zl8iwY8
    downloadPage    : https://gofile.io/d/TEza0q
    code            : TEza0q
    parentFolder    : a1d87e71-f2c0-43e2-974d-a24e8d587bc6
    fileId          : 0ec70f4d-4ae6-4449-8674-91af5909fb42
    fileName        : text.txt
    md5             : 89da2808465ff4b8a18e192ba873c458
    server          : store8</code></pre>
      </details>
    </details>
  </details>
  <details open>
    <summary><h3>AnonFiles (DEPRECATED)</h3></summary>
    <p>Description of AnonFiles</p>
    <details>
      <summary><h4>Windows</h4></summary>
      <h4>Installation</h4>
      <p>You can install by executing <code>anonfiles_setup.exe</code> and follow the steps.</p>
      <details>
        <summary><h4>Usage</h4></summary>
        <p><strong>Python File</strong></p>
        <pre><code>python3 anonFiles.py</code></pre>
        <p><strong>Exe File</strong></p>
        <pre><code>start anonFiles.exe</code></pre>
        <p><strong>Right Click to File</strong></p>
        <img src="imagen-de-asdasdadas-in-the-context-of-the-file-menu" alt="Right Click to File">
      </details>
    </details>
    <details>
      <summary><h4>Linux</h4></summary>
      <h4>Installation</h4>
      <p>You can install by executing <code>anonfiles_setup.sh</code>.</p>
      <details>
        <summary><h4>Permissions</h4></summary>
        <p><strong>Python File</strong></p>
        <pre><code>chmod +x anonFiles.py</code></pre>
        <p><strong>Binary File</strong></p>
        <pre><code>chmod +x anonFiles</code></pre>
      </details>
      <details>
        <summary><h4>Usage</h4></summary>
        <p><strong>Python File</strong></p>
        <pre><code>python3 anonFiles.py</code></pre>
        <p><strong>Binary File</strong></p>
        <pre><code>./anonFiles</code></pre>
      </details>
    </details>
  </details>
  <details>
    <summary><h3>BayFiles (DEPRECATED)</h3></summary>
    <p>Description of BayFiles</p>
    <details>
      <summary><h4>Windows</h4></summary>
      <h4>Installation</h4>
      <p>You can install by executing <code>bayfiles_setup.exe</code> and follow the steps.</p>
      <details>
        <summary><h4>Usage</h4></summary>
        <p><strong>Python File</strong></p>
        <pre><code>python3 bayfiles.py</code></pre>
        <p><strong>Exe File</strong></p>
        <pre><code>start bayfiles.exe</code></pre>
        <p><strong>Right Click to File</strong></p>
        <img src="imagen-de-asdasdadas-in-the-context-of-the-file-menu" alt="Right Click to File">
      </details>
    </details>
    <details>
      <summary><h4>Linux</h4></summary>
      <h4>Installation</h4>
      <p>You can install by executing <code>bayfiles_setup.sh</code>.</p>
      <details>
        <summary><h4>Permissions</h4></summary>
        <p><strong>Python File</strong></p>
        <pre><code>chmod +x bayfiles.py</code></pre>
        <p><strong>Binary File</strong></p>
        <pre><code>chmod +x bayfiles</code></pre>
      </details>
      <details>
        <summary><h4>Usage</h4></summary>
        <p><strong>Python File</strong></p>
        <pre><code>python3 bayfiles.py</code></pre>
        <p><strong>Binary File</strong></p>
        <pre><code>./bayfiles</code></pre>
      </details>
    </details>
  </details>
</body>
</html>
