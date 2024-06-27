"""
package_scripts.py: Generate pre/postinstall scripts for PKG and AutoPkg
"""


class ZSHFunctions:

    def __init__(self) -> None:
        pass


    def generate_standard_pkg_parameters(self) -> str:
        """
        ZSH variables for standard PackageKit parameters
        """

        _script = ""

        _script += "# MARK: PackageKit Parameters\n"
        _script += "# " + "-" * 27 + "\n\n"

        _script += "pathToScript=$0          # ex. /tmp/PKInstallSandbox.*/Scripts/*/preinstall\n"
        _script += "pathToPackage=$1         # ex. ~/Downloads/Installer.pkg\n"
        _script += "pathToTargetLocation=$2  # ex. '/', '/Applications', etc (depends on pkgbuild's '--install-location' argument)\n"
        _script += "pathToTargetVolume=$3    # ex. '/', '/Volumes/MyVolume', etc\n"
        _script += "pathToStartupDisk=$4     # ex. '/'\n"

        return _script


    def generate_script_remove_file(self) -> str:
        """
        ZSH function to remove files
        """

        _script = ""

        _script += "function _removeFile() {\n"
        _script += "    local file=$1\n\n"

        _script += "    if [[ ! -e $file ]]; then\n"
        _script += "        # Check if file is a symbolic link\n"
        _script += "        if [[ -L $file ]]; then\n"
        _script += "            echo \"Removing symbolic link: $file\"\n"
        _script += "            /bin/rm -f $file\n"
        _script += "        fi\n"
        _script += "        return\n"
        _script += "    fi\n\n"

        _script += "    echo \"Removing file: $file\"\n\n"

        _script += "    # Check if file is a directory\n"
        _script += "    if [[ -d $file ]]; then\n"
        _script += "        /bin/rm -rf $file\n"
        _script += "    else\n"
        _script += "        /bin/rm -f $file\n"
        _script += "    fi\n"
        _script += "}\n"

        return _script


    def generate_script_create_parent_directory(self) -> str:
        """
        ZSH function to create parent directory
        """

        _script = ""

        _script += "function _createParentDirectory() {\n"
        _script += "    local file=$1\n\n"

        _script += "    local parentDirectory=\"$(/usr/bin/dirname $file)\"\n\n"

        _script += "    # Check if parent directory exists\n"
        _script += "    if [[ ! -d $parentDirectory ]]; then\n"
        _script += "        echo \"Creating parent directory: $parentDirectory\"\n"
        _script += "        /bin/mkdir -p $parentDirectory\n"
        _script += "    fi\n"
        _script += "}\n"

        return _script


    def generate_set_suid_bit(self) -> str:
        """
        ZSH function to set SUID bit
        """

        _script = ""

        _script += "function _setSUIDBit() {\n"
        _script += "    local binaryPath=$1\n\n"

        _script += "    echo \"Setting SUID bit on: $binaryPath\"\n\n"

        _script += "    # Check if path is a directory\n"
        _script += "    if [[ -d $binaryPath ]]; then\n"
        _script += "        /bin/chmod -R +s $binaryPath\n"
        _script += "    else\n"
        _script += "        /bin/chmod +s $binaryPath\n"
        _script += "    fi\n"
        _script += "}\n"

        return _script


    def generate_create_alias(self) -> str:
        """
        ZSH function to create alias
        """

        _script = ""

        _script += "function _createAlias() {\n"
        _script += "    local mainPath=$1\n"
        _script += "    local aliasPath=$2\n\n"

        _script += "    # Check if alias path exists\n"
        _script += "    if [[ -e $aliasPath ]]; then\n"
        _script += "        # Check if alias path is a symbolic link\n"
        _script += "        if [[ -L $aliasPath ]]; then\n"
        _script += "            echo \"Removing old symbolic link: $aliasPath\"\n"
        _script += "            /bin/rm -f $aliasPath\n"
        _script += "        else\n"
        _script += "            echo \"Removing old file: $aliasPath\"\n"
        _script += "            /bin/rm -rf $aliasPath\n"
        _script += "        fi\n"
        _script += "    fi\n\n"

        _script += "    # Create symbolic link\n"
        _script += "    echo \"Creating symbolic link: $aliasPath\"\n"
        _script += "    /bin/ln -s $mainPath $aliasPath\n"
        _script += "}\n"

        return _script


    def generate_start_patching(self) -> str:
        """
        ZSH function to start patching
        """

        _script = ""

        _script += "function _startPatching() {\n"
        _script += "    local executable=$1\n"
        _script += "    local logPath=$(_logFile)\n\n"

        _script += "    # Start patching\n"
        _script += "    \"$executable\" \"--patch_sys_vol\" &> $logPath\n"
        _script += "}\n"

        return _script


    def generate_log_file(self) -> str:
        """
        ZSH function to generate log file
        """

        _script = ""

        _script += "function _logFile() {\n"
        _script += "    echo \"/Users/Shared/.OCLP-AutoPatcher-Log-$(/bin/date +\"%Y_%m_%d_%I_%M_%p\").txt\"\n"
        _script += "}\n"

        return _script


    def generate_fix_settings_file_permission(self) -> str:
        """
        ZSH function to fix settings file permission
        """

        _script = ""

        _script += "function _fixSettingsFilePermission() {\n"
        _script += "    local settingsPath=\"$pathToTargetVolume/Users/Shared/.com.dortania.opencore-legacy-patcher.plist\"\n\n"

        _script += "    if [[ -e $settingsPath ]]; then\n"
        _script += "        echo \"Fixing settings file permissions: $settingsPath\"\n"
        _script += "        /bin/chmod 666 $settingsPath\n"
        _script += "    fi\n"

        _script += "}\n"

        return _script


    def generate_reboot(self) -> str:
        """
        ZSH function to reboot
        """

        _script = ""

        _script += "function _reboot() {\n"
        _script += "    /sbin/reboot\n"
        _script += "}\n"

        return _script


    def generate_prewarm_gatekeeper(self) -> str:
        """
        ZSH function to prewarm Gatekeeper
        """

        _script = ""

        _script += "function _prewarmGatekeeper() {\n"
        _script += "    local appPath=$1\n\n"

        _script += "    # Check if /usr/bin/gktool exists\n"
        _script += "    if [[ ! -e /usr/bin/gktool ]]; then\n"
        _script += "        echo \"Host doesn't support Gatekeeper prewarming, skipping...\"\n"
        _script += "        return\n"
        _script += "    fi\n\n"

        _script += "    echo \"Prewarming Gatekeeper for application: $appPath\"\n"
        _script += "    /usr/bin/gktool scan $appPath\n"
        _script += "}\n"

        return _script


    def generate_clean_launch_service(self) -> str:
        """
        ZSH function to clean Launch Service
        """

        _script = ""

        _script += "function _cleanLaunchService() {\n"
        _script += "    local domain=\"com.dortania.opencore-legacy-patcher\"\n\n"

        _script += "    # Iterate over launch agents and daemons\n"
        _script += "    for launchServiceVariant in \"$pathToTargetVolume/Library/LaunchAgents\" \"$pathToTargetVolume/Library/LaunchDaemons\"; do\n"
        _script += "        # Check if directory exists\n"
        _script += "        if [[ ! -d $launchServiceVariant ]]; then\n"
        _script += "            continue\n"
        _script += "        fi\n\n"

        _script += "        # Iterate over launch service files\n"
        _script += "        for launchServiceFile in $(/bin/ls -1 $launchServiceVariant | /usr/bin/grep $domain); do\n"
        _script += "            local launchServicePath=\"$launchServiceVariant/$launchServiceFile\"\n\n"

        _script += "            # Remove launch service file\n"
        _script += "            _removeFile $launchServicePath\n"
        _script += "        done\n"
        _script += "    done\n"
        _script += "}\n"

        return _script


    def generate_preinstall_main(self) -> str:
        """
        ZSH function for preinstall's main
        """

        _script = ""

        _script += "function _main() {\n"
        _script += "    for file in $filesToRemove; do\n"
        _script += "        _removeFile $pathToTargetVolume/$file\n"
        _script += "        _createParentDirectory $pathToTargetVolume/$file\n"
        _script += "    done\n"
        _script += "}\n"

        return _script


    def generate_postinstall_main(self, is_autopkg: bool = False) -> str:
        """
        ZSH function for postinstall's main
        """

        _script = ""

        _script += "function _main() {\n"
        _script += "    _setSUIDBit \"$pathToTargetVolume/$helperPath\"\n"
        _script += "    _createAlias \"$pathToTargetVolume/$mainAppPath\" \"$pathToTargetVolume/$shimAppPath\"\n"
        _script += "    _prewarmGatekeeper \"$pathToTargetVolume/$mainAppPath\"\n"
        if is_autopkg:
            _script += "    _startPatching \"$pathToTargetVolume/$executablePath\"\n"
            _script += "    _fixSettingsFilePermission\n"
            _script += "    _reboot\n"
        _script += "}\n"

        return _script


    def generate_uninstall_main(self) -> str:
        """
        ZSH function for uninstall's main
        """

        _script = ""

        _script += "function _main() {\n"
        _script += "    _cleanLaunchService\n"
        _script += "    for file in $filesToRemove; do\n"
        _script += "        _removeFile $pathToTargetVolume/$file\n"
        _script += "    done\n"
        _script += "}\n"

        return _script


class GenerateScripts:

    def __init__(self):
        self.zsh_functions = ZSHFunctions()

        self.files = [
            "Applications/OpenCore-Patcher.app",
            "Library/Application Support/Dortania/Update.plist",
            "Library/Application Support/Dortania/OpenCore-Patcher.app",
            "Library/PrivilegedHelperTools/com.dortania.opencore-legacy-patcher.privileged-helper"
        ]

        self.additional_auto_pkg_files = [
            "Library/LaunchAgents/com.dortania.opencore-legacy-patcher.auto-patch.plist"
        ]


    def __generate_shebang(self) -> str:
        """
        Standard shebang for ZSH
        """
        return "#!/bin/zsh --no-rcs\n"


    def _generate_header_bar(self) -> str:
        """
        # ------------------------------------------------------
        """
        return "# " + "-" * 54 + "\n"


    def _generate_label_bar(self) -> str:
        """
        # ------------------------------
        """
        return "# " + "-" * 27 + "\n"


    def _generate_preinstall_script(self, is_autopkg: bool = False) -> str:
        """
        Generate preinstall script for PKG
        """

        _script = ""

        _script += self.__generate_shebang()

        _script += self._generate_header_bar()
        _script += f"# {'AutoPkg Assets' if is_autopkg else 'OpenCore Legacy Patcher'} Preinstall Script\n"
        _script += self._generate_header_bar()
        _script += "# Remove old files, and prepare directories.\n"
        _script += self._generate_header_bar()
        _script += "\n\n"

        _script += self.zsh_functions.generate_standard_pkg_parameters()
        _script += "\n\n"

        _script += "# MARK: Variables\n"
        _script += self._generate_label_bar()
        _script += "\n"

        _files = self.files
        if is_autopkg:
            _files += self.additional_auto_pkg_files

        _script += f"filesToRemove=(\n"
        for _file in _files:
            _script += f"    \"{_file}\"\n"

        _script += ")\n"

        _script += "\n\n"

        _script += "# MARK: Functions\n"
        _script += self._generate_label_bar()
        _script += "\n"

        _script += self.zsh_functions.generate_script_remove_file()
        _script += "\n"
        _script += self.zsh_functions.generate_script_create_parent_directory()
        _script += "\n"
        _script += self.zsh_functions.generate_preinstall_main()
        _script += "\n\n"

        _script += "# MARK: Main\n"
        _script += self._generate_label_bar()
        _script += "\n"

        _script += "echo \"Starting preinstall script...\"\n"
        _script += "_main\n"

        return _script


    def _generate_postinstall_script(self, is_autopkg: bool = False) -> str:
        """
        """

        _script = ""

        _script += self.__generate_shebang()

        _script += self._generate_header_bar()
        _script += f"# {'AutoPkg Assets' if is_autopkg else 'OpenCore Legacy Patcher'} Post Install Script\n"
        _script += self._generate_header_bar()
        if is_autopkg:
            _script += "# Set UID, create alias, start patching, and reboot.\n"
        else:
            _script += "# Set SUID bit on helper tool, and create app alias.\n"
        _script += self._generate_header_bar()
        _script += "\n\n"

        _script += self.zsh_functions.generate_standard_pkg_parameters()
        _script += "\n\n"

        _script += "# MARK: Variables\n"
        _script += self._generate_label_bar()
        _script += "\n"

        _script += "helperPath=\"Library/PrivilegedHelperTools/com.dortania.opencore-legacy-patcher.privileged-helper\"\n"
        _script += "mainAppPath=\"Library/Application Support/Dortania/OpenCore-Patcher.app\"\n"
        _script += "shimAppPath=\"Applications/OpenCore-Patcher.app\"\n"
        if is_autopkg:
            _script += "executablePath=\"$mainAppPath/Contents/MacOS/OpenCore-Patcher\"\n"

        _script += "\n\n"

        _script += "# MARK: Functions\n"
        _script += self._generate_label_bar()
        _script += "\n"

        _script += self.zsh_functions.generate_set_suid_bit()
        _script += "\n"
        _script += self.zsh_functions.generate_create_alias()
        _script += "\n"
        _script += self.zsh_functions.generate_prewarm_gatekeeper()
        _script += "\n"
        if is_autopkg:
            _script += self.zsh_functions.generate_start_patching()
            _script += "\n"
            _script += self.zsh_functions.generate_log_file()
            _script += "\n"
            _script += self.zsh_functions.generate_fix_settings_file_permission()
            _script += "\n"
            _script += self.zsh_functions.generate_reboot()
            _script += "\n"

        _script += self.zsh_functions.generate_postinstall_main(is_autopkg)
        _script += "\n\n"

        _script += "# MARK: Main\n"
        _script += self._generate_label_bar()
        _script += "\n"

        _script += "echo \"Starting postinstall script...\"\n"
        _script += "_main\n"

        return _script


    def _generate_uninstall_script(self) -> str:
        """
        """
        _script = ""

        _script += self.__generate_shebang()

        _script += self._generate_header_bar()
        _script += f"# OpenCore Legacy Patcher Uninstall Script\n"
        _script += self._generate_header_bar()
        _script += "# Remove OpenCore Legacy Patcher files and directories.\n"
        _script += self._generate_header_bar()
        _script += "\n\n"

        _script += self.zsh_functions.generate_standard_pkg_parameters()
        _script += "\n\n"

        _script += "# MARK: Variables\n"
        _script += self._generate_label_bar()
        _script += "\n"

        _files = self.files

        _script += "filesToRemove=(\n"
        for _file in _files:
            _script += f"    \"{_file}\"\n"

        _script += ")\n"

        _script += "\n\n"

        _script += "# MARK: Functions\n"
        _script += self._generate_label_bar()
        _script += "\n"

        _script += self.zsh_functions.generate_script_remove_file()
        _script += "\n"
        _script += self.zsh_functions.generate_clean_launch_service()
        _script += "\n"
        _script += self.zsh_functions.generate_uninstall_main()
        _script += "\n\n"

        _script += "# MARK: Main\n"
        _script += self._generate_label_bar()
        _script += "\n"

        _script += "echo \"Starting uninstall script...\"\n"
        _script += "_main\n"

        return _script


    def preinstall_pkg(self) -> str:
        """
        Generate preinstall script for PKG
        """
        return self._generate_preinstall_script()


    def preinstall_autopkg(self) -> str:
        """
        Generate preinstall script for AutoPkg
        """
        return self._generate_preinstall_script(is_autopkg=True)


    def postinstall_pkg(self) -> str:
        """
        Generate postinstall script for PKG
        """
        return self._generate_postinstall_script()


    def postinstall_autopkg(self) -> str:
        """
        Generate postinstall script for AutoPkg
        """
        return self._generate_postinstall_script(is_autopkg=True)


    def uninstall(self) -> str:
        """
        Generate uninstall script
        """
        return self._generate_uninstall_script()