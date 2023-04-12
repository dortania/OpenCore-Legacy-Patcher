# Privacy Policy

OpenCore Legacy Patcher may collect pseudo-anonymized data about the host system and the OpenCore Legacy Patcher application. This data is used to improve the project and to help diagnose issues. The data collected is as follows:

* System's UUID as a SHA1 hash
  * This is used to identify the system and to prevent duplicate reports
  * Cannot be used to identify the system without the user providing the UUID
* Application name and version
* System's OS version
* System's model name, GPUs present and firmware vendor
  * May include more hardware information in the future (ex. CPU, WiFi, etc)
* General country code of system's reported region
  * ex. `US`, `CA`, etc

Identifiable data such as IP addresses, MAC addresses, serial numbers, etc. are not collected.

In the future, crash logs may also be collected to help with diagnosing issues.
----------

Users who wish to opt-out can do so either via the application's preferences or via the following command:
```
defaults write com.dortania.opencore-legacy-patcher DisableCrashAndAnalyticsReporting -bool true
```

To have your data removed, please contact us via our [Discord server](https://discord.gg/rqdPgH8xSN) and provide the UUID of your system.