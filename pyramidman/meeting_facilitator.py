
class MeetingFacilitator():
    """Class to handle the logic of meeting facilitation.
    It basically initializes some basic information about the meeting, and then 
    - It starts the listening in a new thread. 
    - The sentences recorded are then transcribed by another thread.
    - If an event is triggered: (i.e command or long silence), another thread is created to handle it.
    """
