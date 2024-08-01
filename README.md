<!--meta http-equiv="refresh" content="0; URL=/index"-->
# FileUploader

Automate Anonymous File Uploads and Downloads

<details open>
<summary><h2>Overview</h2></summary>

FileUploader is a Python script that simplifies the process of uploading files to various file-hosting services, including Anonfiles, Bayfiles (Deprecated), and GoFile. This script streamlines the file upload process and provides you with direct download links, making it convenient for sharing files.

**Note: Anonfiles and Bayfiles are Deprecated. Please consider using the GoFile option for a more reliable service.**

</details>

<details open>
<summary><h2>Usage</h2></summary>

<details>
<summary><h4>FileUploader</h4></summary>
All in One file uploaders at one.

<details>
<summary>Windows</summary>

##### Installation

You can install executing fileuplaoder_setup.exe and follow the steps.

<details>
<summary>Usage</summary>

**Python File**

```shell
python3 fileUploader.py
```

**Exe File**

```shell
start fileUploader.exe
```

**Right Click to File**
![Adjuntar Imagen](imagen de asdasdadas en contexto de menu de archivo)

</details>

</details>

<details>
<summary>Linux</summary>

##### Installation

You can install executing fileuplaoder_setup.sh.

<details>
<summary>Permissions</summary>

**Python File**

```shell
chmod +x fileUploader.py
```

**Binary File**

```shell
chmod +x  fileUploader
```

</details>

<details>
<summary>Usage</summary>

**Python File**

```shell
python3 fileUploader.py
```

**Binary File**

```shell
./fileUploader
```

</details>

</details>
</details>

<details open>
  <summary><h4>GoFile</h4></summary>

GoFile.io File Uploader and Downloader

<detailsopen>
<summary>Windows</summary>

##### Installation

You can install executing gofile_setup.exe and follow the steps.

<detailsopen>
<summary>Usage</summary>
<p>Run the program from the command line with the following options:</p>

  <h3>Options:</h3>
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
<h3>Examples:</h3>
  
Upload a file:
<code>python gofile.py -u file.txt</code>

Download a file by URL:
<code>python gofile.py -d https://store5.gofile.io/download/fcd000f4-73d1-4966-8c56-20496efd150a/text.txt</code>

Download a file by server, fileId, and fileName:
<code>python gofile.py -s store5 fcd000f4-73d1-4966-8c56-20496efd150a file.txt</code>
  <h2>Output Format</h2>
  <p>The program can return data in JSON, XML, or plain text format. If no format is specified, it defaults to plain text format.</p>

**XML**  
```xml
<?xml version="1.0" encoding="UTF-8" ?>
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
</uploadedFile>
```

**JSON***
```json
{
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
}
```
**PLAINTEXT**
```css
status          : ok
data :
    guestToken      : OUWgISULaTNl42Tr5tc8UIiI1Zl8iwY8
    downloadPage    : https://gofile.io/d/TEza0q
    code            : TEza0q
    parentFolder    : a1d87e71-f2c0-43e2-974d-a24e8d587bc6
    fileId          : 0ec70f4d-4ae6-4449-8674-91af5909fb42
    fileName        : text.txt
    md5             : 89da2808465ff4b8a18e192ba873c458
    server          : store8
```

**Right Click to File**
![Adjuntar Imagen](imagen de asdasdadas en contexto de menu de archivo)

</details>

</details>

<details open>
<summary>Linux</summary>

##### Installation

You can install executing gofile_setup.sh.

<details open>
<summary>Permissions</summary>

**Python File**

```shell
chmod +x goFile.py
```

**Binary File**

```shell
chmod +x  goFile
```

</details>

<details open>
<summary>Usage</summary>

<summary>Usage</summary>
<p>Run the program from the command line with the following options:</p>

 <h3>Options:</h3>
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
<h3>Examples:</h3>
  
Upload a file:
<code>python gofile.py -u file.txt</code>

Download a file by URL:
<code>python gofile.py -d https://store5.gofile.io/download/fcd000f4-73d1-4966-8c56-20496efd150a/text.txt</code>

Download a file by server, fileId, and fileName:
<code>python gofile.py -s store5 fcd000f4-73d1-4966-8c56-20496efd150a file.txt</code>
  <h2>Output Format</h2>
  <p>The program can return data in JSON, XML, or plain text format. If no format is specified, it defaults to plain text format.</p>

**XML**  
```xml
<?xml version="1.0" encoding="UTF-8" ?>
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
</uploadedFile>
```

**JSON***
```json
{
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
}
```
**PLAINTEXT**
```css
status          : ok
data :
    guestToken      : OUWgISULaTNl42Tr5tc8UIiI1Zl8iwY8
    downloadPage    : https://gofile.io/d/TEza0q
    code            : TEza0q
    parentFolder    : a1d87e71-f2c0-43e2-974d-a24e8d587bc6
    fileId          : 0ec70f4d-4ae6-4449-8674-91af5909fb42
    fileName        : text.txt
    md5             : 89da2808465ff4b8a18e192ba873c458
    server          : store8
```
</details>

</details>
</details>

<details>
  <summary><h4>AnonFiles (**DEPRECATED**)</h4></summary>

Description of AnonFiles

<details>
<summary>Windows</summary>

##### Installation

You can install executing anonfiles_setup.exe and follow the steps.

<details>
<summary>Usage</summary>

**Python File**

```shell
python3 anonFiles.py
```

**Exe File**

```shell
start anonFiles.exe
```

**Right Click to File**
![Adjuntar Imagen](imagen de asdasdadas in the context of the file menu)

</details>

</details>

<details>
<summary>Linux</summary>

##### Installation

You can install executing anonfiles_setup.sh.

<details>
<summary>Permissions</summary>

**Python File**

```shell
chmod +x anonFiles.py
```

**Binary File**

```shell
chmod +x  anonFiles
```

</details>

<details>
<summary>Usage</summary>

**Python File**

```shell
python3 anonFiles.py
```

**Binary File**

```shell
./anonFiles
```

</details>

</details>
</details>

<details>
  <summary><h4>BayFiles (**DEPRECATED**)</h4></summary>

Description of BayFiles

<details>
<summary>Windows</summary>

##### Installation

You can install executing bayfiles_setup.exe and follow the steps.

<details>
<summary>Usage</summary>

**Python File**

```shell
python3 bayfiles.py
```

**Exe File**

```shell
start bayfiles.exe
```

**Right Click to File**
![Adjuntar Imagen](imagen de asdasdadas in the context of the file menu)

</details>

</details>

<details>
<summary>Linux</summary>

##### Installation

You can install executing bayfiles_setup.sh.

<details>
<summary>Permissions</summary>

**Python File**

```shell
chmod +x bayfiles.py
```

**Binary File**

```shell
chmod +x  bayfiles
```

</details>

<details>
<summary>Usage</summary>

**Python File**

```shell
python3 bayfiles.py
```

**Binary File**

```shell
./bayfiles
```

</details>
</details>
</details>
</details>

## Technologies

<div style="background-color:#74797e;margin:0;padding:0;vertical-align:middle;text-align:center;padding:10pt;border-top:5pt dashed #0d1117;border-bottom:5pt dashed #0d1117;">
  <img src="https://upload.wikimedia.org/wikipedia/commons/9/91/Bayfiles_logo.png" alt="BayFiles" style="padding:10pt;height:50pt;filter:drop-shadow(0.4pt 1pt 1pt black);" height="50pt" title="BayFiles">
  <img src="https://static.wikia.nocookie.net/logopedia/images/5/5a/Logogoloo.png" alt="AnonFiles" style="padding:10pt;height:50pt;filter:drop-shadow(1pt 1pt 1pt black);" height="50pt" title="AnonFiles">
  <img src="https://gofile.io/dist/img/logo-big.png" alt="GoFiles" style="padding:10pt;height:40pt;filter:drop-shadow(1pt 1pt 1pt black);" height="50pt" title="goFile">
</div>

Enjoy easy and convenient file uploads with FileUploader!

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

| **Service** 	| **What we need** 	| **URL** 	| **Active** 	|
|-------------	|------------------	|---------	|------------	|
|**JSONBin**|API KEYs|[Fill te form](https://forms.gle/2J96dZAEYDDJaEcp9)|**YES**|
|*TEST*|API KEYs|[Fill te form](https://forms.gle/)|**No**|
|*TEST*|API KEYs|[Fill te form](https://forms.gle/)|**No**|

## License

[MIT](https://choosealicense.com/licenses/mit/)
