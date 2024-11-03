"""
gui_settings.py: Settings Frame for the GUI
"""

import wx
import wx.adv
import pprint
import logging
import py_sip_xnu
import subprocess

from pathlib import Path

from .. import constants

from ..sys_patch import sys_patch

from ..wx_gui import (
    gui_support,
    gui_update
)
from ..support import (
    global_settings,
    defaults,
    generate_smbios,
    network_handler,
    subprocess_wrapper
)
from ..datasets import (
    model_array,
    sip_data,
    smbios_data,
    os_data,
    cpu_data
)


class SettingsFrame(wx.Frame):
    """
    Modal-based Settings Frame
    """
    def __init__(self, parent: wx.Frame, title: str, global_constants: constants.Constants, screen_location: tuple = None):
        logging.info("Initializing Settings Frame")
        self.constants: constants.Constants = global_constants
        self.title: str = title
        self.parent: wx.Frame = parent

        self.hyperlink_colour = (25, 179, 231)

        self.settings = self._settings()

        self.frame_modal = wx.Dialog(parent, title=title, size=(600, 685))

        self._generate_elements(self.frame_modal)
        self.frame_modal.ShowWindowModal()

    def _generate_elements(self, frame: wx.Frame = None) -> None:
        """
        Generates elements for the Settings Frame
        Uses wx.Notebook to implement a tabbed interface
        and relies on 'self._settings()' for populating
        """

        notebook = wx.Notebook(frame)
        notebook.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer(10)

        model_label = wx.StaticText(frame, label="Target Model", pos=(-1, -1))
        model_label.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_BOLD))
        sizer.Add(model_label, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        model_choice = wx.Choice(frame, choices=model_array.SupportedSMBIOS + ["Host Model"], pos=(-1, -1), size=(150, -1))
        model_choice.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
        model_choice.Bind(wx.EVT_CHOICE, lambda event: self.on_model_choice(event, model_choice))
        selection = self.constants.custom_model if self.constants.custom_model else "Host Model"
        model_choice.SetSelection(model_choice.FindString(selection))
        sizer.Add(model_choice, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        model_description = wx.StaticText(frame, label="Overrides Mac Model the Patcher will build for.", pos=(-1, -1))
        model_description.SetFont(gui_support.font_factory(11, wx.FONTWEIGHT_NORMAL))
        sizer.Add(model_description, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        tabs = list(self.settings.keys())
        if not Path("~/.dortania_developer").expanduser().exists():
            tabs.remove("Developer")
        for tab in tabs:
            panel = wx.Panel(notebook)
            notebook.AddPage(panel, tab)

        sizer.Add(notebook, 1, wx.EXPAND | wx.ALL, 10)

        # Add return button
        return_button = wx.Button(frame, label="Return", pos=(-1, -1), size=(100, 30))
        return_button.Bind(wx.EVT_BUTTON, self.on_return)
        return_button.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
        sizer.Add(return_button, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        frame.SetSizer(sizer)

        horizontal_center = frame.GetSize()[0] / 2
        for tab in tabs:
            if tab not in self.settings:
                continue

            stock_height = 0
            stock_width = 20

            height = stock_height
            width = stock_width

            lowest_height_reached = height
            highest_height_reached = height

            panel = notebook.GetPage(tabs.index(tab))

            for setting, setting_info in self.settings[tab].items():
                if setting_info["type"] == "populate":
                    # execute populate function
                    if setting_info["args"] == wx.Frame:
                        setting_info["function"](panel)
                    else:
                        raise Exception("Invalid populate function")
                    continue

                if setting_info["type"] == "title":
                    stock_height = lowest_height_reached
                    height = stock_height
                    width = stock_width

                    height += 10

                    # Add title
                    title = wx.StaticText(panel, label=setting, pos=(-1, -1))
                    title.SetFont(gui_support.font_factory(19, wx.FONTWEIGHT_BOLD))

                    title.SetPosition((int(horizontal_center) - int(title.GetSize()[0] / 2) - 15, height))
                    highest_height_reached = height + title.GetSize()[1] + 10
                    height += title.GetSize()[1] + 10
                    continue

                if setting_info["type"] == "sub_title":
                    # Add sub-title
                    sub_title = wx.StaticText(panel, label=setting, pos=(-1, -1))
                    sub_title.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))

                    sub_title.SetPosition((int(horizontal_center) - int(sub_title.GetSize()[0] / 2) - 15, height))
                    highest_height_reached = height + sub_title.GetSize()[1] + 10
                    height += sub_title.GetSize()[1] + 10
                    continue

                if setting_info["type"] == "wrap_around":
                    height = highest_height_reached
                    width = 300 if width is stock_width else stock_width
                    continue

                if setting_info["type"] == "checkbox":
                    # Add checkbox, and description underneath
                    checkbox = wx.CheckBox(panel, label=setting, pos=(10 + width, 10 + height), size = (300,-1))

                    value = False
                    if "value" in setting_info:
                        try:
                            value = bool(setting_info["value"])
                        except ValueError:
                            logging.error(f"Invalid value for {setting}, got {setting_info['value']} (type: {type(setting_info['value'])})")
                            value = False

                    checkbox.SetValue(value)
                    checkbox.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_BOLD))
                    event = lambda event, warning=setting_info["warning"] if "warning" in setting_info else "", override=bool(setting_info["override_function"]) if "override_function" in setting_info else False: self.on_checkbox(event, warning, override)
                    checkbox.Bind(wx.EVT_CHECKBOX, event)
                    if "condition" in setting_info:
                        checkbox.Enable(setting_info["condition"])
                        if setting_info["condition"] is False:
                            checkbox.SetValue(False)

                elif setting_info["type"] == "spinctrl":
                    # Add spinctrl, and description underneath
                    spinctrl = wx.SpinCtrl(panel, value=str(setting_info["value"]), pos=(width - 20, 10 + height), min=setting_info["min"], max=setting_info["max"], size = (45,-1))
                    spinctrl.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_BOLD))
                    spinctrl.Bind(wx.EVT_TEXT, lambda event, variable=setting: self.on_spinctrl(event, variable))
                    # Add label next to spinctrl
                    label = wx.StaticText(panel, label=setting, pos=(spinctrl.GetSize()[0] + width - 16, spinctrl.GetPosition()[1]))
                    label.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_BOLD))
                elif setting_info["type"] == "choice":
                    # Title
                    title = wx.StaticText(panel, label=setting, pos=(width + 30, 10 + height))
                    title.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_BOLD))
                    height += title.GetSize()[1] + 10

                    # Add combobox, and description underneath
                    choice = wx.Choice(panel, pos=(width + 25, 10 + height), choices=setting_info["choices"], size = (150,-1))
                    choice.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
                    choice.SetSelection(choice.FindString(setting_info["value"]))
                    if "override_function" in setting_info:
                        choice.Bind(wx.EVT_CHOICE, lambda event, variable=setting: self.settings[tab][variable]["override_function"](event))
                    else:
                        choice.Bind(wx.EVT_CHOICE, lambda event, variable=setting: self.on_choice(event, variable))
                    height += 10
                elif setting_info["type"] == "button":
                    button = wx.Button(panel, label=setting, pos=(width + 25, 10 + height), size = (200,-1))
                    button.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
                    button.Bind(wx.EVT_BUTTON, lambda event, variable=setting: self.settings[tab][variable]["function"](event))
                    height += 10

                else:
                    raise Exception("Invalid setting type")

                lines = '\n'.join(setting_info["description"])
                description = wx.StaticText(panel, label=lines, pos=(30 + width, 10 + height + 20))
                description.SetFont(gui_support.font_factory(11, wx.FONTWEIGHT_NORMAL))
                height += 40
                if "condition" in setting_info:
                    if setting_info["condition"] is False:
                        description.SetForegroundColour((128, 128, 128))

                # Check number of lines in description, and adjust spacer accordingly
                for i, line in enumerate(lines.split('\n')):
                    if line == "":
                        continue
                    if i == 0:
                        height += 11
                    else:
                        height += 13

                if height > lowest_height_reached:
                    lowest_height_reached = height


    def _settings(self) -> dict:
        """
        Generates a dictionary of settings to be used in the GUI
        General format:
        {
            "Tab Name": {
                "type": "title" | "checkbox" | "spinctrl" | "populate" | "wrap_around",
                "value": bool | int | str,
                "variable": str,  (Variable name)
                "constants_variable": str, (Constants variable name, if different from "variable")
                "description": [str, str, str], (List of strings)
                "warning": str, (Optional) (Warning message to be displayed when checkbox is checked)
                "override_function": function, (Optional) (Function to be executed when checkbox is checked)
            }
        }
        """

        models = [model for model in smbios_data.smbios_dictionary if "_" not in model and " " not in model and smbios_data.smbios_dictionary[model]["Board ID"] is not None]
        socketed_imac_models = ["iMac9,1", "iMac10,1", "iMac11,1", "iMac11,2", "iMac11,3", "iMac12,1", "iMac12,2"]
        socketed_gpu_models = socketed_imac_models + ["MacPro3,1", "MacPro4,1", "MacPro5,1", "Xserve2,1", "Xserve3,1"]

        settings = {
            "Build": {
                "General": {
                    "type": "title",
                },
                "FireWire Booting": {
                    "type": "checkbox",
                    "value": self.constants.firewire_boot,
                    "variable": "firewire_boot",
                    "description": [
                        "Enable booting macOS from",
                        "FireWire drives.",
                    ],
                    "condition": not (generate_smbios.check_firewire(self.constants.custom_model or self.constants.computer.real_model) is False)
                },
                "XHCI Booting": {
                    "type": "checkbox",
                    "value": self.constants.xhci_boot,
                    "variable": "xhci_boot",
                    "description": [
                        "Enable booting macOS from add-in",
                        "USB 3.0 expansion cards on systems",
                        "without native support.",
                    ],
                    "condition": not gui_support.CheckProperties(self.constants).host_has_cpu_gen(cpu_data.CPUGen.ivy_bridge) # Sandy Bridge and older do not natively support XHCI booting
                },
                "NVMe Booting": {
                    "type": "checkbox",
                    "value": self.constants.nvme_boot,
                    "variable": "nvme_boot",
                    "description": [
                        "Enable booting macOS from NVMe",
                        "drives on systems without native",
                        "support.",
                        "Note: Requires Firmware support",
                        "for OpenCore to load from NVMe.",
                    ],
                    "condition": not gui_support.CheckProperties(self.constants).host_has_cpu_gen(cpu_data.CPUGen.ivy_bridge) # Sandy Bridge and older do not natively support NVMe booting
                },
                "wrap_around 2": {
                    "type": "wrap_around",
                },
                "OpenCore Vaulting": {
                    "type": "checkbox",
                    "value": self.constants.vault,
                    "variable": "vault",
                    "description": [
                        "Digitally sign OpenCore to prevent",
                        "tampering or corruption."
                    ],
                },

                "Show OpenCore Boot Picker": {
                    "type": "checkbox",
                    "value": self.constants.showpicker,
                    "variable": "showpicker",
                    "description": [
                        "When disabled, users can hold ESC to",
                        "show picker in the firmware.",
                    ],
                },
                "Boot Picker Timeout": {
                    "type": "spinctrl",
                    "value": self.constants.oc_timeout,
                    "variable": "oc_timeout",
                    "description": [
                        "Timeout before boot picker selects default",
                        "entry in seconds.",
                        "Set to 0 for no timeout.",
                    ],

                    "min": 0,
                    "max": 60,
                },
                "MacPro3,1/Xserve2,1 Workaround": {
                    "type": "checkbox",
                    "value": self.constants.force_quad_thread,
                    "variable": "force_quad_thread",
                    "description": [
                        "Limits to 4 threads max on these units.",
                        "Required for macOS Sequoia and later.",
                    ],
                    "condition": (self.constants.custom_model and self.constants.custom_model in ["MacPro3,1", "Xserve2,1"]) or self.constants.computer.real_model in ["MacPro3,1", "Xserve2,1"]
                },
                "Debug": {
                    "type": "title",
                },

                "Verbose": {
                    "type": "checkbox",
                    "value": self.constants.verbose_debug,
                    "variable": "verbose_debug",
                    "description": [
                        "Verbose output during boot.",
                    ],

                },
                "Kext Debugging": {
                    "type": "checkbox",
                    "value": self.constants.kext_debug,
                    "variable": "kext_debug",
                    "description": [
                        "Use DEBUG variants of kexts and",
                        "enables additional kernel logging.",
                    ],
                },
                "wrap_around 1": {
                    "type": "wrap_around",
                },
                "OpenCore Debugging": {
                    "type": "checkbox",
                    "value": self.constants.opencore_debug,
                    "variable": "opencore_debug",
                    "description": [
                        "Use DEBUG variant of OpenCore",
                        "and enables additional logging.",
                    ],
                },
            },
            "Extras": {
                "General (Continued)": {
                    "type": "title",
                },
                "Wake on WLAN": {
                    "type": "checkbox",
                    "value": self.constants.enable_wake_on_wlan,
                    "variable": "enable_wake_on_wlan",
                    "description": [
                        "Disabled by default due to",
                        "performance degradation",
                        "on some systems from wake.",
                        "Only applies to BCM943224, 331,",
                        "360 and 3602 chipsets.",
                    ],
                },
                "Disable Thunderbolt": {
                    "type": "checkbox",
                    "value": self.constants.disable_tb,
                    "variable": "disable_tb",
                    "description": [
                        "For MacBookPro11,x with faulty",
                        "PCHs that may crash sporadically.",
                    ],
                    "condition": (self.constants.custom_model and self.constants.custom_model in ["MacBookPro11,1", "MacBookPro11,2", "MacBookPro11,3"]) or self.constants.computer.real_model in ["MacBookPro11,1", "MacBookPro11,2", "MacBookPro11,3"]
                },
                "Windows GMUX": {
                    "type": "checkbox",
                    "value": self.constants.dGPU_switch,
                    "variable": "dGPU_switch",
                    "description": [
                        "Allow iGPU to be exposed in Windows",
                        "for dGPU-based MacBooks.",
                    ],
                },
                "Disable CPUFriend": {
                    "type": "checkbox",
                    "value": self.constants.disallow_cpufriend,
                    "variable": "disallow_cpufriend",
                    "description": [
                        "Disables power management helper",
                        "for unsupported models.",
                    ],
                },
                "Disable mediaanalysisd service": {
                    "type": "checkbox",
                    "value": self.constants.disable_mediaanalysisd,
                    "variable": "disable_mediaanalysisd",
                    "description": [
                        "For systems that are the primary iCloud",
                        "Photo Library host with a 3802-based GPU,",
                        "this may aid in prolonged idle stability.",
                    ],
                    "condition": gui_support.CheckProperties(self.constants).host_has_3802_gpu()
                },
                "wrap_around 1": {
                    "type": "wrap_around",
                },
                "Allow AppleALC Audio": {
                    "type": "checkbox",
                    "value": self.constants.set_alc_usage,
                    "variable": "set_alc_usage",
                    "description": [
                        "Allow AppleALC to manage audio",
                        "if applicable.",
                        "Only disable if your host lacks",
                        "a GOP ROM.",
                    ],
                },
                "NVRAM WriteFlash": {
                    "type": "checkbox",
                    "value": self.constants.nvram_write,
                    "variable": "nvram_write",
                    "description": [
                        "Allow OpenCore to write to NVRAM.",
                        "Disable on systems with faulty or",
                        "degraded NVRAM.",
                    ],
                },

                "3rd Party NVMe PM": {
                    "type": "checkbox",
                    "value": self.constants.allow_nvme_fixing,
                    "variable": "allow_nvme_fixing",
                    "description": [
                        "Enable non-stock NVMe power",
                        "management in macOS.",
                    ],
                },
                "3rd Party SATA PM": {
                    "type": "checkbox",
                    "value": self.constants.allow_3rd_party_drives,
                    "variable": "allow_3rd_party_drives",
                    "description": [
                        "Enable non-stock SATA power",
                        "management in macOS.",
                    ],
                    "condition": not bool(self.constants.computer.third_party_sata_ssd is False and not self.constants.custom_model)
                },
                "APFS Trim": {
                    "type": "checkbox",
                    "value": self.constants.apfs_trim_timeout,
                    "variable": "apfs_trim_timeout",
                    "description": [
                        "Recommended for all users, however faulty",
                        "SSDs may benefit from disabling this.",
                    ],
                },
            },
            "Advanced": {
                "Miscellaneous": {
                    "type": "title",
                },
                "Disable Firmware Throttling": {
                    "type": "checkbox",
                    "value": self.constants.disable_fw_throttle,
                    "variable": "disable_fw_throttle",
                    "description": [
                        "Disables firmware-based throttling",
                        "caused by missing hardware.",
                        "Ex. Missing Display, Battery, etc.",
                    ],
                },
                "Software DeMUX": {
                    "type": "checkbox",
                    "value": self.constants.software_demux,
                    "variable": "software_demux",
                    "description": [
                        "Enable software based DeMUX",
                        "for MacBookPro8,2 and MacBookPro8,3.",
                        "Prevents faulty dGPU from turning on.",
                        "Note: Requires associated NVRAM arg:",
                        "'gpu-power-prefs'.",
                    ],
                    "warning": "This settings requires 'gpu-power-prefs' NVRAM argument to be set to '1'.\n\nIf missing and this option is toggled, the system will not boot\n\nFull command:\nnvram FA4CE28D-B62F-4C99-9CC3-6815686E30F9:gpu-power-prefs=%01%00%00%00",
                    "condition": not bool((not self.constants.custom_model and self.constants.computer.real_model not in ["MacBookPro8,2", "MacBookPro8,3"]) or (self.constants.custom_model and self.constants.custom_model not in ["MacBookPro8,2", "MacBookPro8,3"]))
                },
                "wrap_around 1": {
                    "type": "wrap_around",
                },
                "FeatureUnlock": {
                    "type": "choice",
                    "choices": [
                        "Enabled",
                        "Partial",
                        "Disabled",
                    ],
                    "value": "Enabled",
                    "variable": "",
                    "description": [
                        "Configure FeatureUnlock level.",
                        "Recommend lowering if your system",
                        "experiences memory instability.",
                    ],
                },
                "Populate FeatureUnlock Override": {
                    "type": "populate",
                    "function": self._populate_fu_override,
                    "args": wx.Frame,
                },
                "Hibernation Work-around": {
                    "type": "checkbox",
                    "value": self.constants.disable_connectdrivers,
                    "variable": "disable_connectdrivers",
                    "description": [
                        "Only load minimum EFI drivers",
                        "to prevent hibernation issues.",
                        "Note: This may break booting from",
                        "external drives.",
                    ],
                },
                "Graphics": {
                    "type": "title",
                },
                "AMD GOP Injection": {
                    "type": "checkbox",
                    "value": self.constants.amd_gop_injection,
                    "variable": "amd_gop_injection",
                    "description": [
                        "Inject AMD GOP for boot screen",
                        "support on PC GPUs.",
                    ],
                    "condition": not bool((not self.constants.custom_model and self.constants.computer.real_model not in socketed_gpu_models) or (self.constants.custom_model and self.constants.custom_model not in socketed_gpu_models))
                },
                "Nvidia GOP Injection": {
                    "type": "checkbox",
                    "value": self.constants.nvidia_kepler_gop_injection,
                    "variable": "nvidia_kepler_gop_injection",
                    "description": [
                        "Inject Nvidia Kepler GOP for boot",
                        "screen support on PC GPUs.",
                    ],
                    "condition": not bool((not self.constants.custom_model and self.constants.computer.real_model not in socketed_gpu_models) or (self.constants.custom_model and self.constants.custom_model not in socketed_gpu_models))
                },
                "wrap_around 2": {
                    "type": "wrap_around",
                },
                "Graphics Override": {
                    "type": "choice",
                    "choices": [
                        "None",
                        "Nvidia Kepler",
                        "AMD GCN",
                        "AMD Polaris",
                        "AMD Lexa",
                        "AMD Navi",
                    ],
                    "value": "None",
                    "variable": "",
                    "description": [
                        "Override detected/assumed GPU on",
                        "socketed MXM-based iMacs.",
                    ],
                    "condition": bool((not self.constants.custom_model and self.constants.computer.real_model in socketed_imac_models) or (self.constants.custom_model and self.constants.custom_model in socketed_imac_models))
                },
                "Populate Graphics Override": {
                    "type": "populate",
                    "function": self._populate_graphics_override,
                    "args": wx.Frame,
                },

            },
            "Security": {
                "Kernel Security": {
                    "type": "title",
                },
                "Disable Library Validation": {
                    "type": "checkbox",
                    "value": self.constants.disable_cs_lv,
                    "variable": "disable_cs_lv",
                    "description": [
                        "Required for loading modified",
                        "system files from root patching.",
                    ],
                },
                "Disable AMFI": {
                    "type": "checkbox",
                    "value": self.constants.disable_amfi,
                    "variable": "disable_amfi",
                    "description": [
                        "Extended version of 'Disable",
                        "Library Validation', required",
                        "for systems with deeper",
                        "root patches.",
                    ],
                },
                "wrap_around 1": {
                    "type": "wrap_around",
                },
                "Secure Boot Model": {
                    "type": "checkbox",
                    "value": self.constants.secure_status,
                    "variable": "secure_status",
                    "description": [
                        "Set Apple Secure Boot Model Identifier",
                        "to matching T2 model if spoofing.",
                        "Note: Incompatible with Root Patching.",
                    ],
                },
                "System Integrity Protection": {
                    "type": "title",
                },
                "Populate SIP": {
                    "type": "populate",
                    "function": self._populate_sip_settings,
                    "args": wx.Frame,
                },
            },
            "SMBIOS": {
                "Model Spoofing": {
                    "type": "title",
                },
                "SMBIOS Spoof Level": {
                    "type": "choice",
                    "choices": [
                        "None",
                        "Minimal",
                        "Moderate",
                        "Advanced",
                    ],
                    "value": self.constants.serial_settings,
                    "variable": "serial_settings",
                    "description": [
                        "Supported Levels:",
                        "   - None: No spoofing.",
                        "   - Minimal: Overrides Board ID.",
                        "   - Moderate: Overrides Model.",
                        "   - Advanced: Overrides Model and serial.",
                    ],
                },

                "SMBIOS Spoof Model": {
                    "type": "choice",
                    "choices": models + ["Default"],
                    "value": self.constants.override_smbios,
                    "variable": "override_smbios",
                    "description": [
                        "Set Mac Model to spoof to.",
                    ],

                },
                "wrap_around 1": {
                    "type": "wrap_around",
                },
                "Allow spoofing native Macs": {
                    "type": "checkbox",
                    "value": self.constants.allow_native_spoofs,
                    "variable": "allow_native_spoofs",
                    "description": [
                        "Allow OpenCore to spoof natively",
                        "supported Macs.",
                        "Primarily used for enabling",
                        "Universal Control on unsupported Macs",
                    ],
                },
                "Serial Spoofing": {
                    "type": "title",
                },
                "Populate Serial Spoofing": {
                    "type": "populate",
                    "function": self._populate_serial_spoofing_settings,
                    "args": wx.Frame,
                },
            },
            "Root Patching": {
                "Root Volume Patching": {
                    "type": "title",
                },
                "TeraScale 2 Acceleration": {
                    "type": "checkbox",
                    "value": global_settings.GlobalEnviromentSettings().read_property("MacBookPro_TeraScale_2_Accel") or self.constants.allow_ts2_accel,
                    "variable": "MacBookPro_TeraScale_2_Accel",
                    "constants_variable": "allow_ts2_accel",
                    "description": [
                        "Enable AMD TeraScale 2 GPU",
                        "Acceleration on MacBookPro8,2 and",
                        "MacBookPro8,3.",
                        "By default this is disabled due to",
                        "common GPU failures on these models.",
                    ],
                    "override_function": self._update_global_settings,
                    "condition": not bool(self.constants.computer.real_model not in ["MacBookPro8,2", "MacBookPro8,3"])
                },
                "wrap_around 1": {
                    "type": "wrap_around",
                },
                "Non-Metal Configuration": {
                    "type": "title",
                },
                "Log out required to apply changes to SkyLight": {
                    "type": "sub_title",
                },
                "Dark Menu Bar": {
                    "type": "checkbox",
                    "value": self._get_system_settings("Moraea_DarkMenuBar"),
                    "variable": "Moraea_DarkMenuBar",
                    "description": [
                        "If Beta Menu Bar is enabled,",
                        "menu bar colour will dynamically",
                        "change as needed.",
                    ],
                    "override_function": self._update_system_defaults,
                    "condition": gui_support.CheckProperties(self.constants).host_is_non_metal(general_check=True)
                },
                "Beta Blur": {
                    "type": "checkbox",
                    "value": self._get_system_settings("Moraea_BlurBeta"),
                    "variable": "Moraea_BlurBeta",
                    "description": [
                        "Control window blur behaviour.",
                    ],
                    "override_function": self._update_system_defaults,
                    "condition": gui_support.CheckProperties(self.constants).host_is_non_metal(general_check=True)

                },
                "Beach Ball Cursor Workaround": {
                    "type": "checkbox",
                    "value": self._get_system_settings("Moraea.EnableSpinHack"),
                    "variable": "Moraea.EnableSpinHack",
                    "description": [
                        "Control beach ball cursor behaviour.",
                    ],
                    "override_function": self._update_system_defaults_root,
                    "condition": gui_support.CheckProperties(self.constants).host_is_non_metal(general_check=True)
                },
                "wrap_around 2": {
                    "type": "wrap_around",
                },
                "Beta Menu Bar": {
                    "type": "checkbox",
                    "value": self._get_system_settings("Amy.MenuBar2Beta"),
                    "variable": "Amy.MenuBar2Beta",
                    "description": [
                        "Supports dynamic colour changes.",
                        "Note: Setting is still experimental.",
                        "If you experience issues, please",
                        "disable this setting.",
                    ],
                    "override_function": self._update_system_defaults,
                    "condition": gui_support.CheckProperties(self.constants).host_is_non_metal(general_check=True)
                },
                "Disable Beta Rim": {
                    "type": "checkbox",
                    "value": self._get_system_settings("Moraea_RimBetaDisabled"),
                    "variable": "Moraea_RimBetaDisabled",
                    "description": [
                        "Control Window Rim rendering.",
                    ],
                    "override_function": self._update_system_defaults,
                    "condition": gui_support.CheckProperties(self.constants).host_is_non_metal(general_check=True)
                },
                "Disable Color Widgets Enforcement": {
                    "type": "checkbox",
                    "value": self._get_system_settings("Moraea_ColorWidgetDisabled"),
                    "variable": "Moraea_ColorWidgetDisabled",
                    "description": [
                        "Control Color Desktop Widgets Enforcement.",
                    ],
                    "override_function": self._update_system_defaults,
                    "condition": gui_support.CheckProperties(self.constants).host_is_non_metal(general_check=True)
                },
            },
            "App": {
                "General": {
                    "type": "title",
                },
                "Allow native models": {
                    "type": "checkbox",
                    "value": self.constants.allow_oc_everywhere,
                    "variable": "allow_oc_everywhere",
                    "description": [
                        "Allow OpenCore to be installed",
                        "on natively supported Macs.",
                        "Note this will not allow unsupported",
                        "macOS versions to be installed on",
                        "your system.",
                    ],
                    "warning": "This option should only be used if your Mac natively supports the OSes you wish to run.\n\nIf you are currently running an unsupported OS, this option will break booting. Only toggle for enabling OS features on a native Mac.\n\nAre you certain you want to continue?",
                },
                "Ignore App Updates": {
                    "type": "checkbox",
                    "value": global_settings.GlobalEnviromentSettings().read_property("IgnoreAppUpdates") or self.constants.ignore_updates,
                    "variable": "IgnoreAppUpdates",
                    "constants_variable": "ignore_updates",
                    "description": [
                        # "Ignore app updates",
                    ],
                    "override_function": self._update_global_settings,
                },
                "wrap_around 1": {
                    "type": "wrap_around",
                },
                "Disable Reporting": {
                    "type": "checkbox",
                    "value": global_settings.GlobalEnviromentSettings().read_property("DisableCrashAndAnalyticsReporting"),
                    "variable": "DisableCrashAndAnalyticsReporting",
                    "description": [
                        "When enabled, patcher will not",
                        "report any info to Dortania.",
                    ],
                    "override_function": self._update_global_settings,
                },
                "Remove Unused KDKs": {
                    "type": "checkbox",
                    "value": global_settings.GlobalEnviromentSettings().read_property("ShouldNukeKDKs") or self.constants.should_nuke_kdks,
                    "variable": "ShouldNukeKDKs",
                    "constants_variable": "should_nuke_kdks",
                    "description": [
                        "When enabled, the app will remove",
                        "unused Kernel Debug Kits from the system",
                        "during root patching.",
                    ],
                    "override_function": self._update_global_settings,
                },
                "Statistics": {
                    "type": "title",
                },
                "Populate Stats": {
                    "type": "populate",
                    "function": self._populate_app_stats,
                    "args": wx.Frame,
                },
            },
            "Developer": {
                "Validation": {
                    "type": "title",
                },
                "Install latest nightly build 🧪": {
                    "type": "button",
                    "function": self.on_nightly,
                    "description": [
                        "If you're already here, I assume you're ok",
                        "bricking your system 🧱.",
                        "Check CHANGELOG before blindly updating.",
                    ],
                },
                "Trigger Exception": {
                    "type": "button",
                    "function": self.on_test_exception,
                    "description": [
                    ],
                },
                "wrap_around 1": {
                    "type": "wrap_around",
                },
                "Export constants": {
                    "type": "button",
                    "function": self.on_export_constants,
                    "description": [
                        "Export constants.py values to a txt file.",
                    ],
                },

                "Developer Root Volume Patching": {
                    "type": "title",
                },
                "Mount Root Volume": {
                    "type": "button",
                    "function": self.on_mount_root_vol,
                    "description": [
                        "Life's too short to type 'sudo mount -o",
                        "nobrowse -t apfs /dev/diskXsY",
                        "/System/Volumes/Update/mnt1' every time.",
                    ],
                },
                "wrap_around 2": {
                    "type": "wrap_around",
                },
                "Save Root Volume": {
                    "type": "button",
                    "function": self.on_bless_root_vol,
                    "description": [
                        "Rebuild kernel cache and bless snapshot 🙏",
                    ],
                },
            },
        }

        return settings


    def on_model_choice(self, event: wx.Event, model_choice: wx.Choice) -> None:
        """
        Sets model to use for patching.
        """

        selection = model_choice.GetStringSelection()
        if selection == "Host Model":
            selection = self.constants.computer.real_model
            self.constants.custom_model = None
            logging.info(f"Using Real Model: {self.constants.computer.real_model}")
            defaults.GenerateDefaults(self.constants.computer.real_model, True, self.constants)
        else:
            logging.info(f"Using Custom Model: {selection}")
            self.constants.custom_model = selection
            defaults.GenerateDefaults(self.constants.custom_model, False, self.constants)
            self.parent.build_button.Enable()



        self.parent.model_label.SetLabel(f"Model: {selection}")
        self.parent.model_label.Centre(wx.HORIZONTAL)

        self.frame_modal.Destroy()
        SettingsFrame(
            parent=self.parent,
            title=self.title,
            global_constants=self.constants,
            screen_location=self.parent.GetPosition()
        )


    def _populate_sip_settings(self, panel: wx.Frame) -> None:

        horizontal_spacer = 250

        # Look for title on frame
        sip_title: wx.StaticText = None
        for child in panel.GetChildren():
            if child.GetLabel() == "System Integrity Protection":
                sip_title = child
                break


        # Label: Flip individual bits corresponding to XNU's csr.h
        # If you're unfamiliar with how SIP works, do not touch this menu
        sip_label = wx.StaticText(panel, label="Flip individual bits corresponding to", pos=(sip_title.GetPosition()[0] - 20, sip_title.GetPosition()[1] + 30))
        sip_label.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))

        # Hyperlink: csr.h
        spacer = 1 if self.constants.detected_os >= os_data.os_data.big_sur else 3
        sip_csr_h = wx.adv.HyperlinkCtrl(panel, id=wx.ID_ANY, label="XNU's csr.h", url="https://github.com/apple-oss-distributions/xnu/blob/xnu-8020.101.4/bsd/sys/csr.h", pos=(sip_label.GetPosition()[0] + sip_label.GetSize()[0] + 4, sip_label.GetPosition()[1] + spacer))
        sip_csr_h.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
        sip_csr_h.SetHoverColour(self.hyperlink_colour)
        sip_csr_h.SetNormalColour(self.hyperlink_colour)
        sip_csr_h.SetVisitedColour(self.hyperlink_colour)

        # Label: SIP Status
        if self.constants.custom_sip_value is not None:
            self.sip_value = int(self.constants.custom_sip_value, 16)
        elif self.constants.sip_status is True:
            self.sip_value = 0x00
        else:
            self.sip_value = 0x803
        sip_configured_label = wx.StaticText(panel, label=f"Currently configured SIP: {hex(self.sip_value)}", pos=(sip_label.GetPosition()[0] + 35, sip_label.GetPosition()[1] + 20))
        sip_configured_label.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_BOLD))
        self.sip_configured_label = sip_configured_label

        # Label: SIP Status
        sip_booted_label = wx.StaticText(panel, label=f"Currently booted SIP: {hex(py_sip_xnu.SipXnu().get_sip_status().value)}", pos=(sip_configured_label.GetPosition()[0], sip_configured_label.GetPosition()[1] + 20))
        sip_booted_label.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))


        # SIP toggles
        entries_per_row = len(sip_data.system_integrity_protection.csr_values) // 2
        horizontal_spacer = 15
        vertical_spacer = 25
        index = 1
        for sip_bit in sip_data.system_integrity_protection.csr_values_extended:
            self.sip_checkbox = wx.CheckBox(panel, label=sip_data.system_integrity_protection.csr_values_extended[sip_bit]["name"].split("CSR_")[1], pos = (vertical_spacer, sip_booted_label.GetPosition()[1] + 20 + horizontal_spacer))
            self.sip_checkbox.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
            self.sip_checkbox.SetToolTip(f'Description: {sip_data.system_integrity_protection.csr_values_extended[sip_bit]["description"]}\nValue: {hex(sip_data.system_integrity_protection.csr_values_extended[sip_bit]["value"])}\nIntroduced in: macOS {sip_data.system_integrity_protection.csr_values_extended[sip_bit]["introduced_friendly"]}')

            if self.sip_value & sip_data.system_integrity_protection.csr_values_extended[sip_bit]["value"] == sip_data.system_integrity_protection.csr_values_extended[sip_bit]["value"]:
                self.sip_checkbox.SetValue(True)

            horizontal_spacer += 20
            if index == entries_per_row:
                horizontal_spacer = 15
                vertical_spacer += 250

            index += 1
            self.sip_checkbox.Bind(wx.EVT_CHECKBOX, self.on_sip_value)


    def _populate_serial_spoofing_settings(self, panel: wx.Frame) -> None:
        title: wx.StaticText = None
        for child in panel.GetChildren():
            if child.GetLabel() == "Serial Spoofing":
                title = child
                break

        # Label: Custom Serial Number
        custom_serial_number_label = wx.StaticText(panel, label="Custom Serial Number", pos=(title.GetPosition()[0] - 150, title.GetPosition()[1] + 30))
        custom_serial_number_label.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_BOLD))

        # Textbox: Custom Serial Number
        custom_serial_number_textbox = wx.TextCtrl(panel, pos=(custom_serial_number_label.GetPosition()[0] - 27, custom_serial_number_label.GetPosition()[1] + 20), size=(200, 25))
        custom_serial_number_textbox.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
        custom_serial_number_textbox.SetToolTip("Enter a custom serial number here. This will be used for the SMBIOS and iMessage.\n\nNote: This will not be used if the \"Use Custom Serial Number\" checkbox is not checked.")
        custom_serial_number_textbox.Bind(wx.EVT_TEXT, self.on_custom_serial_number_textbox)
        custom_serial_number_textbox.SetValue(self.constants.custom_serial_number)
        self.custom_serial_number_textbox = custom_serial_number_textbox

        # Label: Custom Board Serial Number
        custom_board_serial_number_label = wx.StaticText(panel, label="Custom Board Serial Number", pos=(title.GetPosition()[0] + 120, custom_serial_number_label.GetPosition()[1]))
        custom_board_serial_number_label.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_BOLD))

        # Textbox: Custom Board Serial Number
        custom_board_serial_number_textbox = wx.TextCtrl(panel, pos=(custom_board_serial_number_label.GetPosition()[0] - 5, custom_serial_number_textbox.GetPosition()[1]), size=(200, 25))
        custom_board_serial_number_textbox.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
        custom_board_serial_number_textbox.SetToolTip("Enter a custom board serial number here. This will be used for the SMBIOS and iMessage.\n\nNote: This will not be used if the \"Use Custom Board Serial Number\" checkbox is not checked.")
        custom_board_serial_number_textbox.Bind(wx.EVT_TEXT, self.on_custom_board_serial_number_textbox)
        custom_board_serial_number_textbox.SetValue(self.constants.custom_board_serial_number)
        self.custom_board_serial_number_textbox = custom_board_serial_number_textbox

        # Button: Generate Serial Number (below)
        generate_serial_number_button = wx.Button(panel, label=f"Generate S/N: {self.constants.custom_model or self.constants.computer.real_model}", pos=(title.GetPosition()[0] - 30, custom_board_serial_number_label.GetPosition()[1] + 60), size=(200, 25))
        generate_serial_number_button.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))
        generate_serial_number_button.Bind(wx.EVT_BUTTON, self.on_generate_serial_number)


    def _populate_app_stats(self, panel: wx.Frame) -> None:
        title: wx.StaticText = None
        for child in panel.GetChildren():
            if child.GetLabel() == "Statistics":
                title = child
                break

        lines = f"""Application Information:
    Application Version: {self.constants.patcher_version}
    PatcherSupportPkg Version: {self.constants.patcher_support_pkg_version}
    Application Path: {self.constants.launcher_binary}
    Application Mount: {self.constants.payload_path}

Commit Information:
    Branch: {self.constants.commit_info[0]}
    Date: {self.constants.commit_info[1]}
    URL: {self.constants.commit_info[2] if self.constants.commit_info[2] != "" else "N/A"}

Booted Information:
    Booted OS: XNU {self.constants.detected_os} ({self.constants.detected_os_version})
    Booted Patcher Version: {self.constants.computer.oclp_version}
    Booted OpenCore Version: {self.constants.computer.opencore_version}
    Booted OpenCore Disk: {self.constants.booted_oc_disk}

Hardware Information:
    {pprint.pformat(self.constants.computer, indent=4)}
"""
        # TextCtrl: properties
        self.app_stats = wx.TextCtrl(panel, value=lines, pos=(-1, title.GetPosition()[1] + 30), size=(600, 240), style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_RICH2)
        self.app_stats.SetFont(gui_support.font_factory(13, wx.FONTWEIGHT_NORMAL))


    def on_checkbox(self, event: wx.Event, warning_pop: str = "", override_function: bool = False) -> None:
        """
        """
        label = event.GetEventObject().GetLabel()
        value = event.GetEventObject().GetValue()
        if warning_pop != "" and value is True:
            warning = wx.MessageDialog(self.frame_modal, warning_pop, f"Warning: {label}", wx.YES_NO | wx.ICON_WARNING | wx.NO_DEFAULT)
            if warning.ShowModal() == wx.ID_NO:
                event.GetEventObject().SetValue(not event.GetEventObject().GetValue())
                return
            if label == "Allow native models":
                if self.constants.computer.real_model in smbios_data.smbios_dictionary:
                    if self.constants.detected_os > smbios_data.smbios_dictionary[self.constants.computer.real_model]["Max OS Supported"]:
                        chassis_type = "aluminum"
                        if self.constants.computer.real_model in ["MacBook5,2", "MacBook6,1", "MacBook7,1"]:
                            chassis_type = "plastic"
                        dlg = wx.MessageDialog(self.frame_modal, f"This model, {self.constants.computer.real_model}, does not natively support macOS {os_data.os_conversion.kernel_to_os(self.constants.detected_os)}, {os_data.os_conversion.convert_kernel_to_marketing_name(self.constants.detected_os)}. The last native OS was macOS {os_data.os_conversion.kernel_to_os(smbios_data.smbios_dictionary[self.constants.computer.real_model]['Max OS Supported'])}, {os_data.os_conversion.convert_kernel_to_marketing_name(smbios_data.smbios_dictionary[self.constants.computer.real_model]['Max OS Supported'])}\n\nToggling this option will break booting on this OS. Are you absolutely certain this is desired?\n\nYou may end up with a nice {chassis_type} brick 🧱", "Are you certain?", wx.YES_NO | wx.ICON_WARNING | wx.NO_DEFAULT)
                        if dlg.ShowModal() == wx.ID_NO:
                            event.GetEventObject().SetValue(not event.GetEventObject().GetValue())
                            return
        if override_function is True:
            self.settings[self._find_parent_for_key(label)][label]["override_function"](self.settings[self._find_parent_for_key(label)][label]["variable"], value, self.settings[self._find_parent_for_key(label)][label]["constants_variable"] if "constants_variable" in self.settings[self._find_parent_for_key(label)][label] else None)
            return

        self._update_setting(self.settings[self._find_parent_for_key(label)][label]["variable"], value)
        if label == "Allow native models":
            if gui_support.CheckProperties(self.constants).host_can_build() is True:
                self.parent.build_button.Enable()
            else:
                self.parent.build_button.Disable()


    def on_spinctrl(self, event: wx.Event, label: str) -> None:
        """
        """
        value = event.GetEventObject().GetValue()
        self._update_setting(self.settings[self._find_parent_for_key(label)][label]["variable"], value)


    def _update_setting(self, variable, value):
        logging.info(f"Updating Local Setting: {variable} = {value}")
        setattr(self.constants, variable, value)
        tmp_value = value
        if tmp_value is None:
            tmp_value = "PYTHON_NONE_VALUE"
        global_settings.GlobalEnviromentSettings().write_property(f"GUI:{variable}", tmp_value)


    def _update_global_settings(self, variable, value, global_setting = None):
        logging.info(f"Updating Global Setting: {variable} = {value}")
        tmp_value = value
        if tmp_value is None:
            tmp_value = "PYTHON_NONE_VALUE"
        global_settings.GlobalEnviromentSettings().write_property(variable, tmp_value)
        if global_setting is not None:
            self._update_setting(global_setting, value)


    def _update_system_defaults(self, variable, value, global_setting = None):
        value_type = type(value)
        if value_type is str:
            value_type = "-string"
        elif value_type is int:
            value_type = "-int"
        elif value_type is bool:
            value_type = "-bool"

        logging.info(f"Updating System Defaults: {variable} = {value} ({value_type})")
        subprocess.run(["/usr/bin/defaults", "write", "-globalDomain", variable, value_type, str(value)])


    def _update_system_defaults_root(self, variable, value, global_setting = None):
        value_type = type(value)
        if value_type is str:
            value_type = "-string"
        elif value_type is int:
            value_type = "-int"
        elif value_type is bool:
            value_type = "-bool"

        logging.info(f"Updating System Defaults (root): {variable} = {value} ({value_type})")
        subprocess_wrapper.run_as_root(["/usr/bin/defaults", "write", "/Library/Preferences/.GlobalPreferences.plist", variable, value_type, str(value)])


    def _find_parent_for_key(self, key: str) -> str:
        for parent in self.settings:
            if key in self.settings[parent]:
                return parent


    def on_sip_value(self, event: wx.Event) -> None:
        """
        """
        dict = sip_data.system_integrity_protection.csr_values_extended[f"CSR_{event.GetEventObject().GetLabel()}"]

        if event.GetEventObject().GetValue() is True:
            self.sip_value = self.sip_value + dict["value"]
        else:
            self.sip_value = self.sip_value - dict["value"]

        if hex(self.sip_value) == "0x0":
            self.constants.custom_sip_value = None
            self.constants.sip_status = True
            global_settings.GlobalEnviromentSettings().write_property("GUI:custom_sip_value", "PYTHON_NONE_VALUE")
            global_settings.GlobalEnviromentSettings().write_property("GUI:sip_status", True)
        elif hex(self.sip_value) == "0x803":
            self.constants.custom_sip_value = None
            self.constants.sip_status = False
            global_settings.GlobalEnviromentSettings().write_property("GUI:custom_sip_value", "PYTHON_NONE_VALUE")
            global_settings.GlobalEnviromentSettings().write_property("GUI:sip_status", False)
        else:
            self.constants.custom_sip_value = hex(self.sip_value)
            global_settings.GlobalEnviromentSettings().write_property("GUI:custom_sip_value", hex(self.sip_value))

        self.sip_configured_label.SetLabel(f"Currently configured SIP: {hex(self.sip_value)}")

    def on_choice(self, event: wx.Event, label: str) -> None:
        """
        """
        value = event.GetString()
        self._update_setting(self.settings[self._find_parent_for_key(label)][label]["variable"], value)


    def on_generate_serial_number(self, event: wx.Event) -> None:
        dlg = wx.MessageDialog(self.frame_modal, "Please take caution when using serial spoofing. This should only be used on machines that were legally obtained and require reserialization.\n\nNote: new serials are only overlayed through OpenCore and are not permanently installed into ROM.\n\nMisuse of this setting can break power management and other aspects of the OS if the system does not need spoofing\n\nDortania does not condone the use of our software on stolen devices.\n\nAre you certain you want to continue?", "Warning", wx.YES_NO | wx.ICON_WARNING | wx.NO_DEFAULT)
        if dlg.ShowModal() != wx.ID_YES:
            return

        macserial_output = subprocess.run([self.constants.macserial_path, "--generate", "--model", self.constants.custom_model or self.constants.computer.real_model, "--num", "1"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        macserial_output = macserial_output.stdout.decode().strip().split(" | ")
        if len(macserial_output) == 2:
            self.custom_serial_number_textbox.SetValue(macserial_output[0])
            self.custom_board_serial_number_textbox.SetValue(macserial_output[1])
        else:
            wx.MessageBox(f"Failed to generate serial number:\n\n{macserial_output}", "Error", wx.OK | wx.ICON_ERROR)


    def on_custom_serial_number_textbox(self, event: wx.Event) -> None:
        self.constants.custom_serial_number = event.GetEventObject().GetValue()
        global_settings.GlobalEnviromentSettings().write_property("GUI:custom_serial_number", self.constants.custom_serial_number)


    def on_custom_board_serial_number_textbox(self, event: wx.Event) -> None:
        self.constants.custom_board_serial_number = event.GetEventObject().GetValue()
        global_settings.GlobalEnviromentSettings().write_property("GUI:custom_board_serial_number", self.constants.custom_board_serial_number)


    def _populate_fu_override(self, panel: wx.Panel) -> None:
        gpu_combo_box: wx.Choice = None
        for child in panel.GetChildren():
            if isinstance(child, wx.Choice):
                gpu_combo_box = child
                break

        gpu_combo_box.Bind(wx.EVT_CHOICE, self.fu_selection_click)
        if self.constants.fu_status is False:
            gpu_combo_box.SetStringSelection("Disabled")
        elif self.constants.fu_arguments is None or self.constants.fu_arguments == "":
            gpu_combo_box.SetStringSelection("Enabled")
        else:
            gpu_combo_box.SetStringSelection("Partial")


    def fu_selection_click(self, event: wx.Event) -> None:
        value = event.GetEventObject().GetStringSelection()
        if value == "Enabled":
            logging.info("Updating FU Status: Enabled")
            self.constants.fu_status = True
            self.constants.fu_arguments = None
            global_settings.GlobalEnviromentSettings().write_property("GUI:fu_status", True)
            global_settings.GlobalEnviromentSettings().write_property("GUI:fu_arguments", "PYTHON_NONE_VALUE")
            return

        if value == "Partial":
            logging.info("Updating FU Status: Partial")
            self.constants.fu_status = True
            self.constants.fu_arguments = " -disable_sidecar_mac"
            global_settings.GlobalEnviromentSettings().write_property("GUI:fu_status", True)
            global_settings.GlobalEnviromentSettings().write_property("GUI:fu_arguments", " -disable_sidecar_mac")
            return

        logging.info("Updating FU Status: Disabled")
        self.constants.fu_status = False
        self.constants.fu_arguments = None
        global_settings.GlobalEnviromentSettings().write_property("GUI:fu_status", False)
        global_settings.GlobalEnviromentSettings().write_property("GUI:fu_arguments", "PYTHON_NONE_VALUE")


    def _populate_graphics_override(self, panel: wx.Panel) -> None:
        gpu_combo_box: wx.Choice = None
        index = 0
        for child in panel.GetChildren():
            if isinstance(child, wx.Choice):
                if index == 0:
                    index = index + 1
                    continue
                gpu_combo_box = child
                break

        gpu_combo_box.Bind(wx.EVT_CHOICE, self.gpu_selection_click)
        gpu_combo_box.SetStringSelection(f"{self.constants.imac_vendor} {self.constants.imac_model}")

        socketed_gpu_models = ["iMac9,1", "iMac10,1", "iMac11,1", "iMac11,2", "iMac11,3", "iMac12,1", "iMac12,2"]
        if ((not self.constants.custom_model and self.constants.computer.real_model not in socketed_gpu_models) or (self.constants.custom_model and self.constants.custom_model not in socketed_gpu_models)):
            gpu_combo_box.Disable()
            return


    def gpu_selection_click(self, event: wx.Event) -> None:
        gpu_choice = event.GetEventObject().GetStringSelection()

        logging.info(f"Updating GPU Selection: {gpu_choice}")
        if "AMD" in gpu_choice:
            self.constants.imac_vendor = "AMD"
            self.constants.metal_build = True
            if "Polaris" in gpu_choice:
                self.constants.imac_model = "Polaris"
            elif "GCN" in gpu_choice:
                self.constants.imac_model = "GCN"
            elif "Lexa" in gpu_choice:
                self.constants.imac_model = "Lexa"
            elif "Navi" in gpu_choice:
                self.constants.imac_model = "Navi"
            else:
                raise Exception("Unknown GPU Model")
            global_settings.GlobalEnviromentSettings().write_property("GUI:imac_vendor", "AMD")
            global_settings.GlobalEnviromentSettings().write_property("GUI:metal_build", True)
            global_settings.GlobalEnviromentSettings().write_property("GUI:imac_model", self.constants.imac_model)
        elif "Nvidia" in gpu_choice:
            self.constants.imac_vendor = "Nvidia"
            self.constants.metal_build = True
            if "Kepler" in gpu_choice:
                self.constants.imac_model = "Kepler"
            elif "GT" in gpu_choice:
                self.constants.imac_model = "GT"
            else:
                raise Exception("Unknown GPU Model")
            global_settings.GlobalEnviromentSettings().write_property("GUI:imac_vendor", "Nvidia")
            global_settings.GlobalEnviromentSettings().write_property("GUI:metal_build", True)
            global_settings.GlobalEnviromentSettings().write_property("GUI:imac_model", self.constants.imac_model)
        else:
            self.constants.imac_vendor = "None"
            self.constants.metal_build = False
            global_settings.GlobalEnviromentSettings().write_property("GUI:imac_vendor", "None")
            global_settings.GlobalEnviromentSettings().write_property("GUI:metal_build", False)


    def _get_system_settings(self, variable) -> bool:
        result = subprocess.run(["/usr/bin/defaults", "read", "-globalDomain", variable], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.returncode == 0:
            try:
                return bool(int(result.stdout.decode().strip()))
            except:
                return False
        return False


    def on_return(self, event):
        self.frame_modal.Destroy()


    def on_nightly(self, event: wx.Event) -> None:
        # Ask prompt for which branch
        branches = ["main"]
        if self.constants.commit_info[0] not in ["Running from source", "Built from source"]:
            branches = [self.constants.commit_info[0].split("/")[-1]]
        result = network_handler.NetworkUtilities().get("https://api.github.com/repos/dortania/OpenCore-Legacy-Patcher/branches")
        if result is not None:
            result = result.json()
            for branch in result:
                if branch["name"] == "gh-pages":
                    continue
                if branch["name"] not in branches:
                    branches.append(branch["name"])

            with wx.SingleChoiceDialog(self.parent, "Which branch would you like to download?", "Branch Selection", branches) as dialog:
                if dialog.ShowModal() == wx.ID_CANCEL:
                    return

                branch = dialog.GetStringSelection()
        else:
            branch = "main"

        gui_update.UpdateFrame(
            parent=self.parent,
            title=self.title,
            global_constants=self.constants,
            screen_location=self.parent.GetPosition(),
            url=f"https://nightly.link/dortania/OpenCore-Legacy-Patcher/workflows/build-app-wxpython/{branch}/OpenCore-Patcher.pkg.zip",
            version_label="(Nightly)"
        )


    def on_export_constants(self, event: wx.Event) -> None:
        # Throw pop up to get save location
        with wx.FileDialog(self.parent, "Save Constants File", wildcard="JSON files (*.txt)|*.txt", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT, defaultFile=f"constants-{self.constants.patcher_version}.txt") as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            # Save the current contents in the file
            pathname = fileDialog.GetPath()
            logging.info(f"Saving constants to {pathname}")
            with open(pathname, 'w') as file:
                file.write(pprint.pformat(vars(self.constants), indent=4))


    def on_test_exception(self, event: wx.Event) -> None:
        raise Exception("Test Exception")

    def on_mount_root_vol(self, event: wx.Event) -> None:
        #Don't need to pass model as we're bypassing all logic
        if sys_patch.PatchSysVolume("",self.constants)._mount_root_vol() == True:
            wx.MessageDialog(self.parent, "Root Volume Mounted, remember to fix permissions before saving the Root Volume", "Success", wx.OK | wx.ICON_INFORMATION).ShowModal()
        else:
            wx.MessageDialog(self.parent, "Root Volume Mount Failed, check terminal output", "Error", wx.OK | wx.ICON_ERROR).ShowModal()

    def on_bless_root_vol(self, event: wx.Event) -> None:
        #Don't need to pass model as we're bypassing all logic
        if sys_patch.PatchSysVolume("",self.constants)._rebuild_root_volume() == True:
            wx.MessageDialog(self.parent, "Root Volume saved, please reboot to apply changes", "Success", wx.OK | wx.ICON_INFORMATION).ShowModal()
        else:
            wx.MessageDialog(self.parent, "Root Volume update Failed, check terminal output", "Error", wx.OK | wx.ICON_ERROR).ShowModal()