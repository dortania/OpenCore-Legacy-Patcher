import wx
import wx.adv
import logging
import py_sip_xnu
import pprint
import subprocess

from resources.wx_gui import gui_support

from resources import constants, global_settings, defaults
from data import model_array, sip_data, smbios_data

class SettingsFrame(wx.Frame):
    """
    Modal-based Settings Frame
    """
    def __init__(self, parent: wx.Frame, title: str, global_constants: constants.Constants, screen_location: tuple = None):
        self.constants: constants.Constants = global_constants
        self.title: str = title
        self.parent: wx.Frame = parent

        self.hyperlink_colour = (25, 179, 231)

        self.settings = self._settings()

        self.frame_modal = wx.Dialog(parent, title=title, size=(600, 750))

        self._generate_elements(self.frame_modal)
        self.frame_modal.ShowWindowModal()

    def _generate_elements(self, frame: wx.Frame = None) -> None:
        """
        Generates elements for the Settings Frame
        Uses wx.Notebook to implement a tabbed interface
        and relies on 'self._settings()' for populating
        """

        notebook = wx.Notebook(frame)
        notebook.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer(10)

        model_label = wx.StaticText(frame, label="Target Model", pos=(-1, -1))
        model_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        sizer.Add(model_label, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        model_choice = wx.Choice(frame, choices=model_array.SupportedSMBIOS + ["Host Model"], pos=(-1, -1))
        model_choice.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        model_choice.Bind(wx.EVT_CHOICE, lambda event: self.on_model_choice(event, model_choice))
        selection = self.constants.custom_model if self.constants.custom_model else "Host Model"
        model_choice.SetSelection(model_choice.FindString(selection))
        sizer.Add(model_choice, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        model_description = wx.StaticText(frame, label="Overrides Mac Model Patcher will build for.", pos=(-1, -1))
        model_description.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        sizer.Add(model_description, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        tabs = list(self.settings.keys())
        if gui_support.CheckProperties(self.constants).host_is_non_metal(general_check=True) is False:
            tabs.remove("Non-Metal")
        for tab in tabs:
            panel = wx.Panel(notebook)
            notebook.AddPage(panel, tab)

        sizer.Add(notebook, 1, wx.EXPAND | wx.ALL, 10)

        # Add return button
        return_button = wx.Button(frame, label="Return", pos=(-1, -1), size=(100, 30))
        return_button.Bind(wx.EVT_BUTTON, self.on_return)
        return_button.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
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
                    title.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))

                    title.SetPosition((int(horizontal_center) - int(title.GetSize()[0] / 2) - 15, height))
                    highest_height_reached = height + title.GetSize()[1] + 10
                    height += title.GetSize()[1] + 10
                    continue

                if setting_info["type"] == "wrap_around":
                    height = highest_height_reached
                    width = 300 if width is stock_width else stock_width
                    continue

                if setting_info["type"] == "checkbox":
                    # Add checkbox, and description underneath
                    checkbox = wx.CheckBox(panel, label=setting, pos=(10 + width, 10 + height), size = (300,-1))
                    checkbox.SetValue(setting_info["value"] if setting_info["value"] else False)
                    checkbox.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
                    event = lambda event, warning=setting_info["warning"] if "warning" in setting_info else "", override=bool(setting_info["override_function"]) if "override_function" in setting_info else False: self.on_checkbox(event, warning, override)
                    checkbox.Bind(wx.EVT_CHECKBOX, event)

                elif setting_info["type"] == "spinctrl":
                    # Add spinctrl, and description underneath
                    spinctrl = wx.SpinCtrl(panel, value=str(setting_info["value"]), pos=(width - 20, 10 + height), min=setting_info["min"], max=setting_info["max"], size = (45,-1))
                    spinctrl.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
                    spinctrl.Bind(wx.EVT_TEXT, lambda event, variable=setting: self.on_spinctrl(event, variable))
                    # Add label next to spinctrl
                    label = wx.StaticText(panel, label=setting, pos=(spinctrl.GetSize()[0] + width - 16, spinctrl.GetPosition()[1]))
                    label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
                elif setting_info["type"] == "combobox":
                    # Add combobox, and description underneath
                    combobox = wx.ComboBox(panel, value=setting_info["value"], pos=(width + 20, 10 + height), choices=setting_info["choices"], size = (100,-1))
                    combobox.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
                    combobox.Bind(wx.EVT_COMBOBOX, lambda event, variable=setting: self.on_combobox(event, variable))
                    height += 10
                else:
                    raise Exception("Invalid setting type")

                lines = '\n'.join(setting_info["description"])
                description = wx.StaticText(panel, label=lines, pos=(30 + width, 10 + height + 20))
                description.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
                height += 40 if setting_info["type"] != "combobox" else 60



                # Check number of lines in description, and adjust spacer accordingly
                description_lines = len(lines.split('\n'))
                if description_lines > 1:
                    height += (description_lines) * 11

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
                },
                "XHCI Booting": {
                    "type": "checkbox",
                    "value": self.constants.xhci_boot,
                    "variable": "xhci_boot",
                    "description": [
                        "Enable booting macOS from add-in",
                        "USB 3.0 expansion cards.",
                    ],
                },
                "NVMe Booting": {
                    "type": "checkbox",
                    "value": self.constants.nvme_boot,
                    "variable": "nvme_boot",
                    "description": [
                        "Enable booting macOS from NVMe",
                        "drives.",
                        "Note: Requires Firmware support",
                        "for OpenCore to load from NVMe.",
                    ],
                },
                "Wake on WLAN": {
                    "type": "checkbox",
                    "value": self.constants.enable_wake_on_wlan,
                    "variable": "enable_wake_on_wlan",
                    "description": [
                        "Disabled by default due to",
                        "performance degradation",
                        "on some systems from wake.",
                    ],
                },
                "wrap_around 2": {
                    "type": "wrap_around",
                },
                "Content Caching": {
                    "type": "checkbox",
                    "value": self.constants.set_content_caching,
                    "variable": "set_content_caching",
                    "description": [
                        "Enable Content Caching.",
                    ],
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
                "Show Boot Picker": {
                    "type": "checkbox",
                    "value": self.constants.showpicker,
                    "variable": "showpicker",
                    "description": [
                        "Show OpenCore boot picker",
                        "When disabled, users can hold ESC to",
                        "show picker in the firmware.",
                    ],
                },
                "Boot Picker Timeout": {
                    "type": "spinctrl",
                    "value": self.constants.oc_timeout,
                    "variable": "oc_timeout",
                    "description": [
                        "Timeout for OpenCore boot picker",
                        "in seconds.",
                        "Set to 0 for no timeout.",
                    ],

                    "min": 0,
                    "max": 60,
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
            "Advanced": {
                "Miscellaneous": {
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
                },
                "Nvidia GOP Injection": {
                    "type": "checkbox",
                    "value": self.constants.nvidia_kepler_gop_injection,
                    "variable": "nvidia_kepler_gop_injection",
                    "description": [
                        "Inject Nvidia Kepler GOP for boot",
                        "screen support on PC GPUs.",
                    ],
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
                "wrap_around 1": {
                    "type": "wrap_around",
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
                },
                "3rd Party NVMe PM": {
                    "type": "checkbox",
                    "value": self.constants.allow_nvme_fixing,
                    "variable": "allow_nvme_fixing",
                    "description": [
                        "Enable 3rd party NVMe power",
                        "management in macOS.",
                    ],
                },
                "3rd Party SATA PM": {
                    "type": "checkbox",
                    "value": self.constants.allow_3rd_party_drives,
                    "variable": "allow_3rd_party_drives",
                    "description": [
                        "Enable 3rd party SATA power",
                        "management in macOS.",
                    ],
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
                },
                "wrap_around 1": {
                    "type": "wrap_around",
                },
                "Disable ColorSync Downgrade": {
                    "type": "checkbox",
                    "value": global_settings.GlobalEnviromentSettings().read_property("Disable_ColorSync_Downgrade") or self.constants.disable_cat_colorsync,
                    "variable": "Disable_ColorSync_Downgrade",
                    "constants_variable": "disable_cat_colorsync",
                    "description": [
                        "Disable ColorSync downgrade",
                        "on HD3000 GPUs in Ventura and newer.",
                        "Note: Disabling can cause UI corruption.",
                    ],
                },
            },
            "SMBIOS": {
                "Model Spoofing": {
                    "type": "title",
                },
                "SMBIOS Spoof Level": {
                    "type": "combobox",
                    "choices": [
                        "None",
                        "Minimal",
                        "Moderate",
                        "Advanced",
                    ],
                    "value": self.constants.serial_settings,
                    "variable": "serial_settings",
                    "description": [
                        "Set SMBIOS spoofing level.",
                        "Levels are as follows:",
                        "   - None: No spoofing.",
                        "   - Minimal: Overrides Board ID.",
                        "   - Moderate: Overrides Model.",
                        "   - Advanced: Overrides Model and serial.",
                    ],
                },

                "SMBIOS Spoof Model": {
                    "type": "combobox",
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
                "Allow native spoofing": {
                    "type": "checkbox",
                    "value": self.constants.allow_native_spoofs,
                    "variable": "allow_native_spoofs",
                    "description": [
                        "Allow OpenCore to spoof to",
                        "natively supported Macs.",
                        "Primarily used for enabling",
                        "Universal Control.",
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
            "Non-Metal": {
                "SkyLight Configuration": {
                    "type": "title",
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
                        "Ignore app updates",
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
                "Disable Unused KDKs": {
                    "type": "checkbox",
                    "value": global_settings.GlobalEnviromentSettings().read_property("ShouldNukeKDKs") or self.constants.should_nuke_kdks,
                    "variable": "ShouldNukeKDKs",
                    "constants_variable": "should_nuke_kdks",
                    "description": [
                        "When enabled, the app will remove",
                        "unused KDKs from the system during",
                        "root patching.",
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
        self.parent.model_label.Center(wx.HORIZONTAL)

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
        sip_label = wx.StaticText(panel, label="Flip individual bits corresponding to", pos=(sip_title.GetPosition()[0] - 20
                                                                                             , sip_title.GetPosition()[1] + 30))
        sip_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))

        # Hyperlink: csr.h
        sip_csr_h = wx.adv.HyperlinkCtrl(panel, id=wx.ID_ANY, label="XNU's csr.h", url="https://github.com/apple-oss-distributions/xnu/blob/xnu-8020.101.4/bsd/sys/csr.h", pos=(sip_label.GetPosition()[0] + sip_label.GetSize()[0] + 5, sip_label.GetPosition()[1] + 1))
        sip_csr_h.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
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
        sip_configured_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        self.sip_configured_label = sip_configured_label

        # Label: SIP Status
        sip_booted_label = wx.StaticText(panel, label=f"Currently booted SIP: {hex(py_sip_xnu.SipXnu().get_sip_status().value)}", pos=(sip_configured_label.GetPosition()[0] + 34
            , sip_configured_label.GetPosition()[1] + 20))
        sip_booted_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))


        # SIP toggles
        entries_per_row = len(sip_data.system_integrity_protection.csr_values) // 2
        horizontal_spacer = 15
        vertical_spacer = 25
        index = 0
        for sip_bit in sip_data.system_integrity_protection.csr_values_extended:
            self.sip_checkbox = wx.CheckBox(panel, label=sip_data.system_integrity_protection.csr_values_extended[sip_bit]["name"].split("CSR_")[1], pos = (vertical_spacer, sip_booted_label.GetPosition()[1] + 20 + horizontal_spacer))
            self.sip_checkbox.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
            self.sip_checkbox.SetToolTip(f'Description: {sip_data.system_integrity_protection.csr_values_extended[sip_bit]["description"]}\nValue: {hex(sip_data.system_integrity_protection.csr_values_extended[sip_bit]["value"])}\nIntroduced in: macOS {sip_data.system_integrity_protection.csr_values_extended[sip_bit]["introduced_friendly"]}')

            if self.sip_value & sip_data.system_integrity_protection.csr_values_extended[sip_bit]["value"] == sip_data.system_integrity_protection.csr_values_extended[sip_bit]["value"]:
                self.sip_checkbox.SetValue(True)

            horizontal_spacer += 20
            if index == entries_per_row:
                horizontal_spacer = 20
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
        custom_serial_number_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))

        # Textbox: Custom Serial Number
        custom_serial_number_textbox = wx.TextCtrl(panel, pos=(custom_serial_number_label.GetPosition()[0] - 27, custom_serial_number_label.GetPosition()[1] + 20), size=(200, 25))
        custom_serial_number_textbox.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        custom_serial_number_textbox.SetToolTip("Enter a custom serial number here. This will be used for the SMBIOS and iMessage.\n\nNote: This will not be used if the \"Use Custom Serial Number\" checkbox is not checked.")
        custom_serial_number_textbox.Bind(wx.EVT_TEXT, self.on_custom_serial_number_textbox)
        self.custom_serial_number_textbox = custom_serial_number_textbox

        # Label: Custom Board Serial Number
        custom_board_serial_number_label = wx.StaticText(panel, label="Custom Board Serial Number", pos=(title.GetPosition()[0] + 120, custom_serial_number_label.GetPosition()[1]))
        custom_board_serial_number_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))

        # Textbox: Custom Board Serial Number
        custom_board_serial_number_textbox = wx.TextCtrl(panel, pos=(custom_board_serial_number_label.GetPosition()[0] - 5, custom_serial_number_textbox.GetPosition()[1]), size=(200, 25))
        custom_board_serial_number_textbox.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        custom_board_serial_number_textbox.SetToolTip("Enter a custom board serial number here. This will be used for the SMBIOS and iMessage.\n\nNote: This will not be used if the \"Use Custom Board Serial Number\" checkbox is not checked.")
        custom_board_serial_number_textbox.Bind(wx.EVT_TEXT, self.on_custom_board_serial_number_textbox)
        self.custom_board_serial_number_textbox = custom_board_serial_number_textbox

        # Button: Generate Serial Number (below)
        generate_serial_number_button = wx.Button(panel, label=f"Generate S/N: {self.constants.custom_model or self.constants.computer.real_model}", pos=(title.GetPosition()[0] - 30, custom_board_serial_number_label.GetPosition()[1] + 60), size=(200, 25))
        generate_serial_number_button.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
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

Commit Information:
    Branch: {self.constants.commit_info[0]}
    Date: {self.constants.commit_info[1]}
    URL: {self.constants.commit_info[2] if self.constants.commit_info[2] != "" else "N/A"}

Booted Information:
    Booted OS: XNU {self.constants.detected_os} ({self.constants.detected_os_version})
    Booted Patcher Version: {self.constants.computer.oclp_version}
    Booted OpenCore Version: {self.constants.computer.opencore_version}

Hardware Information:
    {pprint.pformat(self.constants.computer, indent=4)}
"""
        # TextCtrl: properties
        self.app_stats = wx.TextCtrl(panel, value=lines, pos=(-1, title.GetPosition()[1] + 30), size=(600, 320), style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_RICH2)
        self.app_stats.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))


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
        if override_function is True:
            print("Override function")
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


    def _update_global_settings(self, variable, value, global_setting = None):
        logging.info(f"Updating Global Setting: {variable} = {value}")
        global_settings.GlobalEnviromentSettings().write_property(variable, value)
        if global_setting is not None:
            self._update_setting(global_setting, value)


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
        elif hex(self.sip_value) == "0x803":
            self.constants.custom_sip_value = None
            self.constants.sip_status = False
        else:
            self.constants.custom_sip_value = hex(self.sip_value)

        self.sip_configured_label.SetLabel(f"Currently configured SIP: {hex(self.sip_value)}")

    def on_combobox(self, event: wx.Event, label: str) -> None:
        """
        """
        value = event.GetEventObject().GetValue()
        self._update_setting(self.settings[self._find_parent_for_key(label)][label]["variable"], value)


    def on_generate_serial_number(self, event: wx.Event) -> None:
        dlg = wx.MessageDialog(self.frame_modal, "Please take caution when using serial spoofing. This should only be used on machines that were legally obtained and require reserialization.\n\nNote: new serials are only overlayed through OpenCore and are not permanently installed into ROM.\n\nMisuse of this setting can break power management and other aspects of the OS if the system does not need spoofing\n\nDortania does not condone the use of our software on stolen devices.\n\nAre you certain you want to continue?", "Warning", wx.YES_NO | wx.ICON_WARNING | wx.NO_DEFAULT)
        if dlg.ShowModal() != wx.ID_YES:
            return

        macserial_output = subprocess.run([self.constants.macserial_path] + f"-g -m {self.constants.custom_model or self.constants.computer.real_model} -n 1".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        macserial_output = macserial_output.stdout.decode().strip().split(" | ")
        if len(macserial_output) == 2:
            self.custom_serial_number_textbox.SetValue(macserial_output[0])
            self.custom_board_serial_number_textbox.SetValue(macserial_output[1])
        else:
            wx.MessageBox(f"Failed to generate serial number:\n\n{macserial_output}", "Error", wx.OK | wx.ICON_ERROR)


    def on_custom_serial_number_textbox(self, event: wx.Event) -> None:
        self.constants.custom_serial_number = event.GetEventObject().GetValue()


    def on_custom_board_serial_number_textbox(self, event: wx.Event) -> None:
        self.constants.custom_board_serial_number = event.GetEventObject().GetValue()


    def on_return(self, event):
        self.frame_modal.Destroy()