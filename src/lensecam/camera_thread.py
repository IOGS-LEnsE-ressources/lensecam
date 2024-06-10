# -*- coding: utf-8 -*-
"""camera_thread file.

File containing :class::CameraThread to create a thread process able to
display images without interfering with the PyQt6 application.

This module is normally independant of the type of camera if it is used
with wrappers contained in the lensecam package (from the LEnsE)

.. note:: LEnsE - Institut d'Optique - version 0.1

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>

"""

import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

class CameraThread(QThread):
    """

    """
    image_acquired = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.running = False
        self.camera = None
        self.stopping = False

    def set_camera(self, camera):
        """"""
        self.camera = camera

    def stop(self):
        if self.camera.camera_acquiring is True:
            self.running = False
            self.stopping = True
            while self.stopping == True:
                pass
            print('Stop 1')
            self.camera.stop_acquisition()
            print('Stop 2')
            self.camera.free_memory()
            print('Stop 3')

    def run(self):
        """
        Collect data from camera to display images.

        .. warning::

            The image must be in 8 bits mode for displaying !

        """
        try:
            if self.camera.camera_acquiring is False:
                self.camera.init_camera()
                self.camera.alloc_memory()
                self.camera.start_acquisition()
                self.running = True
            while self.running:
                image_array = self.camera.get_image()
                self.image_acquired.emit(image_array)
                self.stopping = False
        except Exception as e:
            print(f'Thread Running - Exception - {e}')
