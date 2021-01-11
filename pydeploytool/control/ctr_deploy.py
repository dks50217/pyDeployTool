from deployer import Deployer
from time import sleep
import multiprocessing
cpus = multiprocessing.cpu_count()
import time
import os
from pydeploytool.util.util import MyUtil

from time import sleep

class Ctr_Deploy():

    cancel = False

    @staticmethod
    def init():
        Ctr_Deploy.cancel = False

    @staticmethod
    def is_operation_canceled():
        return Ctr_Deploy.cancel


    @staticmethod
    def output_progress(listener_progress, str_task, progress_percent):
        # only update progress if not requested to cancel
        if not Ctr_Deploy.cancel:
            listener_progress(str_task, progress_percent)

    @staticmethod
    def cancel_operation():
        Ctr_Deploy.cancel = True

        while Ctr_Deploy.step == 0:
            time.sleep(0.1)

        if Ctr_Deploy.step == 1:
            Ctr_Deploy.pool.close()
            Ctr_Deploy.pool.join()

        else:
            Ctr_Deploy.pool.terminate()
            Ctr_Deploy.pool.join()

    @staticmethod
    def start_deploy(
            source_path,
            listener_progress,
            output=None,
    ):

        if os.name != "nt" and "Darwin" in os.uname():
            if 'forkserver' != multiprocessing.get_start_method(allow_none=True):
                multiprocessing.set_start_method('forkserver')
        Ctr_Deploy.cancel = False
        Ctr_Deploy.step = 0
        """
        Given an input audio/video file, generate subtitles in the specified language and format.
        """
        deployer = Deployer(source_path=source_path)

        transcripts = []
        try:
            if Ctr_Deploy.cancel:
                return -1

            regions = [0,0,0,0,0]
            len_regions = len(regions)

            str_task_1 = "步驟1/1: 換版中 "
            Ctr_Deploy.pool = multiprocessing.Pool(cpus)
            for i, transcript in enumerate(Ctr_Deploy.pool.imap(deployer, regions)):
                Ctr_Deploy.step = 1
                transcripts.append(transcript)
                progress_percent = MyUtil.percentage(i, len_regions)
                Ctr_Deploy.output_progress(listener_progress, str_task_1, progress_percent)

            if Ctr_Deploy.cancel:
                return -1
            else:
                Ctr_Deploy.pool.close()
                Ctr_Deploy.pool.join()

        except KeyboardInterrupt:
            Ctr_Deploy.pbar.finish()
            Ctr_Deploy.pool.terminate()
            Ctr_Deploy.pool.join()
            raise

        if Ctr_Deploy.cancel:
            return -1
        else:
            Ctr_Deploy.pool.close()
            Ctr_Deploy.pool.join()
        return 0
