__all__ = [
    "camera_ids",           # refers to the 'camera_ids.py' file
    "camera_ids_widget",    # refers to the 'camera_ids_widget.py' file
    "camera_list",          # refers to the 'camera_list.py' file
]

'''
Mono12g24IDS format conversion ??

def expand(self, array: numpy.ndarray) -> numpy.ndarray:
        bytes_packed = 3  # chunks of 3 bytes
        # pixels_unpacked = 2  # give 2 pixels

        v0, v1, v2 = numpy.reshape(
            array, (array.shape[0] // bytes_packed, bytes_packed)
        ).astype(numpy.uint16).T

        """
        See Figure
        https://www.1stvision.com/cameras/IDS/IDS-manuals/en/basics-monochrome-pixel-formats.html
        Input:           v2        v1       v0
        
        Byte:            B2        B1       B0
                        |....+....|........|........|
        Pixel:           p1-0_LSB  p1_MSB   p0_MSB
                        |........+....|........+....|
        Output:          v1            v0
        
        """
        v0 = numpy.bitwise_or(
            v0 << 4,
            numpy.bitwise_and(v2, 0b000000001111)
        )
        v1 = numpy.bitwise_or(
            v1 << 4,
            numpy.bitwise_and(v2 >> 4, 0b000000001111)
        )

        return numpy.column_stack((v0, v1)).ravel()
'''