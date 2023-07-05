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
```

# Setting up the protocol in PyBpod

1. Start the PyBpod GUI

```bash
python -c 'import pybpodgui_plugin.__main__ as Main; Main.start()'
```
![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/520fb3cd-6d37-4749-9103-3b93f2294cc7)

2. Click `Options` then `Edit user settings`
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

3. Under `Protocols`, Double-click on `Mouse2AFC` and in the task editor change `MOUSE2AFC_PATH` to the path of your `mouse2afc` repository (e.g. `/home/chris/Software/mouse2afc`)

4. Click `Save` and close the program.

# Running the protocol in PyBpod

1. Run
```bash
python -c 'import pybpodgui_plugin.__main__ as Main; Main.start()'
```

2. Under `Users`, double-click on `Default-User` to select it
3. Click `Open` and select `pybpod-project` located in the `mouse2afc` repository folder downloaded previously. Should have something like this:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/a29e3bbf-4e27-4f80-83af-b46898532293)

4. In the `Projects` tab, go to `Boards`, select `Default-Box` then in the `Details` tab check `Emulator mode`:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/7191f691-f01a-455a-95c1-cb9fe6ebe303)

and click `Console`:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/853ace74-3f2d-4a55-bfaf-dec4212acd9b)

4. Under `Subjects`, click on `Default-Subject`. If not already selected, click on the dropdown widget next to `Setup` and select the setup you would like this mouse to use:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/6ca9fd5b-d7c4-442b-8962-1b971c432ff2)

5. Similarly, under `Default Experiment`, click on `Default-Setup` and, if not already selected, select a `Board` and `Procotol` for the experiment:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/45452bea-99c6-4719-aebb-9109eb637cfb)

6. In the `Subjects` tab, if not already selected, click `Add Subject` to select the subject(s) for the experiment:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/eeb7f079-f789-4ec2-bad3-f95b47f78855)

7. Click `Test Protocol IO` and the following GUI window should pop up:

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/556fd20e-d697-4404-8071-3fde4f46a7d4)

8. Click `Save`, click `Run Protocol`, select the appropriate parameters in the task parameter GUI, click `Ok` and the protocol should run. Now check the boxes of your choice in the `Poke` row to emulate a mouse poking in (checked) and out (unchecked):

![image](https://github.com/HenryJFlynn/mouse2afc/assets/130571023/86ea2444-5f34-4277-92e1-62e170f58fd4)

9. When done using, click `Stop` or `Kill`, and then `Save`.
