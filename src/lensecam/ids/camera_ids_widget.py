# -*- coding: utf-8 -*-
"""camera_ids file.

File containing :class::CameraIds
class to communicate with an IDS camera sensor.

.. module:: CameraIds
   :synopsis: class to communicate with an IDS camera sensor.

.. note:: LEnsE - Institut d'Optique - version 0.1

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>


.. warning::

    **IDS peak** (2.8 or higher) and **IDS Sofware Suite** (4.95 or higher) softwares
    are required on your computer.

    For old IDS camera, IDS peak must be installed in Custom mode with the Transport Layer option.

    **IDS peak IPL** (Image Processing Library) and **Numpy** are required.

.. note::

    To use old IDS generation of cameras (type UI), you need to install **IDS peak** in **custom** mode
    and add the **uEye Transport Layer** option.

.. note::

    **IDS peak IPL** can be found in the *IDS peak* Python API.

    Installation file is in the directory :file:`INSTALLED_PATH_OF_IDS_PEAK\generic_sdk\ipl\binding\python\wheel\x86_[32|64]`.

    Then run this command in a shell (depending on your python version and computer architecture):

    .. code-block:: bash

        pip install ids_peak_1.2.4.1-cp<version>-cp<version>m-[win32|win_amd64].whl

    Generally *INSTALLED_PATH_OF_IDS_PEAK* is :file:`C:\Program Files\IDS\ids_peak`

@ see : https://www.1stvision.com/cameras/IDS/IDS-manuals/en/index.html
@ See API DOC : C:\Program Files\IDS\ids_peak\generic_sdk\api\doc\html

# >>> ids_peak.Library.Initialize()
# >>> device_manager = ids_peak.DeviceManager.Instance()
# >>> device_manager.Update()
# >>> device_descriptors = device_manager.Devices()
# >>> my_cam_dev = device_descriptors[0].OpenDevice(ids_peak.DeviceAccessType_Exclusive)
# >>> my_cam = CameraIds(my_cam_dev)

"""

import numpy as np
if __name__ == '__main__':
    from camera_ids import CameraIds
    from camera_thread import CameraThread
else:
    from _tests.camera_ids import CameraIds
    from _tests.camera_thread import CameraThread
from lensecam.ids.camera_ids_widget import CameraIdsListWidget

from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QGridLayout
from PyQt6.QtCore import pyqtSignal
from lensepy.images.conversion import array_to_qimage, resize_image_ratio


class CameraIdsWidget(QWidget):
    """CameraIdsWidget class, children of QWidget.

    Class to integrate an IDS camera into a PyQt6 graphical interface.

    :param cameras_list_widget: Widget containing a ComboBox with the list of available cameras.
    :type cameras_list_widget: CameraIdsListWidget
    :param main_layout: Main layout container of the widget.
    :type main_layout: QGridLayout
    :param camera: Device to control
    :type camera: CameraIds

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

    """
    connected = pyqtSignal(str)

    def __init__(self, camera: CameraIds = None, params_disp=False):
        super().__init__(parent=None)
        # Camera
        self.display_params = params_disp
        self.camera = camera
        self.camera_connected = False
        # GUI
        self.camera_display = QLabel('Image')
        self.initUI()

    def set_camera(self, camera: CameraIds):
        self.camera = camera

    def initUI(self):
        self.layout = QGridLayout()
        self.layout.addWidget(self.camera_display, 0, 0)
        self.setLayout(self.layout)

        if self.camera is None:
            print('No Cam')
            self.cameras_list_widget = CameraIdsListWidget()
            self.layout.addWidget(self.cameras_list_widget, 1, 0)
            # Connect the signal emitted by the ComboList to its action
            self.cameras_list_widget.connected.connect(self.connect_camera)
        else:
            print('Camera OK')
            self.set_camera(camera=self.camera)

    def connect_camera(self, event):
        try:
            cam_dev = self.cameras_list_widget.get_selected_camera_dev()
            self.camera = CameraIds(cam_dev)
            self.camera_connected = True
            self.clear_layout(1, 0)
            print(cam_dev)
            self.connected.emit('cam')
        except Exception as e:
            print(f'Exception - connect_camera {e}')

    def clear_layout(self, row: int, column: int) -> None:
        """Remove widgets from a specific position in the layout.

        :param row: Row index of the layout.
        :type row: int
        :param column: Column index of the layout.
        :type column: int

        """
        item = self.layout.itemAtPosition(row, column)
        if item is not None:
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                self.layout.removeItem(item)

if __name__ ==  '__main__':
    class Remote(QWidget):
        """"""
        transmitted = pyqtSignal(str)

        def __init__(self, camera: CameraIds = None):
            super().__init__(parent=None)
            self.initUI()
            self.camera = camera

        def set_camera(self, camera: CameraIds):
            self.camera = camera
            self.camera.init_camera()
            self.camera.alloc_memory()

        def initUI(self):
            self.get_image_button = QPushButton('Get Image')
            self.get_image_button.clicked.connect(self.action_button)
            self.stop_acq_button = QPushButton('Stop Acq')
            self.stop_acq_button.clicked.connect(self.action_button)
            self.start_acq_button = QPushButton('Start Acq')
            self.start_acq_button.clicked.connect(self.action_button)
            self.expo_button = QPushButton('Expo')
            self.expo_button.clicked.connect(self.action_button)

            self.layout = QVBoxLayout()
            self.layout.addWidget(self.get_image_button)
            self.layout.addWidget(self.start_acq_button)
            self.layout.addWidget(self.stop_acq_button)
            self.layout.addWidget(self.expo_button)

            self.setLayout(self.layout)

        def action_button(self, event):
            button = self.sender()
            if button == self.get_image_button:
                self.transmitted.emit('get')
            if button == self.start_acq_button:
                self.transmitted.emit('start')
            if button == self.stop_acq_button:
                self.transmitted.emit('stop')
            if button == self.expo_button:
                self.transmitted.emit('expo')


    from PyQt6.QtWidgets import QMainWindow
    from PyQt6.QtGui import QPixmap

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.initUI()

            self.camera_thread = CameraThread()
            self.camera_thread.image_acquired.connect(self.update_image)

        def initUI(self):
            self.setWindowTitle("IDS Camera Display")
            self.setGeometry(100, 100, 800, 600)

            self.layout = QGridLayout()
            self.camera_widget = None
            self.remote = Remote()
            self.remote.transmitted.connect(self.action_remote)
            self.layout.addWidget(self.remote, 2, 0)

            self.central_widget = QWidget()
            self.central_widget.setLayout(self.layout)
            self.setCentralWidget(self.central_widget)

        def action_remote(self, event):
            if event == 'get':
                try:
                    print('Get Image OK')
                    self.camera_widget.camera.init_camera()
                    self.camera_widget.camera.alloc_memory()
                    self.camera_widget.camera.start_acquisition()
                    raw_array = self.camera_widget.camera.get_image()
                    # Depending on the color mode - display only in 8 bits mono
                    nb_bits = 8 #get_bits_per_pixel(self.camera.get_color_mode())
                    if nb_bits > 8:
                        image_array = raw_array.view(np.uint16)
                        image_array_disp = (image_array / (2 ** (nb_bits - 8))).astype(np.uint8)
                    else:
                        image_array_disp = raw_array
                    print(image_array_disp.dtype)
                    frame_width = self.camera_widget.width()
                    frame_height = self.camera_widget.height()
                    # Resize to the display size
                    image_array_disp2 = resize_image_ratio(
                            image_array_disp,
                            frame_width,
                            frame_height)
                    # Convert the frame into an image
                    image = array_to_qimage(image_array_disp2)
                    pmap = QPixmap(image)
                    # display it in the cameraDisplay
                    self.camera_widget.camera_display.setPixmap(pmap)
                    self.camera_widget.camera.stop_acquisition()
                    self.camera_widget.camera.free_memory()
                except Exception as e:
                    print("Exception - action_get_image: " + str(e) + "")
            elif event == 'start':
                print('Start')
                self.camera_thread.start()
            elif event == 'stop':
                print('Stop')
                self.camera_widget.camera.set_exposure(1000)
                self.camera_thread.stop()
            elif event == 'expo':
                print(f'Expo {self.camera_widget.camera.get_exposure()}')
                self.camera_widget.camera.set_exposure(20000)

        def set_camera(self, camera: CameraIds):
            """

            """
            self.camera_thread.set_camera(camera)
            self.camera_widget = CameraIdsWidget(camera)
            self.layout.addWidget(self.camera_widget, 1, 0)

        def update_image(self, image_array):
            try:
                frame_width = self.camera_widget.width()
                frame_height = self.camera_widget.height()
                # Resize to the display size
                image_array_disp2 = resize_image_ratio(
                    image_array,
                    frame_width,
                    frame_height)
                # Convert the frame into an image
                image = array_to_qimage(image_array_disp2)
                pmap = QPixmap(image)
                # display it in the cameraDisplay
                self.camera_widget.camera_display.setPixmap(pmap)
            except Exception as e:
                print(f'Exception - update_image {e}')

        def closeEvent(self, event):
            self.camera_thread.stop()
            event.accept()

    if __name__ == "__main__":
        import sys
        from PyQt6.QtWidgets import QApplication

        camera_ids = CameraIds()
        if camera_ids.find_first_camera():
            print(f'Camera OK')
            device = camera_ids.camera_device

        # Test with a Thread
        app = QApplication(sys.argv)
        main_window = MainWindow()
        main_window.set_camera(camera_ids)
        main_window.show()
        sys.exit(app.exec())


        ''' # Test image by image
        try:
            print(camera_ids.get_cam_info())
            camera_ids.init_camera()
            camera_ids.alloc_memory()
    
            numberOfImagesToGrab = 2
            camera_ids.start_acquisition()
    
            for k in range(numberOfImagesToGrab):
                raw_image = camera_ids.get_image()
                color_image = raw_image.ConvertTo(ids_ipl.PixelFormatName_Mono8)
                picture = color_image.get_numpy_3D()
                picture_shape = picture.shape
                # Access the image data.
                print("SizeX: ", picture_shape[1])
                print("SizeY: ", picture_shape[0])
                print("Gray value of first pixel: ", picture[0, 0])
    
                cv2.imshow('image', picture)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
    
            camera_ids.stop_acquisition()
            camera_ids.free_memory()
    
        except Exception as e:
            print("EXCEPTION: " + str(e))
    
        finally:
            ids_peak.Library.Close()
    
        '''