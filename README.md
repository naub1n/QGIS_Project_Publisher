## <img src="icon.png" width="20"> Project Publisher plugin:

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

<table style="border: none;">
    <tr>
        <td align="center" style="text-align: center; vertical-align: middle;padding: 0;margin: 0;" height="20">
            <a href="README_fr.md">            
                <img src="https://github.com/hampusborgos/country-flags/raw/main/png250px/fr.png" width="40" height="20">
            </a>
        </td>
        <td align="center" style="horizontal-align: center; vertical-align: middle;padding: 0;margin: 0;" height="20">
            <a href="README.md">  
                <img src="https://github.com/hampusborgos/country-flags/raw/main/png250px/gb.png" width="40" height="20">
            </a>
        </td>
    </tr> 
    <td style="text-align: center; vertical-align: middle;padding: 0 10px;">
        Lisez-moi
    </td>
    <td style="text-align: center; vertical-align: middle;padding: 0 10px;">
        ReadMe
    </td>
</table>

Publish easily your QGIS project on QWC2 with [QWC Project Publisher service](https://github.com/naub1n/qwc-project-publisher-service)

## Configuration

If qwc-project-publisher-service need authentication:
* create a new Authentication ID, if not exists, with QGIS authentication manager.</br>
`Settings` -> `Options` -> `Authentication`
* Select correct **AuthID** in Project Publisher plugin

Add the qwc-project-publisher-service **URL**. If you use nginx service, use the correct URL redirection (Ex: http://www.myqwc2app.com/publisher).

## How to use :

Click to `Connect` button to list all projects exposed by qwc-project-publisher-service.

Now you can:
* Select a project and click to `Load` button to open project in QGIS
* Select a project and click to `Delete` button to delete project in QWC2
* Select a project and click to `Publish` button to publish your current project and replace project in QWC2
* Select `New` and click to `Publish` button to publish your current project
