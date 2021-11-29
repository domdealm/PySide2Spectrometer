import cv2


def returnCameraIndexes():
    # checks the first 10 indexes.
        index = 0
        arr = []
        i = 10
        while i > 0:
            cap = cv2.VideoCapture(index)
            if cap.read()[0]:
                arr.append(index)
                cap.release()
            index += 1
            i -= 1
        return arr

# Colar no ui_MainPage:
        # self.List = returnCameraIndexes()
        # for i in range(len(self.List)):
        #     self.CamList.addItem(f"Camera {i}")
        #     self.CamList2.addItem(f"Camera {i}")


