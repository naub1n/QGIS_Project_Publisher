# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ProjectPublisherDockWidget
                                 A QGIS plugin
 Publish your project to QWC2 easily with qwc-project-publisher-service
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2022-09-26
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Nicolas AUBIN
        email                : aubinnic@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import tempfile
import requests
import json

from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal, QCoreApplication
from qgis.core import QgsApplication, QgsMessageLog, Qgis, QgsAuthMethodConfig, QgsProject
from qgis.utils import iface


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'project_publisher_dockwidget_base.ui'))


class ProjectPublisherDockWidget(QtWidgets.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(ProjectPublisherDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.qtbtn_refresh_auth.setIcon(self.get_icon("refresh"))

        self.cfg_file = os.path.join(os.path.dirname(__file__), 'project_publisher_conf.json')

        self.qwc_listprojects_path = "listprojects"
        self.qwc_getproject_path = "getproject"
        self.qwc_deleteproject_path = "deleteproject"
        self.qwc_publishproject_path = "publish"
        self.qwc_login_path = "auth/login"

        self.qtbtn_connect.clicked.connect(self._clicked_connect_button)
        self.qtbtn_load_project.clicked.connect(self._clicked_load_button)
        self.qtbtn_publish.clicked.connect(self._clicked_publish_button)
        self.qtbtn_delete_project.clicked.connect(self._clicked_delete_button)
        self.qtbtn_refresh_auth.clicked.connect(self._clicked_refresh_button)
        self.qtle_url_qwc.textChanged.connect(self._changed_url_edit)

        self.session = None
        self.headers = {}

        self.load_auth_ids()
        self.load_config()


    def log(self, message, level, user_alert=False):
        """Send message to QGIS Console and in MessageBar (optional) with specific level

        :param str log_message: message to show.
        :param str level: Qgis Level.
        :returns: None.
        """
        QgsMessageLog.logMessage(message, 'Project publisher', level=level, notifyUser=user_alert)
        if user_alert:
            iface.messageBar().pushMessage(message, level=level)

    def log_err(self, log_message, user_alert=False):
        """Send critical message to QGIS Console and in MessageBar (optional)

        :param str log_message: message to show.
        :returns: None.
        """
        self.log(log_message, Qgis.Critical, user_alert)

    def log_warn(self, log_message, user_alert=False):
        """Send warning message to QGIS Console and in MessageBar (optional)

        :param str log_message: message to show.
        :returns: None.
        """
        self.log(log_message, Qgis.Warning, user_alert)

    def log_info(self, log_message, user_alert=False):
        """Send info message to QGIS Console and in MessageBar (optional)

        :param str log_message: message to show.
        :returns: None.
        """
        self.log(log_message, Qgis.Info, user_alert)

    def tr(self, message):
        return QCoreApplication.translate('ProjectPublisherDockWidget', message)

    def get_icon(self, name):
        if name == "refresh":
            icon = QtGui.QIcon(QgsApplication.iconPath("mActionRefresh.svg"))
        else:
            icon = QtGui.QIcon(QgsApplication.iconPath("missing_image.svg"))

        return icon

    def qwc_pp_service_base_url(self):
        """Add trailing slash at the end of base URL?

        :returns: url string.
        :rtype: str
        """
        return self.qtle_url_qwc.text().rstrip("/") + "/"

    def load_auth_ids(self):
        """Load all auth ids in Qgis auth manager

        :returns: None.
        """
        auth_manager = QgsApplication.authManager()
        auth_ids = auth_manager.availableAuthMethodConfigs().keys()
        cbx = self.qtcbx_auth_ids
        cbx.clear()
        for auth_id in auth_ids:
            cbx.addItem(auth_id)

    def check_before_connect(self):
        """Check value of AuthId combobox and value of QWC project publisher service URL

        :returns: True or False.
        :rtype: bool
        """
        if self.qtgbx_auth.isChecked():
            if not self.qtcbx_auth_ids.currentText():
                self.log_warn(self.tr("Select an auth id"))
                return False

        if not self.qtle_url_qwc.text():
            self.log_warn(self.tr("QWC Project publisher service URL not defined"), True)
            return False

        return True

    def read_project(self, project_path):
        """Open QGIS project in GUI

        :param str project_path: Absolute path of the project.
        :returns: None.
        """
        if QgsProject.instance().isDirty():
            reply = QtWidgets.QMessageBox.question(iface.mainWindow(),
                                                   self.tr('Project unsaved'),
                                                   self.tr('Continue without saving current project?'),
                                                   QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
            if not reply == QtWidgets.QMessageBox.Yes:
                return

        QgsProject.instance().read(project_path)

    def login_to_qwc(self):
        """Connect to QWC Auth service and create a new Requests session

        :return: Request response or None if error.
        :rtype: requests.Response
        """
        qwc_pp_service_base_url = self.qtle_url_qwc.text()
        login_url = requests.compat.urljoin(qwc_pp_service_base_url, self.qwc_login_path)

        if self.qtgbx_auth.isChecked():
            auth_id = self.qtcbx_auth_ids.currentText()
            auth_manager = QgsApplication.authManager()
            qgs_conf = QgsAuthMethodConfig()
            auth_manager.loadAuthenticationConfig(auth_id, qgs_conf, True)
            username = qgs_conf.config('username', '')
            password = qgs_conf.config('password', '')

            data = {
                'username': username,
                'password': password
            }
        else:
            data = {}

        try:
            response = self.session.post(login_url, data=data)
            self.headers = response.headers
            if 'csrf_access_token' in self.session.cookies:
                csrftoken = self.session.cookies['csrf_access_token']
                self.session.headers.update({'X-CSRF-TOKEN': csrftoken})
                self.headers['X-CSRF-TOKEN'] = csrftoken
            else:
                self.log_warn("No CSRF token in reponse cookies")
        except Exception as e:
            self.log_err(str(e), True)
            return

        return response

    def get_projects(self):
        """Get all projects exposed by QWC project publisher

        :return: Request response or False if error.
        :rtype: requests.Response
        """
        url_listprojects = requests.compat.urljoin(self.qwc_pp_service_base_url(), self.qwc_listprojects_path)

        try:
            response = self.session.get(url_listprojects)
        except Exception as e:
            self.log_err(str(e), True)
            return False

        if not response.status_code == 200:
            self.log_err(self.tr("Unable to list projects : %s") % self.get_error_info(response), True)
            return False

        if response:
            return response.json()

    def populate_combobox_projects(self):
        """Add items in projects combobox

        :return: Return True if success.
        :rtype: bool
        """
        projects = self.get_projects()
        if projects:
            cbx = self.qtcbs_projects_list
            cbx.clear()
            cbx.addItem(self.new_project_item_value())
            for project in projects:
                cbx.addItem(project)
        else:
            return False

        return True

    def get_combobox_items(self, combobox_widget):
        """Get items in projects QCombobox

        :param QtWidgets.QComboBox combobox_widget: Projects QCombobox
        :return: list of string.
        :rtype: list
        """
        items = [combobox_widget.itemText(i) for i in range(combobox_widget.count())]
        return items

    def connect_to_qwc(self):
        """Create new requests.session and logging in to QWC (optional)

        :return: True or False.
        :rtype: bool
        """
        self.session = requests.session()
        if self.qtgbx_auth.isChecked():
            login_response = self.login_to_qwc()
            error_msg = self.tr("Unable to login in to qwc auth service : %s")

            if login_response is None:
                self.log_err(error_msg % self.get_error_info(login_response), True)
                return False

            if "login" in login_response.url:
                self.log_err(error_msg % self.tr('Authentication failed'), True)
                return False

            if not login_response.status_code == 200:
                self.log_err(error_msg % self.get_error_info(login_response), True)
                return False

        self.log_info(self.tr("Successfully connected!"), True)

        self.save_config()

        return True

    def get_error_info(self, response):
        """Return JSON response or status code response if response is not json format

        :param requests.Response response: Request response
        :return: Message string with error.
        :rtype: str
        """
        if response is not None:
            try:
                error_info = response.json()
            except:
                error_info = 'HTTP Error %s' % response.status_code
        else:
            error_info = self.tr('No request response')

        return error_info

    def save_config(self):
        """Save current plugin configuration in json file

        :return: None.
        """
        cfg = {
            'auth_checked': self.qtgbx_auth.isChecked(),
            'auth_id': self.qtcbx_auth_ids.currentText(),
            'qwc_projectpublisher_url': self.qtle_url_qwc.text()
        }
        with open(self.cfg_file, 'w') as f:
            json.dump(cfg, f, indent=4)

    def get_config(self):
        """Read plugin configuration in json file

        :return: Plugin configuration.
        :rtype: dict
        """
        if os.path.exists(self.cfg_file):
            with open(self.cfg_file, 'r') as f:
                cfg = json.load(f)

            return cfg

    def load_config(self):
        """Change plugin widgets with plugin configuration values

        :return: None.
        """
        cfg = self.get_config()
        if cfg:
            self.qtgbx_auth.setChecked(cfg['auth_checked'])
            self.qtle_url_qwc.setText(cfg['qwc_projectpublisher_url'])
            auth_id = cfg['auth_id']
            if auth_id in self.get_combobox_items(self.qtcbx_auth_ids):
                self.qtcbx_auth_ids.setCurrentText(auth_id)

    def new_project_item_value(self):
        """Set value of the first item in projects combobox, for create a new project un QWC

        :return: Item value.
        :rtype: str
        """
        return self.tr('_New project_')

    def get_current_project_path(self):
        """Read project path in QGIS instance

        :return: Path.
        :rtype: str
        """
        current_project = QgsProject.instance()
        current_project_path = current_project.fileName()

        return current_project_path

    def get_output_project_filename(self):
        """Prepare the project filename before publishing

        :return: Filename.
        :rtype: str
        """
        current_project_path = self.get_current_project_path()
        current_project_filename = os.path.basename(current_project_path)

        if self.qtcbs_projects_list.currentText() == self.new_project_item_value():
            output_project_filename = current_project_filename
        else:
            output_project_filename = self.qtcbs_projects_list.currentText()

        return output_project_filename

    def enable_after_connect(self, enabled):
        """Enable or disable action buttons

        :param bool enabled: Set widgets to enabled
        :return: None.
        """
        self.qtgb_projects.setEnabled(enabled)
        self.qtbtn_publish.setEnabled(enabled)
        self.qtbtn_connect.setEnabled(not enabled)


    def _clicked_connect_button(self):
        """Action when Connect button is clicked

        :return: None.
        """
        if self.check_before_connect():
            if self.session:
                self.session = None

            if self.connect_to_qwc():
                if self.populate_combobox_projects():
                    self.enable_after_connect(True)

    def _clicked_load_button(self):
        """Action when Load button is clicked

        :return: None.
        """
        url_get_project = requests.compat.urljoin(self.qwc_pp_service_base_url(), self.qwc_getproject_path)
        project_filename = self.qtcbs_projects_list.currentText()

        qwc_getproject_content_params = {'filename': project_filename, 'content_only': False}

        if project_filename:
            if project_filename == self.new_project_item_value():
                self.log_warn(self.tr("Unable to load project '%s'") % project_filename, True)
            else:
                local_project_path = os.path.join(tempfile.gettempdir(), project_filename)
                try:
                    content = self.session.get(url_get_project, params=qwc_getproject_content_params, stream=True).content
                except Exception as e:
                    self.log_err(str(e), True)
                    return

                with open(local_project_path, 'wb') as out_file:
                    out_file.write(content)
                    out_file.close()

                self.log_info(self.tr("Project download to %s.") % local_project_path)

                self.read_project(local_project_path)

    def _clicked_publish_button(self):
        """Action when publish button is clicked

        :return: None.
        """
        if QgsProject.instance().isDirty():
            reply = QtWidgets.QMessageBox.question(iface.mainWindow(),
                                                   self.tr('Project unsaved'),
                                                   self.tr('Project must be saved before publishing. Do you want to save it now?'),
                                                   QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                iface.mainWindow().findChild(QtWidgets.QAction, 'mActionSaveProject').trigger()
            else:
                return

        current_project_path = self.get_current_project_path()
        current_project_filename = os.path.basename(current_project_path)

        url_publish_project = requests.compat.urljoin(self.qwc_pp_service_base_url(), self.qwc_publishproject_path)
        qwc_getproject_content_params = {'filename': current_project_filename, 'delete': False}

        output_project_filename = self.get_output_project_filename()

        projects = self.get_projects()
        if projects:
            if output_project_filename in projects:
                reply = QtWidgets.QMessageBox.question(iface.mainWindow(),
                                                       self.tr('Project already exists'),
                                                       self.tr('Replace online project?'),
                                                       QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
                if not reply == QtWidgets.QMessageBox.Yes:
                    return

        if current_project_path:
            with open(current_project_path, 'rb') as f:
                binary_file = f.read()
        else:
            self.log_warn(self.tr("Current project is not saved."), True)
            return

        files = {'file': (output_project_filename, binary_file)}

        self.log_info(self.tr("Publishing ..."))
        try:
            response = self.session.post(url_publish_project,
                                         files=files,
                                         params=qwc_getproject_content_params,
                                         timeout=120)
        except Exception as e:
            self.log_err(str(e), True)
            return

        if not response.status_code == 200:
            self.log_err(self.tr("Unable to publish project %s : %s") % (output_project_filename, self.get_error_info(response)), True)
        else:
            self.log_info(self.tr("Project %s published") % output_project_filename, True)
            self.populate_combobox_projects()
            if output_project_filename in self.get_combobox_items(self.qtcbs_projects_list):
                self.qtcbs_projects_list.setCurrentText(output_project_filename)

    def _clicked_delete_button(self):
        """Action when Delete button is clicked

        :return: None.
        """
        project_filename = self.qtcbs_projects_list.currentText()
        if project_filename:
            if project_filename == self.new_project_item_value():
                self.log_warn(self.tr("Unable to delete project '%s'") % project_filename, True)
            else:
                reply = QtWidgets.QMessageBox.question(iface.mainWindow(),
                                                       self.tr('Delete project'),
                                                       self.tr('Are you sure to delete permanently %s project in QWC?') % project_filename,
                                                       QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.Yes:
                    url_delete_project = requests.compat.urljoin(self.qwc_pp_service_base_url(), self.qwc_deleteproject_path)
                    qwc_deleteproject_params = {'filename': project_filename}

                    try:
                        response = self.session.delete(url_delete_project, params=qwc_deleteproject_params)
                    except Exception as e:
                        self.log_err(str(e), True)
                        return

                    if not response.status_code == 200:
                        self.log_err(self.tr("Unable to delete project %s : %s") % (project_filename, self.get_error_info(response)), True)
                    else:
                        self.log_info(self.tr("Project %s deleted") % project_filename, True)
                        self.populate_combobox_projects()

    def _clicked_refresh_button(self):
        """Action when Refresh button is clicked

        :return: None.
        """
        self.load_auth_ids()

    def _changed_url_edit(self):
        """Action when URL is changed

        :return: None.
        """
        self.enable_after_connect(False)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
