import wx
import logging

from resources.wx_gui import gui_support

from resources import constants, global_settings, defaults
from data import model_array

class SettingsFrame(wx.Frame):
    """
    """
    def __init__(self, parent: wx.Frame, title: str, global_constants: constants.Constants, screen_location: tuple = None):
        self.constants: constants.Constants = global_constants
        self.title: str = title
        self.parent: wx.Frame = parent

        self.settings = self._settings()

        self.frame_modal = wx.Dialog(parent, title=title, size=(600, 750))

        self._generate_elements(self.frame_modal)
        self.frame_modal.ShowWindowModal()

    def _generate_elements(self, frame: wx.Frame = None) -> None:

        notebook = wx.Notebook(frame)
        notebook.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer(10)

        model_label = wx.StaticText(frame, label="Target Model", pos=(-1, -1))
        model_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        sizer.Add(model_label, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        model_choice = wx.Choice(frame, choices=model_array.SupportedSMBIOS + ["Host Model"] if self.constants.computer.real_model not in model_array.SupportedSMBIOS else model_array.SupportedSMBIOS, pos=(-1, -1))
        model_choice.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        model_choice.Bind(wx.EVT_CHOICE, lambda event: self.on_model_choice(event, model_choice))
        selection = self.constants.custom_model if self.constants.custom_model else self.constants.computer.real_model
        if selection not in model_array.SupportedSMBIOS:
            selection = "Host Model"
        model_choice.SetSelection(model_choice.FindString(selection))

        sizer.Add(model_choice, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # Add label below Override Model
        model_description = wx.StaticText(frame, label="Overrides system OCLP will build for.", pos=(-1, -1))
        model_description.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        sizer.Add(model_description, 0, wx.ALIGN_CENTER | wx.ALL, 5)


        tabs = [
            "Build",
            "Advanced",
            "Security",
            "Root Patching",
            "Non-Metal",
            "SMBIOS",
            "App"
        ]
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
            stock_height = 0
            stock_width = 20

            height = stock_height
            width = stock_width
            panel = notebook.GetPage(tabs.index(tab))

            if tab not in self.settings:
                continue

            lowest_height_reached = height
            highest_height_reached = height

            for setting, setting_info in self.settings[tab].items():
                if setting_info["type"] == "populate":
                    # execute populate function
                    if setting_info["args"] == wx.Frame:
                        setting_info["function"](panel)
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
                    checkbox = wx.CheckBox(panel, label=setting, pos=(10 + width, 10 + height), size = (200,-1))
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
                else:
                    logging.critical(f"Unknown setting type: {setting_info['type']}")
                    continue

                lines = '\n'.join(setting_info["description"])
                description = wx.StaticText(panel, label=lines, pos=(30 + width, 10 + height + 20))
                description.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
                height += 40

                # Check number of lines in description, and adjust spacer accordingly
                description_lines = len(lines.split('\n'))
                if description_lines > 1:
                    height += (description_lines) * 11

                if height > lowest_height_reached:
                    lowest_height_reached = height


    def _settings(self):

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
                        "FireWire drives",
                    ],
                },
                "XHCI Booting": {
                    "type": "checkbox",
                    "value": self.constants.xhci_boot,
                    "variable": "xhci_boot",
                    "description": [
                        "Enable booting macOS from add-in",
                        "USB 3.0 expansion cards",
                    ],
                },
                "NVMe Booting": {
                    "type": "checkbox",
                    "value": self.constants.nvme_boot,
                    "variable": "nvme_boot",
                    "description": [
                        "Enable booting macOS from NVMe",
                        "drives",
                        "Note: Requires Firmware support",
                        "for OpenCore to load from NVMe",
                    ],
                },
                "Wake on WLAN": {
                    "type": "checkbox",
                    "value": self.constants.enable_wake_on_wlan,
                    "variable": "enable_wake_on_wlan",
                    "description": [
                        "Enable Wake on WLAN",
                        "When enabled, macOS will be able to",
                        "wake from sleep using a Wireless",
                        "Network connection.",
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
                        "Enable Content Caching",
                    ],
                },
                "APFS Trim": {
                    "type": "checkbox",
                    "value": self.constants.apfs_trim_timeout,
                    "variable": "apfs_trim_timeout",
                    "description": [
                        "Recommended for all users, however faulty",
                        "SSDs benefit from disabling this.",
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
                        "Set to 0 for no timeout",
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
                        "Verbose output during boot",
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
            "Security": {
                "Disable Library Validation": {
                    "type": "checkbox",
                    "value": self.constants.disable_cs_lv,
                    "variable": "disable_cs_lv",
                    "description": [
                        "Required for root volume patching,",
                        "allowing our custom frameworks to",
                        "load.",
                    ],
                },
                "Disable AMFI": {
                    "type": "checkbox",
                    "value": self.constants.disable_amfi,
                    "variable": "disable_amfi",
                    "description": [
                        "Extended version of 'Disable",
                        "Library Validation', required for",
                        "patching macOS.",
                    ],
                },
                "Secure Boot Model": {
                    "type": "checkbox",
                    "value": self.constants.secure_status,
                    "variable": "secure_status",
                    "description": [
                        "Enable SecureBootModel",
                    ],
                }
            },
            "Advanced": {
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
                        "Disables firmware based throttling",
                        "caused by missing hardware.",
                        "ex. Missing Display, Battery, etc.",
                    ],
                },
                "Software DeMUX": {
                    "type": "checkbox",
                    "value": self.constants.software_demux,
                    "variable": "software_demux",
                    "description": [
                        "Enable software based DeMUX",
                        "for MacBookPro8,2 and MacBookPro8,3",
                        "Prevents faulty dGPU from turning on",
                    ],
                },
                "wrap_around 1": {
                    "type": "wrap_around",
                },
                "3rd Party NVMe PM": {
                    "type": "checkbox",
                    "value": self.constants.allow_nvme_fixing,
                    "variable": "allow_nvme_fixing",
                    "description": [
                        "Enable 3rd party NVMe power",
                        "management. When enabled, macOS",
                        "will be able to control the power",
                        "management of NVMe drives.",
                    ],
                },
                "3rd Party SATA PM": {
                    "type": "checkbox",
                    "value": self.constants.allow_3rd_party_drives,
                    "variable": "allow_3rd_party_drives",
                    "description": [
                        "Enable 3rd party SATA power",
                        "management. When enabled, macOS",
                        "will be able to control the power",
                        "management of SATA drives.",
                    ],
                },
            },
            "Root Patching": {},
            "Non-Metal": {},
            "App": {
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
                    "value": self.constants.ignore_updates,
                    "variable": "ignore_updates",
                    "description": [
                        "Ignore app updates",
                        "When enabled, the app will not",
                        "check for updates.",
                    ],
                },
                "wrap_around 1": {
                    "type": "wrap_around",
                },
                "Disable Reporting": {
                    "type": "checkbox",
                    "value": global_settings.GlobalEnviromentSettings().read_property("DisableCrashAndAnalyticsReporting"),
                    "variable": "DisableCrashAndAnalyticsReporting",
                    "description": [
                        "Disable crash and system reporting",
                        "When enabled, the app will not",
                        "report any info to Dortania.",
                    ],
                    "override_function": global_settings.GlobalEnviromentSettings().write_property,
                },
                "Disable Unused KDKs": {
                    "type": "checkbox",
                    "value": self.constants.should_nuke_kdks,
                    "variable": "should_nuke_kdks",
                    "description": [
                        "Disable unused KDKs",
                        "When enabled, the app will remove",
                        "unused KDKs from the system.",
                    ],
                },
            },
        }

        return settings


    def on_model_choice(self, event: wx.Event, model_choice: wx.Choice) -> None:

        selection = model_choice.GetStringSelection()
        if selection == "Host Model":
            logging.info(f"Using Real Model: {self.constants.computer.real_model}")
            self.constants.custom_model = None
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

        spacer = 280

        # Title: System Integrity Protection
        sip_title = wx.StaticText(panel, label="System Integrity Protection", pos=(-1, 10 + spacer))
        sip_title.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))

        # Label: Flip individual bits corresponding to XNU's csr.h
        # If you're unfamiliar with how SIP works, do not touch this menu
        sip_label = wx.StaticText(panel, label="Flip individual bits corresponding to", pos=(-1, sip_title.GetSize()[1] + 20 + spacer))
        sip_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))

        # Hyperlink: csr.h
        sip_csr_h = wx.adv.HyperlinkCtrl(panel, id=wx.ID_ANY, label="XNU's csr.h", url="https://opensource.apple.com/source/xnu/xnu-6153.141.1/bsd/sys/csr.h.auto.html", pos=(-1, sip_title.GetSize()[1] + 40 + spacer))
        sip_csr_h.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))

        # Label: If you're unfamiliar with how SIP works, do not touch this menu
        sip_description = wx.StaticText(panel, label="If you're unfamiliar with how SIP works, do not touch this menu", pos=(-1, sip_title.GetSize()[1] + 60 + spacer))
        sip_description.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))

        # Label: SIP Status
        sip_status = wx.StaticText(panel, label="SIP Status", pos=(-1, sip_title.GetSize()[1] + 100 + spacer))
        sip_status.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))

        # Label: SIP Status Description
        sip_status_description = wx.StaticText(panel, label="Displays the current status of SIP", pos=(-1, sip_title.GetSize()[1] + 120 + spacer))

#         self.configure_sip_title = wx.StaticText(self.frame_modal, label="Configure SIP", pos=wx.Point(10, 10))
#         self.configure_sip_title.SetFont(wx.Font(19, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
#         self.configure_sip_title.Center(wx.HORIZONTAL)

#         # Label: Flip individual bits corresponding to XNU's csr.h
#         # If you're unfamiliar with how SIP works, do not touch this menu
#         self.sip_label = wx.StaticText(self.frame_modal, label="Flip individual bits corresponding to")
#         self.sip_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
#         self.sip_label.SetPosition(
#             wx.Point(-1, self.configure_sip_title.GetPosition().y + self.configure_sip_title.GetSize().height + 10)
#         )
#         self.sip_label.Center(wx.HORIZONTAL)
#         self.sip_label.SetPosition(
#             wx.Point(self.sip_label.GetPosition().x - 25, -1)
#         )

#         hyperlink_label = hyperlink.HyperLinkCtrl(
#             self.frame_modal,
#             -1,
#             "XNU's csr.h",
#             pos=(self.sip_label.GetPosition().x + self.sip_label.GetSize().width, self.sip_label.GetPosition().y),
#             URL="https://github.com/apple/darwin-xnu/blob/main/bsd/sys/csr.h",
#         )
#         hyperlink_label.SetForegroundColour(self.hyperlink_colour)
#         hyperlink_label.SetColours(
#             link=self.hyperlink_colour,
#             visited=self.hyperlink_colour,
#             rollover=self.hyperlink_colour,
#         )

#         if self.constants.custom_sip_value is not None:
#             self.sip_value = int(self.constants.custom_sip_value, 16)
#         elif self.constants.sip_status is True:
#             self.sip_value = 0x00
#         else:
#             self.sip_value = 0x803

#         self.sip_label_2 = wx.StaticText(self.frame_modal, label=f"Currently configured SIP: {hex(self.sip_value)}")
#         self.sip_label_2.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
#         self.sip_label_2.SetPosition(
#             wx.Point(self.sip_label.GetPosition().x, self.sip_label.GetPosition().y + self.sip_label.GetSize().height + 10)
#         )
#         self.sip_label_2.Center(wx.HORIZONTAL)

#         self.sip_label_2_2 = wx.StaticText(self.frame_modal, label=f"Currently Booted SIP: {hex(py_sip_xnu.SipXnu().get_sip_status().value)}")
#         self.sip_label_2_2.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
#         self.sip_label_2_2.SetPosition(
#             wx.Point(self.sip_label_2.GetPosition().x, self.sip_label_2.GetPosition().y + self.sip_label_2.GetSize().height + 5)
#         )
#         self.sip_label_2_2.Center(wx.HORIZONTAL)

#         self.sip_label_3 = wx.StaticText(self.frame_modal, label="For older Macs requiring root patching, we set SIP to\n be partially disabled (0x803) to allow root patching.")
#         self.sip_label_3.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
#         self.sip_label_3.SetPosition(
#             wx.Point(self.sip_label_2_2.GetPosition().x, self.sip_label_2_2.GetPosition().y + self.sip_label_2_2.GetSize().height + 10)
#         )
#         self.sip_label_3.Center(wx.HORIZONTAL)

#         self.sip_label_4 = wx.StaticText(self.frame_modal, label="This value (0x803) corresponds to the following bits in csr.h:")
#         self.sip_label_4.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
#         self.sip_label_4.SetPosition(
#             wx.Point(self.sip_label_3.GetPosition().x, self.sip_label_3.GetPosition().y + self.sip_label_3.GetSize().height + 5)
#         )
#         self.sip_label_4.Center(wx.HORIZONTAL)

#         self.sip_label_5 = wx.StaticText(self.frame_modal, label="      0x1  - CSR_ALLOW_UNTRUSTED_KEXTS\n      0x2  - CSR_ALLOW_UNRESTRICTED_FS\n   0x800 - CSR_ALLOW_UNAUTHENTICATED_ROOT")
#         self.sip_label_5.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
#         self.sip_label_5.SetPosition(
#             wx.Point(self.sip_label_4.GetPosition().x, self.sip_label_4.GetPosition().y + self.sip_label_4.GetSize().height + 7)
#         )
#         self.sip_label_5.Center(wx.HORIZONTAL)

#         warning_string = """
# OpenCore Legacy Patcher by default knows the most ideal
#  SIP value for your system. Override this value only if you
#      understand the consequences. Reckless usage of this
#                menu can break your installation.
# """
#         self.sip_label_6 = wx.StaticText(self.frame_modal, label=warning_string)
#         self.sip_label_6.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
#         self.sip_label_6.SetPosition(
#             wx.Point(self.sip_label_5.GetPosition().x, self.sip_label_5.GetPosition().y + self.sip_label_5.GetSize().height - 10)
#         )
#         self.sip_label_6.Center(wx.HORIZONTAL)

#         i = -10
#         for sip_bit in sip_data.system_integrity_protection.csr_values_extended:
#             self.sip_checkbox = wx.CheckBox(self.frame_modal, label=sip_data.system_integrity_protection.csr_values_extended[sip_bit]["name"])
#             self.sip_checkbox.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
#             self.sip_checkbox.SetToolTip(f'Description: {sip_data.system_integrity_protection.csr_values_extended[sip_bit]["description"]}\nValue: {hex(sip_data.system_integrity_protection.csr_values_extended[sip_bit]["value"])}\nIntroduced in: macOS {sip_data.system_integrity_protection.csr_values_extended[sip_bit]["introduced_friendly"]}')
#             self.sip_checkbox.SetPosition(
#                 wx.Point(70, self.sip_label_6.GetPosition().y + self.sip_label_6.GetSize().height + i)
#             )
#             i = i + 20
#             self.sip_checkbox.Bind(wx.EVT_CHECKBOX, self.update_sip_value)
#             if self.sip_value & sip_data.system_integrity_protection.csr_values_extended[sip_bit]["value"] == sip_data.system_integrity_protection.csr_values_extended[sip_bit]["value"]:
#                 self.sip_checkbox.SetValue(True)


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
            self.settings[self._find_parent_for_key(label)][label]["override_function"](self.settings["General"][label]["variable"], value)
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
        logging.info(f"Updating Setting: {variable} = {value}")
        setattr(self.constants, variable, value)


    def _find_parent_for_key(self, key: str) -> str:
        for parent in self.settings:
            if key in self.settings[parent]:
                return parent


    def on_return(self, event):
        self.frame_modal.Destroy()