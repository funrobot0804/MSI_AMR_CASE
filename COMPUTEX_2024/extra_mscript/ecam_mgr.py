import subprocess

class ECameraStreamingHelper:

    DEFAULT_PARAMETERS = [ "-nostdin", "-f", "v4l2",
              "-i", "/dev/video18",
              "-pix_fmt", "yuv420p", "-preset", "ultrafast", "-b:v", "9600k",
              "-an", "-f", "rtsp", "rtsp://192.168.10.103:8554/myorinurl"]

    _current_cpid = 0

    def __init__(self) -> None:
        try:
            subprocess.run(["v4l2-ctl", "-d", "/dev/video18", "-c", "brightness=90"], check=True, capture_output=True)
            subprocess.run(["v4l2-ctl", "-d", "/dev/video18", "-c", "contrast=12"], check=True, capture_output=True)
            subprocess.run(["v4l2-ctl", "-d", "/dev/video18", "-c", "saturation=96"], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            # Rush to this once exit value != 0 
            print(f"Error executing the cam init: {e}")


    def stop_ecam_streaming(self)-> int:
        """ Turn off the external camera attached to ARM and close streaming
        Args:
            None
        Returns:
            0 representing the success
            positive non-zero representing the error state
        Raises:
            None
        """
        try:
            CompletedProcess = subprocess.run(["pidof","ffmpeg"], check=True, capture_output=True)
            bytes_pids = CompletedProcess.stdout
            list_pids = bytes_pids.decode('utf-8')
            list_pids.strip()        
            dic_pids = list_pids.split()
            subprocess.run(["kill"] + dic_pids, check=True)
            print("kill execution completed.")
            return 0
        except subprocess.CalledProcessError as e:
            # Rush to this once exit value != 0 
            print(f"Error executing the kill: {e}")
            return e
    
    def start_ecam_streaming(self)-> int:
        """ Open the external camera attached to ARM and start streaming
        Args:
            None
        Returns:
            0 representing the success
            positive non-zero representing the error state
        Raises:
            None
        """

        try:
            CompletedProcess = subprocess.run(["pidof","ffmpeg"], check=True, capture_output=True)
            print(f"Cam device opened, close it first.")
            return 1
        except subprocess.CalledProcessError as e:
            print("Ok to open cam")

        process = subprocess.Popen(
            ["ffmpeg"] + self.DEFAULT_PARAMETERS ,  # The script to run
            stdout=subprocess.PIPE,  # Capture standard output
            stderr=subprocess.PIPE,   # Capture standard error
            start_new_session=True)
        self._current_cpid = process.pid
        return 0
    #end of ECameraStreamingHelper

"""
# test main part
ecam = ECameraStreamingHelper()
while True:
    user_input = input("Type something (or 'exit' to quit, even or 'exitstop' to stop quit without streaming): ")
    if user_input.lower() == 'exit':
        print("Exiting...")
        break
    elif user_input.lower() == 'start':
        ecam.start_ecam_streaming()
        pass
    elif user_input.lower() == 'stop':
        ecam.stop_ecam_streaming()
        pass
    elif user_input.lower() == 'exitstop':
        #stop_ecam_streaming()
        ecam.stop_ecam_streaming()
        break
    else:
        print(f"You typed: {user_input}")
print("Python script has completed.")
"""
