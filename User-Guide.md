# User Guide for Running Mouse2AFC on PyBpod
#### The goal of this document is to provide intructions on how to install and set up pybpod to run the Mouse2AFC protocol.
#### It will be a copy of the instructions provide by [Pybpod](https://pybpod.readthedocs.io/en/v1.8.1/getting-started/install.html) but with more detail as well as some modification for this use case.

## Prerequisites for Installation
1. python 3.6
2. [Anaconda or Miniconda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/download.html)

## Installation
### 1. Setup and Activate the Virtual Environment
1. Got to the [Pybpod wesbite](https://pybpod.readthedocs.io/en/v1.8.1/getting-started/install.html) and see step 2 of installation. 
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/2f705022-145e-40f1-92d6-d42199138465)

2. Follow the intructions
     - `utils` is the folder where you downloaded the `.yml` file.
     - This step will take a couple minutes. The line in terminal `Collect package metadata (repodata.json)` should be loading
3. In terminal type `conda activate pybpod-environment` (Once step 2 finishes, the terminal should print this out and you can copy and paste it)
4. Do a `pip install --upgrade pip`

### 2. Cloning the Repository
1. Go to [this](https://github.com/ckarageorgkaneen/pybpod) Github repository
2. Click the green button labeled ` < > Code ` as seen in the image below 
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/5b579fcd-c308-4be1-8368-07a6a7a5b7e9)

3. Copy the https link                              
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/6a32a8c6-d85f-4c8c-9360-4288eaf3700e)

4. Open terminal and navigate to desired directory
5. In termal type: `git clone --recursive LINK YOUR_FOLDER”`
     - Where `LINK` is the one you just copied and `YOUR_FOLDER` which is up to you to name (just `pybpod` will be fine)
     - This step will create a folder, `FOLDER_NAME`, in the directory you nagivated to and download the repository along with its submodles into that folder
6. Navigate to where you installed the repository: `cd YOUR_FOLDER` and type: `python utils/install.py`
     - This will take a couple minutes
7. Navigate into `base/pybpod` with `cd base/pybpod` and type `pip install -e .`

## Using PyBpod
### 1. Setting Up the Protocol in PyBpod
1. Navigate to `YOUR_FOLDER` in terminal, do: `start-pybpod`. This should pop up
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/520fb3cd-6d37-4749-9103-3b93f2294cc7)

There will likely be errors/warning in terminal which look like this, they can be ignored

```python
/lib/x86_64-linux-gnu/libfontconfig.so.1: undefined symbol: FT_Done_MM_Var
ControlWeb will not work
QtWebEngine may be missing
Warning: Ignoring XDG_SESSION_TYPE=wayland on Gnome. Use QT_QPA_PLATFORM=wayland to run on Wayland anyway.
libpng warning: iCCP: known incorrect sRGB profile
15/06/2023 11:13:20 | WARNING | 7137 | pyforms_generic_editor.plugins.loader | install_plugins | Plugins path was not defined by user
libGL error: MESA-LOADER: failed to open crocus: /usr/lib/dri/crocus_dri.so: cannot open shared object file: No such file or directory (search paths /usr/lib/x86_64-linux-gnu/dri:\$${ORIGIN}/dri:/usr/lib/dri, suffix _dri)
libGL error: failed to load driver: crocus
libGL error: MESA-LOADER: failed to open swrast: /usr/lib/dri/swrast_dri.so: cannot open shared object file: No such file or directory (search paths /usr/lib/x86_64-linux-gnu/dri:\$${ORIGIN}/dri:/usr/lib/dri, suffix _dri)
libGL error: failed to load driver: swrast
```

For detailed intructions how everything works go to the [PyBpod Website](https://pybpod.readthedocs.io/en/v1.8.1/getting-started/basic-usage.html). There are many features PyBpod offers but we will not be using them. This doc will have the basics on how to get the protocol up and running.

2. In the upper left corner, select `New`                                    
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/b9db7442-3b70-4379-811c-b6fbd115b53c)

You will see in the `Projects` tab, it has been populated with this:                              
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/e5ecd9dd-013b-47a6-90eb-b1bd28520024)

3. By right clicking on `Experiments`,`Subjects`,`Bpod Boards` and `Users` you will be able to add each respective item.                       
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/adbb002a-e12f-41ac-be25-226dea92dec2)

4. Add each of these and in the newly created experiment right click once more to add a setup then select it. You should have something that looks like this:
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/42b70fd9-c1ad-4cf2-9a0b-0898317c4275)
You can go through and name each of the experiments and set ups as well as this whole project. 

5. In the upper left corner, Select `Save`                     
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/30171cc8-2b02-4a99-8a0a-3651f7266e9e)                        
This will prompt you to choose a location to save. It is suggested to save it outside of the repository, `YOUR_FOLDER`. 

6.In the `Projects` tab, right click `Protocols` and select `Add Protocol`                   
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/6f9719a9-30ce-447a-9413-93c79028d058)
You should have something that looks like this:          
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/ec14ca8d-28da-4dc0-a2c5-68ffd833429f)

7. Select inside of the task editor:        
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/77edaade-7439-42b9-aa2f-b3d75fe4fdb4)              
and paste this:
```python
#!/usr/bin/env python3
import os
import sys
sys.path.append('YOUR_PATH')
from pybpodapi.protocol import Bpod
from mouse2afc import Mouse2AFC
bpod = Bpod(emulator_mode=True)
Mouse2AFC(bpod).run()
```
8. Change `YOUR_PATH` to your systems path to the Mouse2AFC python protocol. **SHOULD I PUT MY REPO HERE??**
9. In the top left corner, select `Options` and then click `edit user settings`      
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/1f972368-d0bc-47d6-8718-40f27c3ab29b)     


`Ctrl + A`,`delete` and paste this code in:

```python
SETTINGS_PRIORITY = 0

GENERIC_EDITOR_PLUGINS_LIST = ['pybpodgui_plugin', 'pybpod_gui_plugin_emulator']

TARGET_BPOD_FIRMWARE_VERSION = "8"
EMULATOR_BPOD_MACHINE_TYPE = 1

BPOD_BNC_PORTS_ENABLED = [True,True]
BPOD_WIRED_PORTS_ENABLED = [True, True, True, True]
BPOD_BEHAVIOR_PORTS_ENABLED = [True, True, True, False, False, False, False, False]
```
Hit save. Now close the program and restart it. 

### 2. Running the Protocol
1. Navitgate to `YOUR_FOLDER' in terminal, excute `start-pybpod`
2. In the upper left corner, select `Open` and selected the project you created in the previous step
3. In the projects tab, go to boards, select the board you created then on the details tab check `Emulator mode`:
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/7809599d-46c5-4739-a510-5864528de451)
If the details tab does not load this information, save the project, close the project by right clicking on the project name and selecting `Close` and reopen the project with the `Open` button. If this doesn't work, quit the program and restart. 

4. Still there, click `Console`. You should see something like this:
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/f45ca25c-d40c-445d-95c0-a035906b040f)
You can achive the same result my double clicking your board in the projects tab

5. In the project tab, go to subjects and select the subject you created. Click `Setup` and select the setup you would like this mouse to use.
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/84446c72-5937-4bf5-8560-7803e965e5f6)

6. Similarly, go to your setup, and click `Board` and `Procotol` in the deatils tab to choose your board and Protocol for that experiment
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/3d1c80de-2167-493e-9109-680f7dbce6d7)

7. Continuing in the details tab, click `Add Subject` to select the subject(s) for this experiment
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/06ecbe8c-5bf7-43ac-a276-2811031674c6)

8. Select `Test Protocol IO`                                             
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/73be05f0-3e50-4502-a6b0-262d61112716)
and this should pop open:                       
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/5e342cfb-a4fa-4bab-8282-5acb75497535)

9. Once more it `Save`
10. Click `Run` and hit the check box to poke in and out as a mouse
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/b3d15233-307a-4d39-b265-526eb7508ab7)
11. When done using, click `Kill`, and `Save`. All the data is saved in a folder created in your subject's folder **This is vague**







