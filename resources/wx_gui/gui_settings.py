import wx
import logging

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

        self.frame_modal = wx.Dialog(parent, title=title, size=(500, 500))

        self._generate_elements(self.frame_modal)
        self.frame_modal.ShowWindowModal()

    def _generate_elements(self, frame: wx.Frame = None) -> None:

        notebook = wx.Notebook(frame)
        notebook.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))

        tabs = [
            "General",
            "OpenCore",
            "Security",
            "Root Patching",
            "Non-Metal",
        ]
        for tab in tabs:
            panel = wx.Panel(notebook)
            notebook.AddPage(panel, tab)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 1, wx.EXPAND | wx.ALL, 30)
        frame.SetSizer(sizer)
        # Set sizer spacing
        sizer.SetItemMinSize(notebook, (300, 300))

        # Add return button
        return_button = wx.Button(frame, label="Return", pos=(10, frame.GetSize()[1] - 60), size=(100, 30
                                                              ))
        return_button.Bind(wx.EVT_BUTTON, self.on_return)
        return_button.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        return_button.Center(wx.HORIZONTAL)

        for tab in tabs:
            height = 0 if tab != "General" else 80
            width = 0
            panel = notebook.GetPage(tabs.index(tab))

            for setting, setting_info in self.settings[tab].items():
                if setting_info["type"] == "populate":
                    # execute populate function
                    if setting_info["args"] == wx.Frame:
                        setting_info["function"](panel)
                        continue

                if setting_info["type"] == "wrap_around":
                    height = 0 if tab != "General" else 80
                    width += 210
                    continue

                elif setting_info["type"] == "checkbox":
                    # Add checkbox, and description underneath
                    checkbox = wx.CheckBox(panel, label=setting, pos=(10 + width, 10 + height), size = (200,-1))
                    checkbox.SetValue(setting_info["value"] if setting_info["value"] else False)
                    checkbox.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
                    event = lambda event, warning=setting_info["warning"] if "warning" in setting_info else "", override=bool(setting_info["override_function"]) if "override_function" in setting_info else False: self.on_checkbox(event, warning, override)
                    checkbox.Bind(wx.EVT_CHECKBOX, event)

                elif setting_info["type"] == "spinctrl":
                    # Add spinctrl, and description underneath
                    spinctrl = wx.SpinCtrl(panel, value=str(setting_info["value"]), pos=(5 + width, 10 + height), min=setting_info["min"], max=setting_info["max"], size = (45,-1))
                    spinctrl.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
                    spinctrl.Bind(wx.EVT_TEXT, lambda event: self.on_spinctrl(event, setting))
                    # Add label next to spinctrl
                    label = wx.StaticText(panel, label=setting, pos=(spinctrl.GetSize()[0] + 10 + width, spinctrl.GetPosition()[1]))
                    label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
                else:
                    logging.critical(f"Unknown setting type: {setting_info['type']}")
                    continue

                description = wx.StaticText(panel, label=setting_info["description"], pos=(30 + width, 10 + height + 20))
                description.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
                height += 40

                # Check number of lines in description, and adjust spacer accordingly
                description_lines = len(description.GetLabel().split("\n"))
                if description_lines > 1:
                    height += (description_lines) * 10


    def _settings(self):

        settings = {
            "General": {
                "Populate SMBIOS": {
                    "type": "populate",
                    "function": self._populate_model_selection,
                    "args": wx.Frame,
                },
                "Allow native models": {
                    "type": "checkbox",
                    "value": self.constants.allow_oc_everywhere,
                    "variable": "allow_oc_everywhere",
                    "description": "Allow OpenCore to be installed\non natively supported Macs.\nNote this will not allow unsupported\nmacOS versions to be installed on\nyour system.",
                    "warning": "This option should only be used if your Mac natively supports the OSes you wish to run.\n\nIf you are currently running an unsupported OS, this option will break booting. Only toggle for enabling OS features on a native Mac.\n\nAre you certain you want to continue?",
                },
                "Verbose": {
                    "type": "checkbox",
                    "value": self.constants.verbose_debug,
                    "variable": "verbose_debug",
                    "description": "Enable verbose debug logging",
                },
                "Kext Debugging": {
                    "type": "checkbox",
                    "value": self.constants.kext_debug,
                    "variable": "kext_debug",
                    "description": "Enable additional kext logging.",
                },
                "OpenCore Debugging": {
                    "type": "checkbox",
                    "value": self.constants.opencore_debug,
                    "variable": "opencore_debug",
                    "description": "Enable additional OpenCore logging.",
                },
                "Show Boot Picker": {
                    "type": "checkbox",
                    "value": self.constants.showpicker,
                    "variable": "showpicker",
                    "description": "Show OpenCore boot picker\nWhen disabled, users can hold ESC to\nshow picker in the firmware.",
                },
                "wrap_around": {
                    "type": "wrap_around",
                },
                "Boot Picker Timeout": {
                    "type": "spinctrl",
                    "value": self.constants.oc_timeout,
                    "variable": "oc_timeout",
                    "description": "Timeout for OpenCore boot picker\nin seconds.\nSet to 0 for no timeout",
                    "min": 0,
                    "max": 60,
                },
                "Ignore App Updates": {
                    "type": "checkbox",
                    "value": self.constants.ignore_updates,
                    "variable": "ignore_updates",
                    "description": "Ignore app updates\nWhen enabled, the app will not\ncheck for updates.",
                },
                "Disable Reporting": {
                    "type": "checkbox",
                    "value": global_settings.GlobalEnviromentSettings().read_property("DisableCrashAndAnalyticsReporting"),
                    "variable": "DisableCrashAndAnalyticsReporting",
                    "description": "Disable crash and system reporting\nWhen enabled, the app will not\nreport any info to Dortania.",
                    "override_function": global_settings.GlobalEnviromentSettings().write_property,
                },
            },
            "OpenCore": {
                "FireWire Booting": {
                    "type": "checkbox",
                    "value": self.constants.firewire_boot,
                    "variable": "firewire_boot",
                    "description": "Enable booting macOS from\nFireWire drives",
                },
                "XHCI Booting": {
                    "type": "checkbox",
                    "value": self.constants.xhci_boot,
                    "variable": "xhci_boot",
                    "description": "Enable booting macOS from add-in\nUSB 3.0 expansion cards",
                },
                "NVMe Booting": {
                    "type": "checkbox",
                    "value": self.constants.nvme_boot,
                    "variable": "nvme_boot",
                    "description": "Enable booting macOS from NVMe\ndrives",
                },
                "3rd Party NVMe PM": {
                    "type": "checkbox",
                    "value": self.constants.allow_nvme_fixing,
                    "variable": "allow_nvme_fixing",
                    "description": "Enable 3rd party NVMe power\nmanagement. When enabled, macOS\n will be able to control the power\nmanagement of NVMe drives.",
                },
                "Wake on WLAN": {
                    "type": "checkbox",
                    "value": self.constants.enable_wake_on_wlan,
                    "variable": "enable_wake_on_wlan",
                    "description": "Enable Wake on WLAN\nWhen enabled, macOS will be able to\nwake from sleep using a Wireless\nNetwork connection.",
                },
                "wrap_around": {
                    "type": "wrap_around",
                },
                "Content Caching": {
                    "type": "checkbox",
                    "value": self.constants.set_content_caching,
                    "variable": "set_content_caching",
                    "description": "Enable Content Caching\nWhen enabled, macOS will be able\nto use the Content Caching feature.",
                },
                "APFS Trim": {
                    "type": "checkbox",
                    "value": self.constants.apfs_trim_timeout,
                    "variable": "apfs_trim_timeout",
                    "description": "Enable APFS Trim\nRecommended for all users, however faulty\nSSDs benefit from disabling this.",
                },
            },
            "Security": {
                "Disable Library Validation": {
                    "type": "checkbox",
                    "value": self.constants.disable_cs_lv,
                    "variable": "disable_cs_lv",
                    "description": "Required for root volume patching,\nallowing our custom frameworks to\nload.",
                },
                "Disable AMFI": {
                    "type": "checkbox",
                    "value": self.constants.disable_amfi,
                    "variable": "disable_amfi",
                    "description": "Extended version of 'Disable\nLibrary Validation', required for\npatching macOS.",
                },
            },
            "Root Patching": {},
            "Non-Metal": {},
        }

        return settings

    def _populate_model_selection(self, panel: wx.Frame) -> None:
        # Set Override Model to top middle
        model_choice = wx.Choice(panel, choices=model_array.SupportedSMBIOS + ["Host Model"] if self.constants.computer.real_model not in model_array.SupportedSMBIOS else model_array.SupportedSMBIOS, pos=(panel.GetSize()[0] / 2, 10))
        model_choice.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        model_choice.Bind(wx.EVT_CHOICE, lambda event: self.on_model_choice(event, model_choice))
        selection = self.constants.custom_model if self.constants.custom_model else self.constants.computer.real_model
        if selection not in model_array.SupportedSMBIOS:
            selection = "Host Model"
        model_choice.SetSelection(model_choice.FindString(selection))

        # Set position to middle of panel
        center = (panel.GetSize()[0] + 150)
        model_choice.SetPosition((center, 10))

        # Add label below Override Model
        model_label = wx.StaticText(panel, label="Target Model", pos=(model_choice.GetPosition()[0] + 100, model_choice.GetSize()[1] + 20))
        model_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, ".AppleSystemUIFont"))
        model_label.SetPosition((center + 20, model_choice.GetSize()[1] + 20))

        # Description: Overrides system OCLP will build for
        model_description = wx.StaticText(panel, label="Overrides system OCLP will build for.", pos=(model_choice.GetPosition()[0] + 100, model_choice.GetSize()[1] + 40))
        model_description.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, ".AppleSystemUIFont"))
        model_description.SetPosition((model_label.GetPosition()[0] - 60, model_choice.GetSize()[1] + 40))


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

        self.parent.model_label.SetLabel(f"Model: {selection}")
        self.parent.model_label.Center(wx.HORIZONTAL)

        self.frame_modal.Destroy()
        SettingsFrame(
            parent=self.parent,
            title=self.title,
            global_constants=self.constants,
            screen_location=self.parent.GetPosition()
        )


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
            print(f"Overriding function: {self.settings['General'][label]['override_function']}")
            self.settings["General"][label]["override_function"](self.settings["General"][label]["variable"], value)
            return
        self._update_setting(self.settings["General"][label]["variable"], value)


    def on_spinctrl(self, event: wx.Event, label: str) -> None:
        """
        """
        value = event.GetEventObject().GetValue()
        self._update_setting(self.settings["General"][label]["variable"], value)


    def _update_setting(self, variable, value):
        print(f"Updating Setting: {variable} = {value}")
        setattr(self.constants, variable, value)


    def on_return(self, event):
        self.frame_modal.Destroy()