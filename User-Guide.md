# User Guide running Mouse2AFC on PyBpod
#### The goal of this doc is to provide intructions how to install and set up pybpod for the Mouse2AFC protocol.
#### It will be a copy of the instructions provide by [Pybpod](https://pybpod.readthedocs.io/en/v1.8.1/getting-started/install.html) but with more detail as well as some modification for this use case.

## Prerequisits for Installation
1. python 3.6
2. Anaconda or Miniconda

## Installation
### 1. Setup and Activate the Virtual Environment
1. Got to the [Pybpod](https://pybpod.readthedocs.io/en/v1.8.1/getting-started/install.html) website and see step 2 of installation. 
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/2f705022-145e-40f1-92d6-d42199138465)

2. Follow the intructions
     - `utils` is the folder where you downloaded the `.yml` file\
3. In terminal type `conda activate pybpod-environment` (or just `activate pybpod-environment` depending on your system) **DOUBLE CHECK**
4. Do a `pip install --upgrade pip`

### 2. Cloning the Repository
1. Go to [this](https://pybpod.readthedocs.io/en/v1.8.1/getting-started/install.html) Github repository
2. Click the green button labeled ` < > Code ` as seen in the image below 
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/5b579fcd-c308-4be1-8368-07a6a7a5b7e9)

3. Copy the https link                              
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/6a32a8c6-d85f-4c8c-9360-4288eaf3700e)

4. Open terminal and navigate to desired directory
5. In termal type: `git clone --recursive LINK YOUR_FOLDER”`
     - Where `LINK` is the one you just copied and `YOUR_FOLDER` which is up to you to name (just `pybpod` will be fine)
     - This step will create a folder, `FOLDER_NAME`, in the directory you nagivated to and download the repository along with its submodles into that folder
6. Navigate to where you installed the repository: `cd YOUR_FOLDER` and type: `python utils/install.py`
7. Navigate into `base/pybpod` in `YOUR_FOLDER` and type `pip install -e .`

### 3. Setting Up the Protocol in PyBpod
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

For detailed intructions how everything works at the [PyBpod Website](https://pybpod.readthedocs.io/en/v1.8.1/getting-started/basic-usage.html). There are many features PyBpod has but we will not be using them. This doc will have the basics on how to get the protocol up and running.

2. In the top left corner, select `New`                                    
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/b9db7442-3b70-4379-811c-b6fbd115b53c)

You will see in the `Projects` tab, it has been populated with this:                              
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/e5ecd9dd-013b-47a6-90eb-b1bd28520024)

3. By right clicking on `Experiments`,`Subjects`,`Bpod Boards` and `Users` you will be able to add each spective item.                       
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/adbb002a-e12f-41ac-be25-226dea92dec2)

4. Add each of these and in the newly created experiment right click once more to add a setup then select it. You should have something that looks like this:
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/42b70fd9-c1ad-4cf2-9a0b-0898317c4275)
On the right you can see the `Details` tab 

5. In the top left corner, Select `Save`                     
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

### Running the Protocol
1. 





