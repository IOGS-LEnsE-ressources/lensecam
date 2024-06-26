# -*- coding: utf-8 -*-
"""*camera_ids_widget* file.

*camera_ids_widget* file that contains :

    * :class::CameraIdsWidget to integrate an IDS camera into a PyQt6 graphical interface.
    * :class::CameraIdsListWidget to generate a Widget including the list of available camerasintegrate an IDS camera into a PyQt6 graphical interface.
    * :class::CameraIdsParamsWidget to display the parameters of a camera.
    * :class::SmallParamsDisplay to ...

.. module:: CameraIDSWidget
   :synopsis: class to integrate an IDS camera into a PyQt6 graphical interface.

.. note:: LEnsE - Institut d'Optique - version 0.1

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>
"""

import sys
import time
from ids_peak import ids_peak

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QCheckBox,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap

from lensepy.images.conversion import *
from lensepy.pyqt6.widget_slider import WidgetSlider

if __name__ == "__main__":
    from camera_list import CameraList
    from camera_ids import CameraIds, get_bits_per_pixel
else:
    from lensecam.ids.camera_list import CameraList
    from lensecam.ids.camera_ids import CameraIds, get_bits_per_pixel


class CameraIdsListWidget(QWidget):
    """Generate available cameras list.
    
    Generate a Widget including the list of available cameras and two buttons :
        * connect : to connect a selected camera ;
        * refresh : to refresh the list of available cameras.
    
    :param cam_list: CameraList object that lists available cameras.
    :type cam_list: CameraList
    :param cameras_list: list of the available IDS Camera.
    :type cameras_list: list[tuple[int, str, str]]
    :param cameras_nb: Number of available cameras.
    :type cameras_nb: int
    :param cameras_list_combo: A QComboBox containing the list of the available cameras
    :type cameras_list_combo: QComboBox
    :param main_layout: Main layout container of the widget.
    :type main_layout: QVBoxLayout
    :param title_label: title displayed in the top of the widget.
    :type title_label: QLabel
    :param bt_connect: Graphical button to connect the selected camera
    :type bt_connect: QPushButton
    :param bt_refresh: Graphical button to refresh the list of available cameras.
    :type bt_refresh: QPushButton
    """

    connected = pyqtSignal(str)

    def __init__(self) -> None:
        """
        Default constructor of the class.
        """
        super().__init__(parent=None)
        # Objects linked to the CameraList object
        self.cam_list = CameraList()
        self.cameras_list = self.cam_list.get_cam_list()
        self.cameras_nb = self.cam_list.get_nb_of_cam()

        # Graphical list as QComboBox 
        self.cameras_list_combo = QComboBox()

        # Graphical elements of the interface
        self.main_layout = QVBoxLayout()

        self.title_label = QLabel('Available cameras')

        self.bt_connect = QPushButton('Connect')
        self.bt_connect.clicked.connect(self.send_signal_connected)
        self.bt_refresh = QPushButton('Refresh')
        self.bt_refresh.clicked.connect(self.refresh_cameras_list_combo)

        if self.cameras_nb == 0:
            self.bt_connect.setEnabled(False)
        self.main_layout.addWidget(self.title_label)
        self.main_layout.addWidget(self.cameras_list_combo)
        self.main_layout.addWidget(self.bt_connect)
        self.main_layout.addWidget(self.bt_refresh)

        self.setLayout(self.main_layout)
        self.refresh_cameras_list_combo()

    def refresh_cameras_list(self) -> None:
        """Refresh the list of available cameras.
        
        Update the cameras_list parameter of this class.
        """
        self.cam_list.refresh_list()
        self.cameras_list = self.cam_list.get_cam_list()
        self.cameras_nb = self.cam_list.get_nb_of_cam()
        if self.cameras_nb == 0:
            self.bt_connect.setEnabled(False)
        else:
            self.bt_connect.setEnabled(True)

    def refresh_cameras_list_combo(self) -> None:
        """Refresh the combobox list of available cameras.
        
        Update the cameras_list_combo parameter of this class.
        """
        self.refresh_cameras_list()
        self.cameras_list_combo.clear()
        for i, cam in enumerate(self.cameras_list):
            self.cameras_list_combo.addItem(f'IDS-{cam[1]}')

    def get_selected_camera_dev(self) -> ids_peak.Device:
        """Return the device object.
        
        Return the device object from ids_peak API of the selected camera.
        
        :return: the index number of the selected camera.
        :rtype: ids_peak.Device
        """
        cam_id = self.cameras_list_combo.currentIndex()
        dev = self.cam_list.get_cam_device(cam_id)
        return dev

    def send_signal_connected(self, event) -> None:
        """Send a signal when a camera is selected to be used.
        """
        cam_id = self.cameras_list_combo.currentIndex()
        self.connected.emit('cam:' + str(cam_id) + ':')


class CameraIdsParamsWidget(QWidget):
    """CameraIdsWidget class, children of QWidget.
    
    Class to display and to change the available parameters of a camera.
    
    :param parent: Parent widget of this widget.
    :type parent: SmallParamsDisplay
    :param camera: Device to control
    :type camera: ids_peak.Device
    
    """
    params_dict = {'fps': 'FPS', 'expo': 'Exposure Time', 'black': 'Black Level'}

    def __init__(self, parent):
        """Default constructor of the class.
        
        :param parent: Parent widget of this widget.
        :type parent: SmallParamsDisplay
        """
        super().__init__(parent=None)
        self.parent = parent
        # Camera device
        self.camera = None
        # Main layout
        self.main_layout = QVBoxLayout()
        # Graphical objects
        self.name_label = QLabel('Parameters')
        self.auto_update_check = QCheckBox('Auto-Update')
        self.auto_update_validated = False

        top_layout = QGridLayout()
        top_layout.addWidget(self.name_label, 0, 0)
        top_layout.setRowStretch(0, 2)
        top_layout.addWidget(self.auto_update_check, 0, 1)
        top_layout.setRowStretch(1, 1)
        top_widget = QWidget()
        top_widget.setLayout(top_layout)

        self.main_layout.addWidget(top_widget)

        name = CameraIdsParamsWidget.params_dict['fps']
        signal_name = 'fps'
        self.fps_slider = WidgetSlider(
            name=name, signal_name=signal_name)
        self.fps_slider.slider_changed_signal.connect(self.update_params)
        self.fps_slider.set_units('frames/s')
        self.fps_slider.set_min_max_slider(5, 50)
        fps_value = self.parent.camera.get_frame_rate()
        self.fps_slider.set_value(fps_value)
        self.main_layout.addWidget(self.fps_slider)

        name = CameraIdsParamsWidget.params_dict['expo']
        signal_name = 'expo'
        self.expotime_slider = WidgetSlider(
            name=name, signal_name=signal_name, integer=True)
        self.expotime_slider.slider_changed_signal.connect(self.update_params)
        self.expotime_slider.set_units('ms')
        max_expo = 1000 / fps_value - 1  # in ms
        self.expotime_slider.set_min_max_slider(1, max_expo)
        expo_value = self.parent.camera.get_exposure()
        self.expotime_slider.set_value(expo_value / 1000)
        self.main_layout.addWidget(self.expotime_slider)

        name = CameraIdsParamsWidget.params_dict['black']
        signal_name = 'black'
        self.blacklevel_slider = WidgetSlider(
            name=name, signal_name=signal_name, integer=True)
        self.blacklevel_slider.slider_changed_signal.connect(self.update_params)
        self.blacklevel_slider.set_units('LSB')
        cam_bits_nb = get_bits_per_pixel(self.parent.camera.get_color_mode())
        max_blacklevel = 2 ** cam_bits_nb - 1
        self.blacklevel_slider.set_min_max_slider(0, max_blacklevel)
        self.main_layout.addWidget(self.blacklevel_slider)

        self.setFixedSize(300, 400)
        self.setLayout(self.main_layout)

    def set_camera(self, camera) -> None:
        """Set the camera device to setup.
        
        :param camera: Device to control
        :type camera: pylon.TlFactory        
        """
        self.camera = camera
        _, name = self.camera.get_cam_info()
        self.name_label.setText(name + ' Parameters')

    def update_params(self, event) -> None:
        """Update parameters."""
        str_event = event.split(':')
        if str_event[0].lower() != 'update':
            if str_event[0].lower() == 'slider':
                if self.auto_update_check.isChecked() is False:
                    return

        if str_event[1].lower() == 'fps':
            value = self.fps_slider.get_real_value()
            # Verify if exposure time is lower than FPS limit
            expo = self.parent.camera.get_exposure() / 1000  # in ms
            fps_t = 1 / value * 1000  # in ms
            expo_val = int(fps_t - 1) * 1000
            print(f'Expo = {expo} - 1/FPS = {fps_t} --> EXP_V = {expo_val}')
            # Update exposure time limits
            self.expotime_slider.set_min_max_slider(1, expo_val / 1000)

            if expo > fps_t:
                print('UPD')
                self.parent.camera.set_exposure(expo_val)
                self.expotime_slider.set_value(expo_val)
            # Update frame rate of the camera
            self.parent.camera.set_frame_rate(value)
            # Update interval of the timer
        elif str_event[1].lower() == 'expo':
            value = self.expotime_slider.get_real_value() * 1000
            # time_ms = 1/value
            # self.parent.parent.main_timer.setInterval()
            self.parent.camera.set_exposure(value)
        elif str_event[1].lower() == 'black':
            value = self.blacklevel_slider.get_real_value()
            self.parent.camera.set_black_level(value)
        else:
            print('Error')

        # Update Small panel information
        self.parent.update_params()

    def closeEvent(self, event):
        """closeEvent redefinition. 
        
        Use when the user clicks on the red cross 
        to close the window.
        """
        reply = QMessageBox.question(self, 'Quit', 'Do you really want to close ?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()




class CameraIdsWidget(QWidget):
    """CameraIdsWidget class, children of QWidget.
    
    Class to integrate an IDS camera into a PyQt6 graphical interface.
 
    :param cameras_list_widget: Widget containing a ComboBox with the list of available cameras.
    :type cameras_list_widget: CameraIdsListWidget
    :param main_layout: Main layout container of the widget.
    :type main_layout: QGridLayout
    :param camera: Device to control
    :type camera: ids_peak.Device
    
    .. note::
        
        The camera is initialized with the following parameters :
            
        * Exposure time = 10 ms
        * FPS = 10
        * Black Level = 0
        * Color Mode = 'Mono12' (if possible)
     
    :param camera_display: Area to display the camera image
    :type camera_display: QLabel
    :param camera_infos: Area to display camera informations (FPS, expotime...)
    :type camera_infos: SmallParamsDisplay
    :param main_timer: timer object to manage display refresh
    :type main_timer: QTimer
    
    """

    connected = pyqtSignal(str)

    def __init__(self, camera_device:  ids_peak.Device = None, params_disp: bool = True, css: str = '') -> None:
        """Default constructor of the class.

        :param params_disp: Displaying the parameters. Default true.
        :type params_disp: bool
        """

        super().__init__(parent=None)
        # Camera
        self.display_params = params_disp

        # Graphical objects
        self.camera_display = QLabel('Test')
        if self.display_params:
            self.camera_infos = SmallParamsDisplay(self)
        self.main_layout = QGridLayout()

        # Time management
        self.main_timer = QTimer()
        self.main_timer.stop()
        self.main_timer.setInterval(100)  # in ms
        self.main_timer.timeout.connect(self.refresh)

        # List of the available camera
        self.camera = None
        self.image_array = None
        if camera_device is None:
            print('No Cam')
            self.camera_device = None
            self.cameras_list_widget = CameraIdsListWidget()
            self.main_layout.addWidget(self.cameras_list_widget, 0, 0)

            # Connect the signal emitted by the ComboList to its action
            self.cameras_list_widget.connected.connect(self.connect_camera)
        else:
            print('Camera OK')
            self.camera_device = camera_device
            self.connect_camera(camera_device=camera_device)

        self.setLayout(self.main_layout)
        self.setStyleSheet(css)

    def connect_camera(self, event=None, camera_device: ids_peak.Device = None) -> None:
        """
        Trigger action when a connected signal from the combo list is emitted.


        """
        try:
            if camera_device is None:
                print('No Connect')
                # Get the index of the selected camera
                cam_dev = self.cameras_list_widget.get_selected_camera_dev()
            else:
                cam_dev = camera_device
            print(type(cam_dev))
            # Create Camera object
            self.camera: CameraIds = CameraIds(cam_dev) # CameraIds
            _,model = self.camera.get_cam_info()
            # Emit the connected signal with the model of the camera
            self.connected.emit(f'cam:{model}:')

            # Initialize the camera with default parameters
            self.camera.set_frame_rate(10)
            self.camera.set_color_mode('Mono8')
            self.camera.set_exposure(10000)
            self.camera.set_black_level(0)
            # Clear layout with combo list
            self.clear_layout()
            # Include the widget with the camera display
            self.camera_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.main_layout.addWidget(self.camera_display, 0, 0)
            self.main_layout.setRowStretch(0, 4)
            if self.display_params:
                self.main_layout.addWidget(self.camera_infos, 1, 0)
                self.main_layout.setRowStretch(1, 1)
                self.camera_infos.set_camera(self.camera)
                self.camera_infos.update_params()
            # Start main timer
            self.camera.start_acquisition()
            self.acquiring = True
            fps = self.camera.get_frame_rate()
            time_ms = int(1000 / fps + 10)  # 10 ms extra time
            self.main_timer.setInterval(time_ms)  # in ms
            self.main_timer.start()
        except Exception as e:
            print("Exception - connect_camera: " + str(e) + "")

    def is_connected(self) -> bool:
        """
        Test if a camera is connected.
        
        :return: True if a camera is connected.
        :rtype: bool
        """
        if self.camera is None:
            return False
        else:
            return True

    def stop_acquisition(self, keep_active:bool = False):
        """Stop the acquisition of the camera."""
        if self.is_connected():
            if self.main_timer.isActive():
                self.main_timer.stop()
            if keep_active is False:
                self.camera.stop_acquisition()

    def start_acquisition(self):
        """Stop the acquisition of the camera."""
        if self.is_connected():
            self.camera.start_acquisition()
            # Start main timer
            fps = self.camera.get_frame_rate()
            time_ms = int(1000 / fps + 10)  # 10 ms extra time
            self.main_timer.setInterval(time_ms)  # in ms
            self.main_timer.start()

    def clear_layout(self) -> None:
        """
        Clear the main layout of the Widget.
        
        .. note::
            
            This function is used to display camera image instead of the camera
            list when a camera is selected and the user clicks on the connect
            button.
            
        """
        count = self.main_layout.count()
        for i in reversed(range(count)):
            item = self.main_layout.itemAt(i)
            widget = item.widget()
            widget.deleteLater()

    def refresh(self) -> None:
        """
        Refresh the image from camera.
        
        .. note::
            
            This function is called by a QTimer event
            according to the FPS rate.
        
        """
        try:
            if self.is_connected():
                self.image_array = self.get_disp_image()
                # Get widget size
                frame_width = self.width()
                frame_height = self.height()
                # Resize to the display size
                image_array_disp2 = resize_image_ratio(
                    self.image_array,
                    frame_width,
                    frame_height)
                # Convert the frame into an image
                image = array_to_qimage(image_array_disp2)
                pmap = QPixmap(image)

                # display it in the cameraDisplay
                self.camera_display.setPixmap(pmap)
            else:
                self.camera_display.setText('No Camera Connected')
        except Exception as e:
            print("Exception - refresh: " + str(e) + "")

    def get_image(self) -> np.ndarray:
        """Return a RAW image from the camera as an array."""
        if self.camera.is_camera_connected():
            self.start_acquisition()
            # Get raw image
            image_array = self.camera.get_image()
            # Depending on the color mode - display only in 8 bits mono
            nb_bits = get_bits_per_pixel(self.camera.get_color_mode())
            if nb_bits > 8:
                image_array = image_array.view(np.uint16)
            else:
                image_array = image_array.view(np.uint8)
            return image_array
        else:
            return None

    def get_disp_image(self) -> np.ndarray:
        """Return an image from the camera as an array of uint8."""
        if self.camera.is_camera_connected():
            self.start_acquisition()
            # Get raw image
            image_array = self.camera.get_image()
            # Depending on the color mode - display only in 8 bits mono
            nb_bits = get_bits_per_pixel(self.camera.get_color_mode())
            if nb_bits > 8:
                image_array = image_array.view(np.uint16)
                image_array_disp = (image_array / (2 ** (nb_bits - 8))).astype(np.uint8)
            else:
                image_array = image_array.view(np.uint8)
                image_array_disp = image_array.astype(np.uint8)
            return image_array_disp
        else:
            return None

    def quit_application(self) -> None:
        """
        Quit properly the PyQt6 application window.
        """
        try:
            if self.main_timer.isActive():
                self.main_timer.stop()
                print('TIMER STOP')
            time.sleep(0.5)
            if self.camera is not None:
                self.camera.disconnect()
                print('DISCONNECTED')
                ids_peak.Library.Close()
            QApplication.instance().quit()
        except Exception as e:
            print("Exception - close/quit: " + str(e) + "")


class MyMainWindow(QMainWindow):
    """MyMainWindow class, children of QMainWindow.
    
    Class to test the previous widget.

    """

    def __init__(self) -> None:
        """
        Default constructor of the class.
        """
        super().__init__()
        self.setWindowTitle("CameraIdsWidget Test Window")
        self.setGeometry(100, 100, 500, 400)

        # Init IDS Peak
        ids_peak.Library.Initialize()
        # Create a camera manager
        manager = ids_peak.DeviceManager.Instance()
        manager.Update()

        if manager.Devices().empty():
            print("No Camera")
        else:
            print("Camera")
            device = manager.Devices()[0].OpenDevice(ids_peak.DeviceAccessType_Exclusive)

        self.central_widget = CameraIdsWidget(camera_device=device, params_disp=True)
        #self.central_widget = CameraIdsWidget()
        self.setCentralWidget(self.central_widget)

        self.choice_widget = QWidget()
        self.choice_layout = QVBoxLayout()
        self.mode_acq = QPushButton('Mode ACQ')
        self.mode_stop = QPushButton('Mode STOP')
        self.mode_get = QPushButton('Mode GET')
        self.mode_acq.clicked.connect(self.action_mode_acq)
        self.choice_layout.addWidget(self.mode_acq)
        self.mode_stop.clicked.connect(self.action_mode_stop)
        self.choice_layout.addWidget(self.mode_stop)
        self.mode_get.clicked.connect(self.action_mode_get)
        self.choice_layout.addWidget(self.mode_get)
        self.choice_widget.setLayout(self.choice_layout)
        self.setMenuWidget(self.choice_widget)

    def action_mode_stop(self, event):
        print(f'STOP')
        self.central_widget.stop_acquisition(keep_active=True)

    def action_mode_acq(self, event):
        print(f'ACQ')
        self.central_widget.start_acquisition()

    def action_mode_get(self, event):
        print(f'GET')
        self.central_widget.stop_acquisition()
        pict1 = self.central_widget.get_image()
        cv2.imwrite('myImage1.png', pict1)
        print('2')
        pict2 = self.central_widget.get_image()
        cv2.imwrite('myImage2.png', pict2)
        print('2')
        pict3 = self.central_widget.get_image()
        cv2.imwrite('myImage3.png', pict3)
        print('2')
        pict4 = self.central_widget.get_image()
        cv2.imwrite('myImage4.png', pict4)
        print('2')
        pict5 = self.central_widget.get_image()
        cv2.imwrite('myImage5.png', pict5)
        print('2')
        self.central_widget.start_acquisition()


    def closeEvent(self, event):
        """
        closeEvent redefinition. Use when the user clicks 
        on the red cross to close the window
        """
        reply = QMessageBox.question(self, 'Quit', 'Do you really want to close ?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.central_widget.quit_application()
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    def test(event):
        print(f'Camera {event}')

    app = QApplication(sys.argv)
    main_window = MyMainWindow()
    main_window.show()
    sys.exit(app.exec())
