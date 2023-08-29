## About
This guide is a modified version of [PyBpod's Installation Guide](https://pybpod.readthedocs.io/en/v1.8.1/getting-started/install.html) specific to the Poirazi Lab's Mouse2AFC protocol. For more detail on what PyBpod is and how to use other features please see their wiki [here](https://pybpod.readthedocs.io/en/v1.8.1/index.html). 

# Installation

### 1. Create environment
Do steps 1-3 from [Installation for Developers](https://pybpod.readthedocs.io/en/v1.8.1/getting-started/install.html#installation-for-developers)

**NOTE: If using Windows 11:**
- Before executing step 2 of the Installation for Developers, open the Windows 10 yml file and delete `sqlite=3.19.3=vc14_1`,`jpeg=9b=vc14_2`,`qt=5.6.2=vc14_1`,`matplotlib=2.0.2=np113py36_0` and `tk=8.5.18=vc14_0`
- After activating the environment in step 3 of the Installatin for Developers:
```bash
conda install jpeg=9b qt=5.6.2 matplotlib=2.0.2 tk --channel conda-forge --channel anaconda --channel defaults
```

### 2. Verify conda environment is activated
```bash
conda env list
```
yields
```bash
# conda environments:
#
base                    /...
pybpod-environment     */...
```
with the asterik `*` next to `pybpod-environment`

### 3. Verify the executable is inside the conda environment path
```bash
pip --version
```
yeilds
#### Linux: 
```bash
pip 9.0.1 from /home/user/anaconda3/envs/pybpod-environment/lib/python3.6/site-packages/pip (python 3.6)
```
#### Windows:
```bash
pip 18.1 from C:\Users\user\miniconda3\envs\pybpod-environment\lib\site-packages\pip (python 3.6)
```

### 4. Upgrade pip

```bash
pip install --upgrade pip
```

### 5. Clone pybpod github respository 

```bash
git clone --recurse-submodules -j8 https://github.com/ckarageorgkaneen/pybpod <REPONAME>
```
Change`<REPONAME>` to whatever you like. The repository will be cloned into a new folder called `<REPONAME>`
### 6. Install pybpod

```bash
cd <REPONAME>
python utils/install.py  # may take a few minutes
```
### 7. Clone mouse2afc github repository
Clone outside of `<REPONAME>`
```bash
git clone https://github.com/HenryJFlynn/mouse2afc.git mouse2afc
```

### 8. Install mouse2afc
```bash
cd mouse2afc
pip install -e .
``` 

# Setting Up the Protocol in PyBpod

### 1. Start the pybpod GUI.
#### Linux:
```bash
cd <REPONAME>
python -c 'import pybpodgui_plugin.__main__ as Main; Main.start()'
```
#### Windows:
```bash
cd <REPONAME>
python -c "import pybpodgui_plugin.__main__ as Main; Main.start()"
```
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/520fb3cd-6d37-4749-9103-3b93f2294cc7)

### 2. Editing user settings
Click `Options` then `Edit user settings`. Paste the following settings:

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

replace `PYBPOD_SESSION_PATH` with the path of the folder you want the session to be saved into. (e.g. Linux: `/home/user/Documents/mouse2afc_sessions`, Windows: `"C:\\Users\\mouse2afc\\mouse2afc_sessions"`)

### 3. Save the changes
Click `Save` and close the program.

# Running the protocol in PyBpod

### 1. Run Pybpod
#### Linux:
```bash
cd <REPONAME>
python -c 'import pybpodgui_plugin.__main__ as Main; Main.start()'
```

#### Windows:
```bash
cd <REPONAME>
python -c "import pybpodgui_plugin.__main__ as Main; Main.start()"
```

### 2. Open project folder 
Click `Open` and select `pybpod-project` located in the `mouse2afc` repository folder downloaded previously. Should have something like this:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/51a90a6b-64f2-4e51-84c6-63fb1c500427)

### 3. Select user
In the `Projects` window, under `Users`, double-click on `Default-User` to select it

### 4. Select Bpod board information
In the `Projects` window, go to `Bpod boards`, select `Default-Box` then in the `Details` window select the serial port your Bpod is connected to. For Linux the serial port will look like `/dev/tty`, for Windows `COM`

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/c82364bc-c492-4ebf-941a-9869ed7d8467)


and click `Console`:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/ae4e52e0-aabc-4dc2-acc8-baae1e36198e)

### 5. Assign subjects to setup
In the `Projects` window, under `Subjects`, click on `Default-Subject`. If not already selected, click on the dropdown widget next to `Setup` and select the setup you would like this mouse to use:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/70a85f8f-8348-418d-98b2-f607a3040c9a)

### 6. Assign experiment setup, board, and protocol
Similarly, under `Default Experiment`, click on `Default-Setup` and, if not already selected, select a `Board` and `Procotol` for the experiment:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/7a90ca3f-5f96-44c5-a845-3f9e8907e121)

### 7. Add subject to setup
In the `Subjects` tab, if not already selected, click `Add Subject` to select the subject(s) for the experiment:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/42400e4e-8340-413d-8e92-098f3c65d926)

### 8. Open emulator GUI
Click `Test Protocol IO` and the following GUI window should pop up:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/4a78ee03-a3da-4ac0-9539-2801fa4a6b65)

### 9. Run the protocol using Pybpod
Click `Save`, click `Run Protocol`, select the appropriate parameters in the task parameter GUI, click `Ok` and the protocol should run. Check the boxes of your choice in the `Poke` row to emulate a mouse poking in (checked) and out (unchecked):

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/7e0afd02-d21d-4096-a843-90ff0fd3249b)

## 10. Stop the experiment
When done using, click `Stop` or `Kill`, and then `Save`.

### Note about emulator mode in Pybpod:
If you wish to test a protocol without connecting to a Bpod:
1. Instead of doing step five, check `Emulator mode`
2. Under `Protocols`, open `Mouse2AFC_` and edit line 6 to be `bpod=Bpod(emulator_mode=True`)

### Note about examples
The examples are meant to be run outside of pybpod, inside of your IDE
