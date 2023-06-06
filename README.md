# gst-python-face-detector
This is a simple gst-python application that detects faces and greets the detected faces.

### How to run
To run the application, follow the steps below:

- Install the required dependencies by running the following command:
```bash
pip install -r requirements.txt
```
- Set the GST_PLUGIN_PATH environment variable to the current directory. This step is necessary for GStreamer to find the face_detector_py plugin. Run the following command:
```bash
export GST_PLUGIN_PATH=$PWD
```

- Launch the application using the gst-launch-1.0 command:
```bash
gst-launch-1.0 v4l2src ! videorate ! "video/x-raw,framerate=25/1" ! queue ! videoconvert ! face_detector_py ! queue ! videoconvert ! autovideosink sync=false
```

This command sets up a GStreamer pipeline that reads video frames from a v4l2src, performs face detection using the face_detector_py plugin, and displays the video with greetings using autovideosink.

Make sure you have a compatible video source connected to your system before running the command.

### Acknowledgements
This application utilizes the gst-python library and the face_detector_py plugin to enable face detection and greetings functionality.

### License
This project is licensed under the Apache License.