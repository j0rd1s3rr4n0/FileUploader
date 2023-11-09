<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FileUploader</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            margin: 0;
            padding: 0;
        }

        h1 {
            background-color: #0d1117;
            color: #ffffff;
            padding: 10px;
            margin: 0;
            text-align: center;
        }

        .container {
            margin: 20px;
        }

        .details {
            margin: 20px;
            padding: 10px;
            background-color: #ffffff;
            box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
            border-radius: 5px;
            transition: box-shadow 0.3s;
        }

        .details:hover {
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
        }

        summary {
            cursor: pointer;
            background-color: #0d1117;
            color: #ffffff;
            padding: 10px;
            margin: 0;
        }

        summary h2 {
            margin: 0;
        }

        img {
            padding: 10px;
            height: 50px;
            filter: drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.2));
        }

        .tech-icons {
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #ffffff;
            margin: 0;
            padding: 10px;
            border-top: 5px solid #0d1117;
            border-bottom: 5px solid #0d1117;
        }

        .license {
            margin: 20px 0;
        }

        a {
            color: #1f6feb;
            text-decoration: none;
        }

        a:hover {
            color: #0d93fc;
        }

        p {
            font-size: 16px;
        }
    </style>
</head>
<body>
    <h1>FileUploader</h1>

    <div class="container">
        <details class="details">
            <summary>
                <h2>Automate Anonymous File Uploads and Downloads</h2>
            </summary>

            <details>
                <summary>
                    <h3>Overview</h3>
                </summary>
                <p>
                    FileUploader is a Python script that simplifies the process of uploading files to various file-hosting services, including Anonfiles, Bayfiles (Deprecated), and GoFile. This script streamlines the file upload process and provides you with direct download links, making it convenient for sharing files.
                </p>
                <p><strong>Note:</strong> Anonfiles and Bayfiles are Deprecated. Please consider using the GoFile option for a more reliable service.</p>
            </details>

            <details>
                <summary>
                    <h3>Usage</h3>
                </summary>

                <details>
                    <summary>
                        <h4>FileUploader</h4>
                    </summary>

                    <details>
                        <summary>
                            <h5>Windows</h5>
                        </summary>

                        <p><strong>Installation</strong></p>
                        <p>You can install by executing fileuploader_setup.exe and follow the steps.</p>

                        <p><strong>Usage</strong></p>

                        <p><strong>Python File</strong></p>
                        <pre>python3 fileUploader.py</pre>

                        <p><strong>Exe File</strong></p>
                        <pre>start fileUploader.exe</pre>

                        <img src="file.png" alt="File Icon" />

                    </details>

                    <details>
                        <summary>
                            <h5>Linux</h5>
                        </summary>

                        <p><strong>Installation</strong></p>
                        <p>You can install by executing fileuploader_setup.sh.</p>

                        <p><strong>Permissions</strong></p>

                        <p><strong>Python File</strong></p>
                        <pre>chmod +x fileUploader.py</pre>

                        <p><strong>Binary File</strong></p>
                        <pre>chmod +x fileUploader</pre>

                        <p><strong>Usage</strong></p>

                        <p><strong>Python File</strong></p>
                        <pre>python3 fileUploader.py</pre>

                        <p><strong>Binary File</strong></p>
                        <pre>./fileUploader</pre>

                        <img src="file.png" alt="File Icon" />

                    </details>
                </details>

                <details>
                    <summary>
                        <h4>GoFile</h4>
                    </summary>

                    <details>
                        <summary>
                            <h5>Windows</h5>
                        </summary>

                        <p><strong>Installation</strong></p>
                        <p>You can install by executing gofile_setup.exe and follow the steps.</p>

                        <details>
                            <summary>
                                <h6>Usage</h6>
                            </summary>
                            <p>Run the program from the command line with the following options:</p>
                            <p><strong>Options:</strong></p>
                            <ul>
                                <li><code>-v, --verbose</code>: Enable verbose mode to display detailed information during execution.</li>
                                <li><code>-d, --download-url &lt;url&gt;</code>: Download a file by providing the URL.</li>
                                <li><code>-s, --download &lt;server&gt; &lt;fileId&gt; &lt;fileName&gt;</code>: Download a file by specifying the server, fileId, and fileName.</li>
                                <li><code>-u, --upload &lt;filepath&gt;</code>: Upload a file from a local path.</li>
                                <li><code>--json</code>: Return data in JSON format.</li>
                                <li><code>--xml</code>: Return data in XML format.</li>
                                <li><code>--plaintext</code>: Return data in plain text format.</li>
                                <li><code>-o, --output &lt;output-file&gt;</code>: Save the processed data to a file with the specified name.</li>
                            </ul>
                            <p><strong>Examples:</strong></p>
                            <p>Upload a file:</p>
                            <pre>python gofile.py -u file.txt</pre>
                            <p>Download a file by URL:</p>
                            <pre>python gofile.py -d https://store5.gofile.io/download/fcd000f4-73d1-4966-8c56-20496efd150a/text.txt</pre>
                            <p>Download a file by server, fileId, and fileName:</p>
                            <pre>python gofile.py -s store5 fcd000f4-73d1-4966-8c56-20496efd150a file.txt</pre>
                            <p><strong>Output Format</strong></p>
                            <p>The program can return data in JSON, XML, or plain text format. If no format is specified, it defaults to plain text format.</p>
                            <p><strong>XML</strong></p>
                            <pre>
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
                            </pre>
                        </details>
