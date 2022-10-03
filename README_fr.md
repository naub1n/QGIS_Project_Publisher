## <img src="icon.png" width="20"> Plugin Project Publisher:

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

Publiez facilement votre projet QGIS sur QWC2 avec [QWC Project Publisher service](https://github.com/naub1n/qwc-project-publisher-service)

## Configuration

Si qwc-project-publisher-service a besoin d'une authentification:
* Créez un nouvel ID d'authentification, s'il n'existe pas, avec le gestionnaire d'authentification de QGIS.</br>
`Préférences` -> `Options` -> `Authentification`
* Selectionnez le bon **AuthID** dans le plugin Project Publisher.

Ajoutez l'**URL** de qwc-project-publisher-service. Si vous utilisez le service nginx, utilisez la bonne URL de redirection (Ex: http://www.myqwc2app.com/publisher).

## How to use :

Cliquez sur le bouton `Connect` pour lister l'ensemble des projets exposés par qwc-project-publisher-service.

Maintenant vous pouvez:
* Selectionner un projet et cliquer sur le bouton `Charger` pour ouvrir le projet dans QGIS
* Selectionner un projet et cliquer sur le bouton `Supprimer` pour supprimer run projet dans QWC2
* Selectionner un projet et cliquer sur le bouton `Publier` pour publier le projet existant et remplacer le projet dans QWC2
* Selectionner `Nouveau` et cliquer sur le bouton `Publier` pour publier le projet existant dans QWC2