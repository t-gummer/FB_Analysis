# FB_Analysis

Python program to analyse Facebook (FB) messenger data from JSON extracts. It currently can be run for an individual
conversation or all conversations, like the example in main.py. The plan is to develop a console app and then eventually
an executable with a GUI, to enable a user to drill down into their data.

### Contents

* **main.py:** primary point of execution for the program, currently contains inputs specific to my dataset. Add another
  string with the name of a specific Facebook friend to only process the conversation between the user and the specified
  friend
  <br><br>

* **convo.py:** defines the Convo (Conversation) class. There is one instance per conversation. There is currently no
  difference between individual conversations and group chats. This is also currently where the output generation
  methods are stored.
  <br><br>

* **convo_reader.py:** the class responsible for extracting data from the FB json extracts and building the Convo class
  <br><br>

* **convo_visualisation.py:** the module which houses all functions responsible for graphing the data. It is intended to
  be abstracted from the original format of the data and only loosely coupled with the Convo class
  <br><br>

* **test_convo.py:** this is the test harness, using the unittest package, to test the **convo.py** file. It is
  currently out of date.

### Prerequisites

* **Python** version 3.10.6

* **Facebook data file** in **JSON* format. For instructions on how to download:
  [How do I download a copy of my information on Facebook?](https://www.facebook.com/help/212802592074644?rdrhc)

* **FFMpeg** Version: 2023-05-15-git-2953ebe7b6-full_build-www.gyan.dev For instructions on how to install:
  [How to install FFMpeg](https://www.linkedin.com/pulse/step-solve-common-error-racing-bar-chart-ffmpeg-available-yang/)
