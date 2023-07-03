# Installation

1. Do steps 1-3 from [Installation for developers](https://pybpod.readthedocs.io/en/v1.8.1/getting-started/install.html#installation-for-developers)

2. Verify

```bash
echo $CONDA_DEFAULT_ENV
```

yields

```
pybpod-environment
```

3. Verify the executable is inside the conda environment path. E.g.

```bash
which pip
```

yields

```
/home/USER/anaconda3/envs/pybpod-environment/bin/pip
```

4. Upgrade pip

```bash
pip install --upgrade pip
```

5. Clone pybpod

```bash
git clone --recurse-submodules -j8 https://github.com/ckarageorgkaneen/pybpod <REPONAME>
```

or 

```bash
git clone https://github.com/ckarageorgkaneen/pybpod <REPONAME>
git submodule update --init --recursive
```

6. Install pybpod

```bash
cd <REPONAME>
python utils/install.py  # may take a few minutes
cd base/pybpod
pip install -e .
```

# Setting up the protocol in PyBpod

1. Open the PyBpod GUI

```bash
start-pybpod
```
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/520fb3cd-6d37-4749-9103-3b93f2294cc7)


2. Click `New`

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/b9db7442-3b70-4379-811c-b6fbd115b53c)

after which you will see the `Projects` tab populated as such:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/e5ecd9dd-013b-47a6-90eb-b1bd28520024)

3. Right click on `Experiments`, `Subjects`, `Bpod Boards` and `Users` and add one of each, naming the items as you wish (e.g. `mouse2afc_...`)

4. Right click on the newly created experiment and add a setup:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/42b70fd9-c1ad-4cf2-9a0b-0898317c4275)

5. Click `Save` to save your project to a `PROJECT_FOLDER` of your choice:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/30171cc8-2b02-4a99-8a0a-3651f7266e9e)

6. In the `Projects` tab, select the protocol you created. It should look like this:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/ec14ca8d-28da-4dc0-a2c5-68ffd833429f)

7. Paste the following code:

```python
#!/usr/bin/env python3
import os
import sys
sys.path.append('MOUSE2AFC_PATH')
from pybpodapi.protocol import Bpod
from mouse2afc import Mouse2AFC
bpod = Bpod(emulator_mode=True)
Mouse2AFC(bpod).run()
```

replace `MOUSE2AFC_PATH` with the path of your `mouse2afc` repository (e.g. `/home/chris/Software/mouse2afc`)

8. Click `Save`, then click `Options` and then `Edit user settings`:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/1f972368-d0bc-47d6-8718-40f27c3ab29b)

Paste the following settings:

```python
SETTINGS_PRIORITY = 0

GENERIC_EDITOR_PLUGINS_LIST = ['pybpodgui_plugin', 'pybpod_gui_plugin_emulator']

PYBPOD_SESSION_PATH = 'PYBPOD_SESSION_PATH' 

TARGET_BPOD_FIRMWARE_VERSION = "22"
EMULATOR_BPOD_MACHINE_TYPE = 1

BPOD_BNC_PORTS_ENABLED = [True,True]
BPOD_WIRED_PORTS_ENABLED = [True, True, True, True]
BPOD_BEHAVIOR_PORTS_ENABLED = [True, True, True, False, False, False, False, False]
```

replace `PYBPOD_SESSION_PATH` with the path of the folder you want the session to be saved into (e.g. /home/chris/Documents/mouse2afc_sessions)

9. Click `Save` and close the program.

# Running the protocol in PyBpod

1. Run `start-pybpod`
2. In the GUI window click `Open` and navigate to your `PROJECT_FOLDER`
3. In the `Projects` tab, go to `Boards`, select the board you created and on the `Details` tab check `Emulator mode`:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/7809599d-46c5-4739-a510-5864528de451)

If the details tab does not load this information, save the project, close the project by right clicking on the project name and selecting `Close` and reopen the project with the `Open` button. If this doesn't work, quit the program and restart. 

4. Click `Console`:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/f45ca25c-d40c-445d-95c0-a035906b040f)

You can achieve the same result my double clicking your board in the projects tab.

5. In the `Project` tab, go to `Subjects` and select the subject you created. Click `Setup` and select the setup you would like this mouse to use:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/84446c72-5937-4bf5-8560-7803e965e5f6)

6. Similarly, go to your setup, and click `Board` and `Procotol` in the details tab to choose your board and protocol for that experiment:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/3d1c80de-2167-493e-9109-680f7dbce6d7)

7. In the `Details` tab, click `Add Subject` to select the subject(s) for this experiment

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/06ecbe8c-5bf7-43ac-a276-2811031674c6)

8. Click `Test Protocol IO`:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/73be05f0-3e50-4502-a6b0-262d61112716)

and the following GUI window should pop up:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/5e342cfb-a4fa-4bab-8282-5acb75497535)

9. Click `Save`, click `Run`, select the appropriate parameters in the protocol parameter GUI, click `Ok` and the protocol should run. Then any of the `Poke` check boxes of your choice to poke in and out like a mouse would:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/b3d15233-307a-4d39-b265-526eb7508ab7)

10. When done using, click `Kill`, and `Save`.
