from data import smbios_data, os_data, cpu_data
from resources import utilities


def set_smbios_model_spoof(model):
    try:
        smbios_data.smbios_dictionary[model]["Screen Size"]
        # Found mobile SMBIOS
        if model.startswith("MacBookAir"):
            return "MacBookAir8,1"
        elif model.startswith("MacBookPro"):
            if smbios_data.smbios_dictionary[model]["Screen Size"] == 13:
                return "MacBookPro14,1"
            elif smbios_data.smbios_dictionary[model]["Screen Size"] >= 15:
                # 15" and 17"
                return "MacBookPro14,3"
            else:
                # Unknown Model
                raise Exception(f"Unknown SMBIOS for spoofing: {model}")
        elif model.startswith("MacBook"):
            if smbios_data.smbios_dictionary[model]["Screen Size"] == 13:
                return "MacBookAir8,1"
            elif smbios_data.smbios_dictionary[model]["Screen Size"] == 12:
                return "MacBook10,1"
            else:
                # Unknown Model
                raise Exception(f"Unknown SMBIOS for spoofing: {model}")
        else:
            # Unknown Model
            raise Exception(f"Unknown SMBIOS for spoofing: {model}")
    except KeyError:
        # Found desktop model
        if model.startswith("MacPro") or model.startswith("Xserve"):
            return "MacPro7,1"
        elif model.startswith("Macmini"):
            return "Macmini8,1"
        elif model.startswith("iMac"):
            if smbios_data.smbios_dictionary[model]["Max OS Supported"] <= os_data.os_data.high_sierra:
                # Models dropped in Mojave either do not have an iGPU, or should have them disabled
                return "iMacPro1,1"
            else:
                return "iMac18,3"
        else:
            # Unknown Model
            raise Exception(f"Unknown SMBIOS for spoofing: {model}")


def update_firmware_features(firmwarefeature):
    # Adjust FirmwareFeature to support everything macOS requires
    # APFS Bit (19/20): 10.13+ (OSInstall)
    # Large BaseSystem Bit (35): 12.0 B7+ (patchd)
    # https://github.com/acidanthera/OpenCorePkg/tree/2f76673546ac3e32d2e2d528095fddcd66ad6a23/Include/Apple/IndustryStandard/AppleFeatures.h
    firmwarefeature |= 2 ** 19  # FW_FEATURE_SUPPORTS_APFS
    firmwarefeature |= 2 ** 20  # FW_FEATURE_SUPPORTS_APFS_EXTRA
    firmwarefeature |= 2 ** 35  # FW_FEATURE_SUPPORTS_LARGE_BASESYSTEM
    return firmwarefeature


def generate_fw_features(model, custom):
    if not custom:
        firmwarefeature = utilities.get_rom("firmware-features")
        if not firmwarefeature:
            print("- Failed to find FirmwareFeatures, falling back on defaults")
            if smbios_data.smbios_dictionary[model]["FirmwareFeatures"] is None:
                firmwarefeature = 0
            else:
                firmwarefeature = int(smbios_data.smbios_dictionary[model]["FirmwareFeatures"], 16)
    else:
        if smbios_data.smbios_dictionary[model]["FirmwareFeatures"] is None:
            firmwarefeature = 0
        else:
            firmwarefeature = int(smbios_data.smbios_dictionary[model]["FirmwareFeatures"], 16)
    firmwarefeature = update_firmware_features(firmwarefeature)
    return firmwarefeature


def find_model_off_board(board):
    # Find model based off Board ID provided
    # Return none if unknown

    # Strip extra data from Target Types (ap, uppercase)
    if not (board.startswith("Mac-") or board.startswith("VMM-")):
        if board.lower().endswith("ap"):
            board = board[:-2]
        board = board.lower()

    for key in smbios_data.smbios_dictionary:
        if board in [smbios_data.smbios_dictionary[key]["Board ID"], smbios_data.smbios_dictionary[key]["SecureBootModel"]]:
            if key.endswith("_v2") or key.endswith("_v3") or key.endswith("_v4"):
                # smbios_data has duplicate SMBIOS to handle multiple board IDs
                key = key[:-3]
            if key == "MacPro4,1":
                # 4,1 and 5,1 have the same board ID, best to return the newer ID
                key = "MacPro5,1"
            return key
    return None

def find_board_off_model(model):
    if model in smbios_data.smbios_dictionary:
        return smbios_data.smbios_dictionary[model]["Board ID"]
    else:
        return None


def check_firewire(model):
    # MacBooks never supported FireWire
    # Pre-Thunderbolt MacBook Airs as well
    if model.startswith("MacBookPro"):
        return True
    elif model.startswith("MacBookAir"):
        if smbios_data.smbios_dictionary[model]["CPU Generation"] < cpu_data.cpu_data.sandy_bridge.value:
            return False
    elif model.startswith("MacBook"):
        return False
    else:
        return True

def determine_best_board_id_for_sandy(current_board_id, gpus):
    # This function is mainly for users who are either spoofing or using hackintoshes
    # Generally hackintosh will use whatever the latest SMBIOS is, so we need to determine
    # the best Board ID to patch inside of AppleIntelSNBGraphicsFB

    # Currently the kext supports the following models:
    #   MacBookPro8,1 - Mac-94245B3640C91C81 (13")
    #   MacBookPro8,2 - Mac-94245A3940C91C80 (15")
    #   MacBookPro8,3 - Mac-942459F5819B171B (17")
    #   MacBookAir4,1 - Mac-C08A6BB70A942AC2 (11")
    #   MacBookAir4,2 - Mac-742912EFDBEE19B3 (13")
    #   Macmini5,1    - Mac-8ED6AF5B48C039E1
    #   Macmini5,2    - Mac-4BC72D62AD45599E (headless)
    #   Macmini5,3    - Mac-7BA5B2794B2CDB12
    #   iMac12,1      - Mac-942B5BF58194151B (headless)
    #   iMac12,2      - Mac-942B59F58194171B (headless)
    #   Unknown(MBP)  - Mac-94245AF5819B141B
    #   Unknown(iMac) - Mac-942B5B3A40C91381 (headless)
    if current_board_id:
        model = find_model_off_board(current_board_id)
        if model:
            if model.startswith("MacBook"):
                try:
                    size = int(smbios_data.smbios_dictionary[model]["Screen Size"])
                except KeyError:
                    size = 13 # Assume 13 if it's missing
                if model.startswith("MacBookPro"):
                    if size >= 17:
                        return find_board_off_model("MacBookPro8,3")
                    elif size >= 15:
                        return find_board_off_model("MacBookPro8,2")
                    else:
                        return find_board_off_model("MacBookPro8,1")
                else: # MacBook and MacBookAir
                    if size >= 13:
                        return find_board_off_model("MacBookAir4,2")
                    else:
                        return find_board_off_model("MacBookAir4,1")
            else:
                # We're working with a desktop, so need to figure out whether the unit is running headless or not
                if len(gpus) > 1:
                    # More than 1 GPU detected, assume headless
                    if model.startswith("Macmini"):
                        return find_board_off_model("Macmini5,2")
                    else:
                        return find_board_off_model("iMac12,2")
                else:
                    return find_board_off_model("Macmini5,1")
    return find_board_off_model("Macmini5,1") # Safest bet if we somehow don't know the model